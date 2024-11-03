from itertools import chain, combinations
import re, time

class ProcesadorGramatica:
    def __init__(self):
        self.TERMINALS = set()
        self.NON_TERMINALS = set()
        self.pattern = re.compile(r'[A-Z]+\s*→\s*([A-Za-z0-9ε\s\|\(\)\+\*]+)')

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
            
            # Manejar las producciones separadas por |
            productions = [p.strip() for p in productions.split('|')]
            
            if non_terminal in grammar:
                grammar[non_terminal].extend(productions)
            else:
                grammar[non_terminal] = productions

            # Identificar terminales
            for prod in productions:
                symbols = prod.split()
                for symbol in symbols:
                    if not symbol.isupper() and symbol != 'ε':
                        self.TERMINALS.add(symbol)
        
        return grammar

    def encontrar_anulables(self, grammar):
        """Encuentra todos los símbolos anulables."""
        nullable = set()
        changed = True
        
        while changed:
            changed = False
            for nt, productions in grammar.items():
                if nt not in nullable:
                    for prod in productions:
                        symbols = prod.split()
                        if prod == 'ε' or (symbols and all(sym in nullable for sym in symbols)):
                            nullable.add(nt)
                            changed = True
        return nullable

    def eliminar_epsilon(self, grammar):
        """Elimina las producciones epsilon manteniendo las equivalencias."""
        nullable = self.encontrar_anulables(grammar)
        new_grammar = {}

        for nt, productions in grammar.items():
            new_productions = set()
            for prod in productions:
                if prod == 'ε':
                    continue
                
                symbols = prod.split()
                nullable_positions = [i for i, sym in enumerate(symbols) if sym in nullable]
                
                # Generar todas las combinaciones posibles de eliminación
                for r in range(len(nullable_positions) + 1):
                    for combo in combinations(nullable_positions, r):
                        new_prod = ' '.join(sym for i, sym in enumerate(symbols) if i not in combo)
                        if new_prod:  # No agregar producciones vacías
                            new_productions.add(new_prod)
                        elif nt in nullable:  # Si el no terminal es anulable, mantener ε
                            new_productions.add('ε')
                            
            new_grammar[nt] = list(new_productions) if new_productions else productions

        return new_grammar

    def eliminar_produccion_unitaria(self, grammar):
        """Elimina las producciones unitarias preservando la equivalencia."""
        # Encontrar todos los pares unitarios
        unit_pairs = {(nt, nt) for nt in grammar}
        changed = True
        
        while changed:
            changed = False
            for nt, productions in grammar.items():
                for prod in productions:
                    if len(prod.split()) == 1 and prod in self.NON_TERMINALS:
                        for pair in list(unit_pairs):
                            if pair[0] == prod and (nt, pair[1]) not in unit_pairs:
                                unit_pairs.add((nt, pair[1]))
                                changed = True

        # Construir nueva gramática
        new_grammar = {nt: [] for nt in grammar}
        for nt, productions in grammar.items():
            for prod in productions:
                symbols = prod.split()
                if len(symbols) != 1 or symbols[0] not in self.NON_TERMINALS:
                    for head, body in unit_pairs:
                        if body == nt:
                            new_grammar[head].append(prod)

        return new_grammar

    def eliminar_no_generados(self, grammar, start_symbol='S'):
        """Elimina símbolos no generadores y no alcanzables."""
        # Encontrar símbolos generadores
        generating = set()
        changed = True
        
        while changed:
            changed = False
            for nt, productions in grammar.items():
                if nt not in generating:
                    for prod in productions:
                        symbols = prod.split()
                        if all(s in self.TERMINALS or s in generating for s in symbols):
                            generating.add(nt)
                            changed = True

        # Eliminar no generadores
        new_grammar = {nt: [p for p in prods if all(s in self.TERMINALS or s in generating 
                          for s in p.split())]
                      for nt, prods in grammar.items() if nt in generating}

        # Encontrar símbolos alcanzables
        reachable = {start_symbol}
        changed = True
        while changed:
            changed = False
            new_reachable = set()
            for nt in reachable:
                if nt in new_grammar:
                    for prod in new_grammar[nt]:
                        symbols = prod.split()
                        for symbol in symbols:
                            if symbol in self.NON_TERMINALS and symbol not in reachable:
                                new_reachable.add(symbol)
                                changed = True
            reachable.update(new_reachable)

        # Eliminar no alcanzables
        return {nt: prods for nt, prods in new_grammar.items() if nt in reachable}

    def convertir_CNF(self, grammar):
        """Convierte la gramática a Forma Normal de Chomsky."""
        new_grammar = {}
        temp_rules = {}
        counter = 1

        def new_symbol():
            nonlocal counter
            while f'X{counter}' in self.NON_TERMINALS:
                counter += 1
            symbol = f'X{counter}'
            counter += 1
            return symbol

        # Paso 1: Manejar terminales en producciones largas
        for nt, productions in grammar.items():
            new_productions = []
            for prod in productions:
                symbols = prod.split()
                if len(symbols) > 1:
                    new_symbols = []
                    for symbol in symbols:
                        if symbol in self.TERMINALS:
                            if symbol not in temp_rules:
                                new_nt = new_symbol()
                                temp_rules[symbol] = new_nt
                                new_grammar[new_nt] = [symbol]
                                self.NON_TERMINALS.add(new_nt)
                            new_symbols.append(temp_rules[symbol])
                        else:
                            new_symbols.append(symbol)
                    new_productions.append(' '.join(new_symbols))
                else:
                    new_productions.append(prod)
            new_grammar[nt] = new_productions

        # Paso 2: Dividir producciones largas
        final_grammar = {}
        for nt, productions in new_grammar.items():
            final_productions = []
            for prod in productions:
                symbols = prod.split()
                while len(symbols) > 2:
                    new_nt = new_symbol()
                    self.NON_TERMINALS.add(new_nt)
                    final_grammar[new_nt] = [' '.join(symbols[:2])]
                    symbols = [new_nt] + symbols[2:]
                final_productions.append(' '.join(symbols))
            final_grammar[nt] = final_productions

        return final_grammar

    def algoritmo_CYK(self, grammar, input_string):
        """Implementa el algoritmo CYK con seguimiento de derivaciones."""
        words = input_string.split()
        n = len(words)
        
        if n == 0:
            return False, []

        # Inicializar tabla CYK
        table = [[set() for _ in range(n - i)] for i in range(n)]
        
        # Llenar la diagonal (casos base)
        for i, word in enumerate(words):
            for nt, productions in grammar.items():
                if word in productions:
                    table[0][i].add(nt)
        
        # Llenar el resto de la tabla
        for l in range(1, n):  # longitud del span
            for i in range(n - l):  # posición inicial
                for k in range(l):  # punto de división
                    for nt, productions in grammar.items():
                        for prod in productions:
                            if ' ' in prod:  # solo producciones binarias
                                B, C = prod.split()
                                if B in table[k][i] and C in table[l-k-1][i+k+1]:
                                    table[l][i].add(nt)
        
        print("\nTabla CYK:")
        for i, row in enumerate(table):
            print(f"Nivel {i}:", row)
        
        return 'S' in table[n-1][0], table

def procesar_gramatica_completa(grammar_text):
    processor = ProcesadorGramatica()
    
    # Procesar la gramática
    original_grammar = processor.leer_gramatica(grammar_text)
    print("Gramática original:", original_grammar)
    
    # Aplicar transformaciones
    grammar = processor.eliminar_epsilon(original_grammar)
    print("\nDespués de eliminar ε:", grammar)
    
    grammar = processor.eliminar_produccion_unitaria(grammar)
    print("\nDespués de eliminar producciones unitarias:", grammar)
    
    grammar = processor.eliminar_no_generados(grammar)
    print("\nDespués de eliminar símbolos inútiles:", grammar)
    
    grammar = processor.convertir_CNF(grammar)
    print("\nEn Forma Normal de Chomsky:", grammar)
    
    while True:
        print("\nIngrese una cadena para verificar (o 'salir' para terminar):")
        input_string = input().strip()
        
        if input_string.lower() == 'salir':
            break
            
        start_time = time.time()
        result, table = processor.algoritmo_CYK(grammar, input_string)
        end_time = time.time()
        
        print(f"\nLa cadena '{input_string}' {'SÍ' if result else 'NO'} pertenece a la gramática")
        print(f"Tiempo de ejecución: {end_time - start_time:.4f} segundos")

if __name__ == "__main__":
    # Ejemplo de uso
    grammar_text = """
    S → NP VP
    VP → VP PP | V NP | cooks | drinks | eats | cuts
    PP → P NP
    NP → Det N | he | she
    V → cooks | drinks | eats | cuts
    P → in | with
    N → cat | dog | beer | cake | juice | meat | soup | fork | knife | oven | spoon
    Det → a | the
    """
    
    print("=== Procesador de Gramática y Verificador CYK ===")
    procesar_gramatica_completa(grammar_text)