import re
import itertools
import sys

def lectura_gramatica(filename):
    grammar = {}
    non_terminals = set()
    terminals = set()
    production_regex = re.compile(r'^[A-Z]\s*→\s*((([A-Za-z0-9]+)|ε)(\s*\|\s*(([A-Za-z0-9]+)|ε))*)$')

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except IOError:
        print(f"Error al abrir el archivo {filename}")
        sys.exit(1)

    for line_num, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue  # Ignorar líneas vacías

        # Validar la línea con la expresión regular
        if not production_regex.match(line):
            print(f"Error de sintaxis en la línea {line_num}: '{line}'")
            sys.exit(1)

        # Separar LHS y RHS
        lhs, rhs = map(str.strip, line.split('→'))

        # Agregar el no-terminal al conjunto de no-terminales
        non_terminals.add(lhs)

        # Separar las producciones por '|'
        productions = {prod.strip() for prod in rhs.split('|')}

        # Agregar las producciones al diccionario de gramática
        grammar[lhs] = productions
        for prod in productions:
            for symbol in prod:
                if symbol.isupper():
                    non_terminals.add(symbol)
                elif symbol.islower() or symbol.isdigit():
                    terminals.add(symbol)
                elif symbol != 'ε':
                    print(f"Símbolo inválido '{symbol}' en la línea {line_num}")
                    sys.exit(1)

    return grammar, non_terminals, terminals

def find_nullable_non_terminals(grammar):
    nullable = {lhs for lhs, prods in grammar.items() if 'ε' in prods}
    changed = True
    while changed:
        changed = False
        for lhs, prods in grammar.items():
            if lhs not in nullable and any(all(symbol in nullable for symbol in prod if symbol.isupper()) for prod in prods):
                nullable.add(lhs)
                changed = True
    print("\nSímbolos anulables:", nullable)
    return nullable

def remove_epsilon_productions(grammar, nullable):
    new_grammar = {}
    for lhs, prods in grammar.items():
        new_productions = set()
        for prod in prods:
            if prod == 'ε':
                continue
            positions = [i for i, symbol in enumerate(prod) if symbol in nullable]
            for subset in itertools.chain.from_iterable(itertools.combinations(positions, r) for r in range(1, len(positions) + 1)):
                new_prod = ''.join([symbol for i, symbol in enumerate(prod) if i not in subset])
                new_productions.add(new_prod if new_prod else 'ε')
            new_productions.add(prod)
        new_grammar[lhs] = new_productions

    start_symbol = next(iter(grammar))
    if start_symbol in nullable:
        new_grammar[start_symbol].add('ε')

    return new_grammar

def mostrar_gramatica(grammar, title):
    print(f"\n{title}")
    for lhs, prods in grammar.items():
        productions = ' | '.join(sorted(prods, key=lambda x: (x != 'ε', x)))
        print(f"{lhs} → {productions}")

