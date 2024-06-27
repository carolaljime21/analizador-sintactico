class NodoSintactico:
    def __init__(self, contenido, subnodos=None):
        self.contenido = contenido
        self.subnodos = subnodos if subnodos else []

    def añadir_subnodo(self, subnodo):
        self.subnodos.append(subnodo)


class ParserLR:
    def __init__(self):
        self.producciones = [
            ('E', 'E+T'),  # R1
            ('E', 'T'),    # R2
            ('T', 'T*F'),  # R3
            ('T', 'F'),    # R4
            ('F', '(E)'),  # R5
            ('F', 'id')    # R6
        ]
        
        self.tabla_acciones = {
            (0, 'id'): ('D', 5), (0, '('): ('D', 4), (0, 'E'): (1, None), (0, 'T'): (2, None), (0, 'F'): (3, None),
            (1, '+'): ('D', 6), (1, '$'): ('accept', None),
            (2, '+'): ('R', 2), (2, '*'): ('D', 7), (2, ')'): ('R', 2), (2, '$'): ('R', 2),
            (3, '+'): ('R', 4), (3, '*'): ('R', 4), (3, ')'): ('R', 4), (3, '$'): ('R', 4),
            (4, 'id'): ('D', 5), (4, '('): ('D', 4), (4, 'E'): (8, None), (4, 'T'): (3, None), (4, 'F'): (2, None),
            (5, '+'): ('R', 6), (5, '*'): ('R', 6), (5, ')'): ('R', 6), (5, '$'): ('R', 6),
            (6, 'id'): ('D', 5), (6, '('): ('D', 4), (6, 'T'): (9, None), (6, 'F'): (3, None),
            (7, 'id'): ('D', 5), (7, '('): ('D', 4), (7, 'F'): (10, None),
            (8, '+'): ('D', 6), (8, ')'): ('D', 11),
            (9, '+'): ('R', 1), (9, '*'): ('D', 7), (9, ')'): ('R', 1), (9, '$'): ('R', 1),
            (10, '+'): ('R', 3), (10, '*'): ('R', 3), (10, ')'): ('R', 3), (10, '$'): ('R', 3),
            (11, '+'): ('R', 5), (11, '*'): ('R', 5), (11, ')'): ('R', 5), (11, '$'): ('R', 5),
        }
        
        self.tabla_goto = {
            (0, 'E'): 1, (0, 'T'): 2, (0, 'F'): 3,
            (4, 'E'): 8, (4, 'T'): 2, (4, 'F'): 3,
            (6, 'T'): 9, (6, 'F'): 3,
            (7, 'F'): 10
        }

    def tokenizar_cadena(self, cadena):
        tokens = []
        i = 0
        while i < len(cadena):
            if cadena[i:i+2] == 'id':
                tokens.append('id')
                i += 2
            elif cadena[i] in ['+', '*', '(', ')']:
                tokens.append(cadena[i])
                i += 1
            elif cadena[i].isspace():
                i += 1
            else:
                raise ValueError(f"Carácter no reconocido: {cadena[i]}")
        return tokens

    def analizar(self, cadena):
        pila = [0]
        nodos_pila = []
        tokens = self.tokenizar_cadena(cadena) + ['$']
        puntero = 0
        
        print(f"{'Pila':<30} {'ae':<5} {'S':<5} {'a':<5} {'Accion[S,A]':<20} {'S^':<5} {'A':<5} {'B':<10} {'ir a S^A':<10}")
        print("-" * 100)
        
        while True:
            estado = pila[-1]
            token_actual = tokens[puntero]
            
            if (estado, token_actual) not in self.tabla_acciones:
                print(f"Error: No se encontró acción para el estado {estado} y el token '{token_actual}'")
                return False, None
            
            accion, valor = self.tabla_acciones[(estado, token_actual)]
            
            print(f"{str(pila):<30} {token_actual:<5} {estado:<5} {token_actual:<5}", end=" ")
            
            if accion == 'D':
                print(f"D{valor:<19} {valor:<5}")
                pila.append(token_actual)
                pila.append(valor)
                nodos_pila.append(NodoSintactico(token_actual))
                puntero += 1
            elif accion == 'R':
                regla = self.producciones[valor - 1]
                print(f"R{valor:<19}", end=" ")
                
                simbolos_produccion = regla[1]
                elementos_quitar = 2 * len(simbolos_produccion.replace('id', 'x'))
                
                if len(pila) >= elementos_quitar:
                    hijos = []
                    for _ in range(len(simbolos_produccion.replace('id', 'x'))):
                        hijos.insert(0, nodos_pila.pop())
                    
                    nuevo_nodo = NodoSintactico(regla[0], hijos)
                    nodos_pila.append(nuevo_nodo)
                    
                    for _ in range(elementos_quitar):
                        pila.pop()
                    
                    estado_previo = pila[-1]
                    pila.append(regla[0])
                    
                    if (estado_previo, regla[0]) in self.tabla_goto:
                        ir_a_SA = self.tabla_goto[(estado_previo, regla[0])]
                        pila.append(ir_a_SA)
                        print(f"{estado_previo:<5} {regla[0]:<5} {regla[1]:<10} {ir_a_SA:<10}")
                    else:
                        print(f"\nError: No se encontró estado GOTO para ({estado_previo}, {regla[0]})")
                        return False, None
                else:
                    print(f"\nError: No hay suficientes elementos en la pila para realizar la reducción")
                    return False, None
            elif accion == 'accept':
                print("Aceptar")
                return True, nodos_pila[0]
            
            print()

# Función para imprimir el árbol
def imprimir_arbol(nodo, prefijo='', es_ultimo=True):
    print(prefijo + ('└── ' if es_ultimo else '├── ') + nodo.contenido)
    prefijo += '    ' if es_ultimo else '│   '
    for i, hijo in enumerate(nodo.subnodos):
        es_ultimo_hijo = (i == len(nodo.subnodos) - 1)
        imprimir_arbol(hijo, prefijo, es_ultimo_hijo)


parser = ParserLR()
cadena = "id * id + id"
print(cadena)
result, arbol = parser.analizar(cadena)

if result:
    print("\nCadena: ACEPTADA.")
    print("\nÁrbol de derivación:")
    imprimir_arbol(arbol)
else:
    print("\nCadena: RECHAZADA.")
