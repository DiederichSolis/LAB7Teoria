import re
import itertools
import sys

def read_grammar(filename):
    grammar = {}
    non_terminals = set()
    terminals = set()
    production_regex = r'^[A-Z]\s*→\s*((([A-Za-z0-9]+)|ε)(\s*\|\s*(([A-Za-z0-9]+)|ε))*)$'

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
        if not re.match(production_regex, line):
            print(f"Error de sintaxis en la línea {line_num}: '{line}'")
            sys.exit(1)

        # Separar LHS y RHS
        lhs, rhs = line.split('→')
        lhs = lhs.strip()
        rhs = rhs.strip()

        # Agregar el no-terminal al conjunto de no-terminales
        non_terminals.add(lhs)

        # Separar las producciones por '|'
        productions = [prod.strip() for prod in rhs.split('|')]

        # Agregar las producciones al diccionario de gramática
        if lhs not in grammar:
            grammar[lhs] = set()
        for prod in productions:
            grammar[lhs].add(prod)
            for symbol in prod:
                if symbol.isupper():
                    non_terminals.add(symbol)
                elif symbol.islower() or symbol.isdigit():
                    terminals.add(symbol)
                elif symbol == 'ε':
                    pass  # ε no se agrega a terminales ni no-terminales
                else:
                    print(f"Símbolo inválido '{symbol}' en la línea {line_num}")
                    sys.exit(1)

    return grammar, non_terminals, terminals
