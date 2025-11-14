"""
Validadores para gramáticas y autómatas
"""

from typing import Dict, List, Set, Tuple, Optional
import re


def validate_grammar_format(text: str) -> Tuple[bool, Optional[str]]:
    """
    Valida que el formato de la gramática sea correcto.
    
    Args:
        text: Texto de la gramática
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not text or not text.strip():
        return False, "La gramática está vacía"
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        return False, "No se encontraron producciones"
    
    # Verificar que cada línea tenga un símbolo de producción
    for i, line in enumerate(lines, 1):
        if not re.search(r'→|->|::=', line):
            return False, f"Línea {i} no contiene un símbolo de producción válido (→, ->, ::=)"
    
    return True, None


def validate_production(left: str, bodies: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Valida una producción individual.
    
    Args:
        left: Lado izquierdo (símbolo no terminal)
        bodies: Lista de cuerpos de producción
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not left:
        return False, "El lado izquierdo de la producción está vacío"
    
    if not bodies:
        return False, "El lado derecho de la producción está vacío"
    
    # Verificar que el lado izquierdo sea un símbolo válido
    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', left):
        return False, f"El símbolo no terminal '{left}' debe empezar con mayúscula"
    
    return True, None


def validate_automaton_definition(definition: Dict) -> Tuple[bool, Optional[str]]:
    """
    Valida la definición de un autómata.
    
    Args:
        definition: Diccionario con la definición del autómata
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    required_keys = ['states', 'alphabet', 'transitions', 'initial_state', 'final_states']
    
    for key in required_keys:
        if key not in definition:
            return False, f"Falta la clave requerida: {key}"
    
    # Validar estados
    if not definition['states']:
        return False, "El conjunto de estados no puede estar vacío"
    
    # Validar alfabeto
    if not definition['alphabet']:
        return False, "El alfabeto no puede estar vacío"
    
    # Validar estado inicial
    if definition['initial_state'] not in definition['states']:
        return False, "El estado inicial debe estar en el conjunto de estados"
    
    # Validar estados finales
    for state in definition['final_states']:
        if state not in definition['states']:
            return False, f"El estado final '{state}' no está en el conjunto de estados"
    
    # Validar transiciones
    for transition in definition['transitions']:
        if len(transition) < 3:
            return False, "Cada transición debe tener al menos (estado_origen, símbolo, estado_destino)"
        
        state_from = transition[0]
        if state_from not in definition['states']:
            return False, f"Estado origen '{state_from}' no está en el conjunto de estados"
    
    return True, None


def check_grammar_consistency(productions: Dict[str, List[str]]) -> Tuple[bool, List[str]]:
    """
    Verifica la consistencia de una gramática.
    
    Args:
        productions: Diccionario de producciones
        
    Returns:
        Tupla (es_consistente, lista_de_advertencias)
    """
    warnings = []
    
    # Verificar que todos los símbolos no terminales usados tengan producción
    used_nts = set()
    for bodies in productions.values():
        for body in bodies:
            # Buscar símbolos no terminales en los cuerpos
            nts = re.findall(r'[A-Z][a-zA-Z0-9]*', body)
            used_nts.update(nts)
    
    # Verificar símbolos no terminales sin producción
    undefined = used_nts - set(productions.keys())
    if undefined:
        warnings.append(f"Símbolos no terminales usados pero sin producción: {', '.join(sorted(undefined))}")
    
    # Verificar símbolos no terminales definidos pero nunca usados
    defined = set(productions.keys())
    unused = defined - used_nts - {list(productions.keys())[0]}  # Excluir símbolo inicial
    if unused:
        warnings.append(f"Símbolos no terminales definidos pero nunca usados: {', '.join(sorted(unused))}")
    
    return len(warnings) == 0, warnings

