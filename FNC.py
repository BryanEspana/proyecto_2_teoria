from itertools import chain, combinations
import re, time



class proceso_gramatica:
    def __init__(self):
        self.TERMINALS = set()
        self.NON_TERMINALS = set()
        self.pattern = re.compile(r'[A-Z]+\s*→\s*([A-Za-z0-9ε]+\s*\|?\s*)+')

    def leer_gramatica(self, file_content):
        """Lee la gramática desde un string y la convierte a diccionario."""
        grammar = {}
        for line in file_content.split('\n'):
            line = line.strip()
            if not line or not self.pattern.match(line):
                continue

            non_terminal, productions = line.split('→')
            non_terminal = non_terminal.strip()
            self.NON_TERMINALS.add(non_terminal)
            productions = [p.strip() for p in productions.split('|')]
            
            for prod in productions:
                symbols = prod.split()
                for symbol in symbols:
                    if not symbol.isupper() and symbol != 'ε':
                        self.TERMINALS.add(symbol)
            
            grammar[non_terminal] = productions
        
        return grammar
    
    def encontrar_anulables(self, grammar):
        """Encuentra todos los símbolos anulables directa e indirectamente."""
        nullable = set()
        changed = True
        
        while changed:
            changed = False
            for nt, productions in grammar.items():
                if nt not in nullable:
                    for prod in productions:
                        if prod == 'ε' or all(symbol in nullable for symbol in prod.split()):
                            nullable.add(nt)
                            changed = True
        return nullable
    
    def eliminar_epsilon(self, grammar):
        """Elimina las producciones epsilon y genera todas las combinaciones posibles."""
        nullable = self.encontrar_anulables(grammar)
        new_grammar = {}

        for nt, productions in grammar.items():
            new_productions = set()
            for prod in productions:
                if prod == 'ε':
                    continue
                    
                symbols = prod.split()
                nullable_positions = [i for i, sym in enumerate(symbols) if sym in nullable]
                
                for r in range(len(nullable_positions) + 1):
                    for combo in combinations(nullable_positions, r):
                        new_prod = ' '.join(sym for i, sym in enumerate(symbols) if i not in combo)
                        if new_prod:
                            new_productions.add(new_prod)
                            
            new_grammar[nt] = list(new_productions) if new_productions else productions

        return new_grammar

    def eliminar_produccion_unitaria(self, grammar):
        """Elimina las producciones unitarias."""
        def obtener_producciones(grammar):
            unit_prods = set()
            for nt, productions in grammar.items():
                for prod in productions:
                    if len(prod.split()) == 1 and prod in self.NON_TERMINALS:
                        unit_prods.add((nt, prod))
            return unit_prods

        new_grammar = {nt: set(prods) for nt, prods in grammar.items()}
        unit_productions = obtener_producciones(grammar)
        
        while unit_productions:
            A, B = unit_productions.pop()
            if B in new_grammar:
                new_prods = new_grammar[B] - {A}  # Evitar ciclos
                new_grammar[A].update(new_prods)
                new_grammar[A] = {prod for prod in new_grammar[A] 
                                if not (len(prod.split()) == 1 and prod in self.NON_TERMINALS)}

        return {nt: list(prods) for nt, prods in new_grammar.items()}

    def eliminar_no_generados(self, grammar, start_symbol):
        """Elimina símbolos no generadores y no alcanzables."""
        # Encuentra símbolos generadores
        generating = set()
        changed = True
        while changed:
            changed = False
            for nt, productions in grammar.items():
                if nt not in generating:
                    for prod in productions:
                        symbols = prod.split()
                        if all(s not in self.NON_TERMINALS or s in generating 
                              for s in symbols):
                            generating.add(nt)
                            changed = True

        # Elimina no generadores
        new_grammar = {nt: [p for p in prods if all(s not in self.NON_TERMINALS or s in generating 
                          for s in p.split())]
                      for nt, prods in grammar.items() if nt in generating}

        # Encuentra símbolos alcanzables
        reachable = {start_symbol}
        changed = True
        while changed:
            changed = False
            for nt in list(reachable):
                if nt in new_grammar:
                    for prod in new_grammar[nt]:
                        for symbol in prod.split():
                            if symbol in self.NON_TERMINALS and symbol not in reachable:
                                reachable.add(symbol)
                                changed = True

        # Elimina no alcanzables
        return {nt: prods for nt, prods in new_grammar.items() if nt in reachable}

    def convertirCNF(self, grammar):
        """Convierte la gramática a Forma Normal de Chomsky."""
        new_grammar = {}
        terminal_rules = {}
        var_counter = 1

        def nueva_variable():
            nonlocal var_counter
            var = f'X{var_counter}'
            var_counter += 1
            return var

        # Paso 1: Manejar terminales
        for nt, productions in grammar.items():
            new_productions = set()
            for prod in productions:
                symbols = prod.split()
                new_symbols = []
                
                for symbol in symbols:
                    if not symbol.isupper() and len(symbols) > 1:
                        if symbol not in terminal_rules:
                            new_nt = nueva_variable()
                            terminal_rules[symbol] = new_nt
                            new_grammar[new_nt] = [symbol]
                        new_symbols.append(terminal_rules[symbol])
                    else:
                        new_symbols.append(symbol)
                        
                new_productions.add(' '.join(new_symbols))
            new_grammar[nt] = list(new_productions)

        # Paso 2: Manejar producciones largas
        final_grammar = {}
        for nt, productions in new_grammar.items():
            final_productions = set()
            for prod in productions:
                symbols = prod.split()
                while len(symbols) > 2:
                    new_nt = nueva_variable()
                    final_grammar[new_nt] = [' '.join(symbols[:2])]
                    symbols = [new_nt] + symbols[2:]
                final_productions.add(' '.join(symbols))
            final_grammar[nt] = list(final_productions)

        return final_grammar

    def algoritmoCYK(self, grammar, input_string):
        """Implementa el algoritmo CYK."""
        words = input_string.split()
        n = len(words)
        
        # Inicializar tabla CYK
        table = [[set() for _ in range(n)] for _ in range(n)]
        
        # Llenar la diagonal (casos base)
        for i, word in enumerate(words):
            for nt, productions in grammar.items():
                if word in productions:
                    table[i][i].add(nt)
        
        # Llenar el resto de la tabla
        for l in range(2, n + 1):  # longitud del span
            for i in range(n - l + 1):  # posición inicial
                j = i + l - 1  # posición final
                for k in range(i, j):  # punto de división
                    for nt, productions in grammar.items():
                        for prod in productions:
                            if ' ' in prod:  # solo considerar producciones binarias
                                B, C = prod.split()
                                if B in table[i][k] and C in table[k+1][j]:
                                    table[i][j].add(nt)
        
        return 'S' in table[0][n-1]

def procesar_gramatica_completa(grammar_text):
    processor = proceso_gramatica()
    
    # Leer y procesar la gramática
    grammar = processor.leer_gramatica(grammar_text)
    print("Gramática original:", grammar)
    
    # Aplicar transformaciones
    grammar = processor.eliminar_epsilon(grammar)
    print("\nDespués de eliminar ε:", grammar)
    
    grammar = processor.eliminar_produccion_unitaria(grammar)
    print("\nDespués de eliminar producciones unitarias:", grammar)
    
    grammar = processor.eliminar_no_generados(grammar, 'S')
    print("\nDespués de eliminar símbolos inútiles:", grammar)
    
    grammar = processor.convertirCNF(grammar)
    print("\nEn Forma Normal de Chomsky:", grammar)
    
    while True:
        # Solicitar entrada al usuario
        print("\nIngrese una cadena para verificar (o 'salir' para terminar):")
        input_string = input().strip()
        
        if input_string.lower() == 'salir':
            break
            
        # Verificar la cadena
        result = processor.algoritmoCYK(grammar, input_string)
        print(f"\nLa cadena '{input_string}' {'pertenece' if result else 'NO pertenece'} a la gramática")

# Ejemplo de uso con la gramática dada
grammar_text = """
S → 0A0 | 1B1 | BB
A → C | ε
B → S | A
C → S | ε
"""


print("=== Procesador de Gramática y Verificador CYK ===")
procesar_gramatica_completa(grammar_text)