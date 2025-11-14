"""
Funciones auxiliares para el proyecto Chomsky Classifier AI
"""

import re
from typing import List, Set, Tuple, Dict, Optional


def clean_grammar_text(text: str) -> str:
    """
    Limpia y normaliza el texto de una gramática.
    
    Args:
        text: Texto crudo de la gramática
        
    Returns:
        Texto limpio y normalizado
    """
    # Eliminar comentarios (líneas que empiezan con #)
    lines = [line.split('#')[0].strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    
    # Unir líneas continuas
    cleaned = '\n'.join(lines)
    
    # Normalizar espacios
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()


def parse_production(production: str) -> Tuple[str, List[str]]:
    """
    Parsea una producción individual en formato 'A → α | β | γ'
    
    Args:
        production: String con la producción
        
    Returns:
        Tupla (símbolo_no_terminal, lista_de_cuerpos)
        
    Example:
        >>> parse_production('S → aSb | ab')
        ('S', ['aSb', 'ab'])
    """
    # Buscar el símbolo de producción (→, ->, ::=)
    production = production.strip()
    
    # Normalizar diferentes símbolos de producción
    production = re.sub(r'->|::=', '→', production)
    
    if '→' not in production:
        raise ValueError(f"Producción inválida: no se encontró símbolo de producción (→, ->, ::=) en '{production}'")
    
    left, right = production.split('→', 1)
    left = left.strip()
    right = right.strip()
    
    if not left:
        raise ValueError(f"Producción inválida: lado izquierdo vacío en '{production}'")
    
    # Separar las alternativas (separadas por |)
    bodies = [body.strip() for body in right.split('|')]
    bodies = [body for body in bodies if body]  # Eliminar vacíos
    
    if not bodies:
        raise ValueError(f"Producción inválida: lado derecho vacío en '{production}'")
    
    return left, bodies


def extract_symbols(productions: Dict[str, List[str]]) -> Tuple[Set[str], Set[str]]:
    """
    Extrae los símbolos terminales y no terminales de un conjunto de producciones.
    
    Args:
        productions: Diccionario {símbolo_no_terminal: [cuerpos]}
        
    Returns:
        Tupla (terminales, no_terminales)
    """
    non_terminals = set(productions.keys())
    terminals = set()
    
    # Encontrar todos los posibles no terminales usando regex
    # Patrón: letra mayúscula seguida de letras/números opcionales
    nt_pattern = r'[A-Z][a-zA-Z0-9]*'
    all_found_nts = set(non_terminals)  # Empezar con los definidos
    
    # Buscar en todos los cuerpos
    for bodies in productions.values():
        for body in bodies:
            if body in ['ε', 'λ', '']:
                continue
            # Encontrar todos los matches de no terminales
            matches = re.findall(nt_pattern, body)
            all_found_nts.update(matches)
    
    # Ahora, para cada cuerpo, identificar qué símbolos son realmente no terminales
    # vs terminales. Un símbolo es no terminal si:
    # 1. Está definido en productions, O
    # 2. Es un patrón [A-Z][a-zA-Z0-9]* que aparece en algún cuerpo
    
    # Identificar terminales: caracteres que no son no terminales
    for bodies in productions.values():
        for body in bodies:
            if body in ['ε', 'λ', '']:
                continue
            
            # Procesar el cuerpo carácter por carácter, identificando no terminales
            i = 0
            while i < len(body):
                # Intentar hacer match con un no terminal
                matched = False
                # Probar con todos los no terminales encontrados, del más largo al más corto
                sorted_nts = sorted(all_found_nts, key=len, reverse=True)
                for nt in sorted_nts:
                    if body[i:].startswith(nt):
                        # Verificar que no sea parte de un no terminal más largo
                        # (el siguiente carácter debe ser terminal o límite)
                        next_pos = i + len(nt)
                        if (next_pos >= len(body) or 
                            body[next_pos].islower() or 
                            not body[next_pos].isalnum() or
                            body[next_pos] in ['(', ')', '+', '*', '|', '→', ' ']):
                            # Es un no terminal válido
                            i = next_pos
                            matched = True
                            break
                
                if not matched:
                    # Es un terminal (carácter individual)
                    char = body[i]
                    if char not in [' ', '|', '→', '(', ')', '+', '*', '-'] and char not in ['ε', 'λ']:
                        terminals.add(char)
                    i += 1
    
    return terminals, all_found_nts


def is_epsilon_production(body: str) -> bool:
    """
    Verifica si un cuerpo de producción es epsilon (vacío).
    
    Args:
        body: Cuerpo de producción
        
    Returns:
        True si es epsilon, False en caso contrario
    """
    body = body.strip()
    return body in ['ε', 'λ', '']


def normalize_symbol(symbol: str) -> str:
    """
    Normaliza un símbolo de gramática.
    
    Args:
        symbol: Símbolo a normalizar
        
    Returns:
        Símbolo normalizado
    """
    symbol = symbol.strip()
    # Reemplazar epsilon
    if symbol in ['ε', 'λ']:
        return 'ε'
    return symbol


def format_grammar(productions: Dict[str, List[str]], start_symbol: str = 'S') -> str:
    """
    Formatea un diccionario de producciones en texto legible.
    
    Args:
        productions: Diccionario de producciones
        start_symbol: Símbolo inicial
        
    Returns:
        String formateado
    """
    lines = []
    if start_symbol in productions:
        lines.append(f"{start_symbol} → {' | '.join(productions[start_symbol])}")
    
    for nt, bodies in sorted(productions.items()):
        if nt != start_symbol:
            lines.append(f"{nt} → {' | '.join(bodies)}")
    
    return '\n'.join(lines)


def find_start_symbol(productions: Dict[str, List[str]]) -> Optional[str]:
    """
    Encuentra el símbolo inicial de la gramática (primera producción o 'S').
    
    Args:
        productions: Diccionario de producciones
        
    Returns:
        Símbolo inicial o None
    """
    if 'S' in productions:
        return 'S'
    
    if productions:
        return list(productions.keys())[0]
    
    return None

