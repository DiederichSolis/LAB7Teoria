import re
import itertools
import sys

# Función para leer la gramática desde un archivo
def lectura_gramatica(filename):
    """
    Lee una gramática de un archivo y la valida, asegurando que cumpla con las reglas definidas.

    Args:
        filename (str): El nombre del archivo que contiene la gramática.

    Returns:
        tuple: Contiene el diccionario de la gramática, el conjunto de no-terminales y el conjunto de terminales.
    """
    grammar = {}  # Diccionario para almacenar las producciones de la gramática
    non_terminals = set()  # Conjunto de símbolos no-terminales
    terminals = set()  # Conjunto de símbolos terminales
    # Expresión regular para validar las producciones (formato: A → B | C)
    production_regex = re.compile(r'^[A-Z]\s*→\s*((([A-Za-z0-9]+)|ε)(\s*\|\s*(([A-Za-z0-9]+)|ε))*)$')

    try:
        # Intentar abrir el archivo en modo lectura
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()  # Leer todas las líneas del archivo
    except IOError:
        # Manejo de error si no se puede abrir el archivo
        print(f"Error al abrir el archivo {filename}")
        sys.exit(1)

    # Procesar cada línea del archivo
    for line_num, line in enumerate(lines, start=1):
        line = line.strip()  # Eliminar espacios en blanco
        if not line:
            continue  # Ignorar líneas vacías

        # Validar la línea con la expresión regular
        if not production_regex.match(line):
            print(f"Error de sintaxis en la línea {line_num}: '{line}'")
            sys.exit(1)

        # Separar el lado izquierdo (LHS) y el lado derecho (RHS) de la producción
        lhs, rhs = map(str.strip, line.split('→'))

        # Agregar el símbolo no-terminal (LHS) al conjunto
        non_terminals.add(lhs)

        # Separar las producciones del RHS por el símbolo '|'
        productions = {prod.strip() for prod in rhs.split('|')}

        # Agregar las producciones al diccionario de gramática
        grammar[lhs] = productions

        # Procesar cada producción para identificar terminales y no-terminales
        for prod in productions:
            for symbol in prod:
                if symbol.isupper():
                    non_terminals.add(symbol)  # Agregar símbolos no-terminales
                elif symbol.islower() or symbol.isdigit():
                    terminals.add(symbol)  # Agregar símbolos terminales
                elif symbol != 'ε':  # Verificar símbolos inválidos
                    print(f"Símbolo inválido '{symbol}' en la línea {line_num}")
                    sys.exit(1)

    return grammar, non_terminals, terminals

# Función para encontrar los símbolos anulables
def find_nullable_non_terminals(grammar):
    """
    Encuentra los símbolos no-terminales que son anulables (que pueden derivar a ε).

    Args:
        grammar (dict): El diccionario de la gramática.

    Returns:
        set: Conjunto de símbolos no-terminales que son anulables.
    """
    # Inicialmente, los no-terminales que derivan directamente a ε
    nullable = {lhs for lhs, prods in grammar.items() if 'ε' in prods}
    changed = True

    # Algoritmo para encontrar todos los símbolos anulables
    while changed:
        changed = False
        for lhs, prods in grammar.items():
            if lhs not in nullable and any(all(symbol in nullable for symbol in prod if symbol.isupper()) for prod in prods):
                nullable.add(lhs)
                changed = True

    print("\nSímbolos anulables:", nullable)
    return nullable

# Función para eliminar las producciones-ε
def remove_epsilon_productions(grammar, nullable):
    """
    Elimina las producciones-ε de la gramática, excepto cuando sea necesario.

    Args:
        grammar (dict): El diccionario de la gramática original.
        nullable (set): Conjunto de no-terminales anulables.

    Returns:
        dict: Nueva gramática sin producciones-ε.
    """
    new_grammar = {}  # Nueva gramática sin ε-producciones

    # Iterar sobre las producciones originales
    for lhs, prods in grammar.items():
        new_productions = set()
        for prod in prods:
            if prod == 'ε':
                continue  # Ignorar las producciones que derivan a ε directamente

            # Encontrar todas las combinaciones posibles de símbolos anulables
            positions = [i for i, symbol in enumerate(prod) if symbol in nullable]
            for subset in itertools.chain.from_iterable(itertools.combinations(positions, r) for r in range(1, len(positions) + 1)):
                # Crear una nueva producción sin los símbolos anulables
                new_prod = ''.join([symbol for i, symbol in enumerate(prod) if i not in subset])
                new_productions.add(new_prod if new_prod else 'ε')

            new_productions.add(prod)

        new_grammar[lhs] = new_productions

    # Asegurar que el símbolo inicial aún pueda derivar a ε si es anulable
    start_symbol = next(iter(grammar))
    if start_symbol in nullable:
        new_grammar[start_symbol].add('ε')

    return new_grammar

# Función para mostrar la gramática
def mostrar_gramatica(grammar, title):
    """
    Imprime la gramática de una forma legible.

    Args:
        grammar (dict): El diccionario de la gramática.
        title (str): Título de la gramática que se va a mostrar.
    """
    print(f"\n{title}")
    for lhs, prods in grammar.items():
        productions = ' | '.join(sorted(prods, key=lambda x: (x != 'ε', x)))  # Ordenar las producciones
        print(f"{lhs} → {productions}")

# Función principal del programa
def main():
    """
    Función principal que coordina la lectura de la gramática, identificación de símbolos anulables,
    eliminación de producciones-ε y la visualización de la gramática resultante.
    """
    filename = input("Ingrese el nombre del archivo de gramática: ")
    
    # Leer la gramática desde el archivo proporcionado
    grammar, non_terminals, terminals = lectura_gramatica(filename)

    # Mostrar la gramática original
    mostrar_gramatica(grammar, "Gramática original:")

    # Encontrar los símbolos anulables
    nullable = find_nullable_non_terminals(grammar)

    # Eliminar producciones-ε
    new_grammar = remove_epsilon_productions(grammar, nullable)

    # Mostrar la gramática sin producciones-ε
    mostrar_gramatica(new_grammar, "Gramática sin producciones-ε:")

# Ejecutar la función principal si se ejecuta el script directamente
if __name__ == "__main__":
    main()
