"""
Módulo conversor entre diferentes representaciones formales.

Permite convertir entre:
- Expresiones Regulares (Regex)
- Autómatas Finitos No Deterministas (AFN)
- Autómatas Finitos Deterministas (AFD)
- Gramáticas Regulares (Tipo 3)

Incluye explicaciones del proceso de conversión.
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from grammar_parser import GrammarParser
from automata_analyzer import AutomatonAnalyzer, AutomatonType


class RegexToAFNConverter:
    """
    Convierte expresiones regulares a Autómatas Finitos No Deterministas.
    
    Implementa el algoritmo de Thompson para la construcción de AFN.
    """
    
    def __init__(self, regex: str):
        """
        Inicializa el conversor con una expresión regular.
        
        Args:
            regex: Expresión regular a convertir
        """
        self.regex = regex
        self.state_counter = 0
        self.explanation: List[str] = []
    
    def convert(self) -> Dict:
        """
        Convierte la expresión regular a un AFN.
        
        Returns:
            Diccionario con la definición del AFN
        """
        self.explanation = []
        self.explanation.append(f"Convirtiendo expresión regular: {self.regex}")
        
        # Simplificar y parsear la expresión regular
        simplified = self._simplify_regex(self.regex)
        self.explanation.append(f"Expresión simplificada: {simplified}")
        
        # Construir AFN usando algoritmo de Thompson
        afn = self._thompson_construction(simplified)
        
        self.explanation.append("AFN construido exitosamente")
        return afn
    
    def _simplify_regex(self, regex: str) -> str:
        """
        Simplifica una expresión regular.
        
        Args:
            regex: Expresión regular
            
        Returns:
            Expresión regular simplificada
        """
        # Eliminar espacios
        regex = regex.replace(' ', '')
        return regex
    
    def _thompson_construction(self, regex: str) -> Dict:
        """
        Construye un AFN usando el algoritmo de Thompson.
        
        Args:
            regex: Expresión regular
            
        Returns:
            Diccionario con la definición del AFN
        """
        # Implementación simplificada del algoritmo de Thompson
        # Para una implementación completa, se necesitaría un parser de regex
        
        states = set()
        transitions = []
        initial_state = self._new_state()
        final_state = self._new_state()
        
        states.add(initial_state)
        states.add(final_state)
        
        # Construcción básica para caracteres simples
        # (Implementación simplificada - se puede extender)
        alphabet = set()
        
        for char in regex:
            if char.isalnum():
                alphabet.add(char)
                # Crear transición para el carácter
                intermediate = self._new_state()
                states.add(intermediate)
                transitions.append((initial_state, char, intermediate))
                transitions.append((intermediate, 'ε', final_state))
        
        return {
            'states': states,
            'alphabet': alphabet,
            'transitions': transitions,
            'initial_state': initial_state,
            'final_states': {final_state}
        }
    
    def _new_state(self) -> str:
        """
        Genera un nuevo nombre de estado.
        
        Returns:
            Nombre del nuevo estado
        """
        state = f"q{self.state_counter}"
        self.state_counter += 1
        return state
    
    def get_explanation(self) -> List[str]:
        """
        Obtiene la explicación del proceso de conversión.
        
        Returns:
            Lista de strings con la explicación
        """
        return self.explanation.copy()


class AFNToAFDConverter:
    """
    Convierte Autómatas Finitos No Deterministas a Deterministas.
    
    Implementa el algoritmo de construcción de subconjuntos.
    """
    
    def __init__(self, afn_definition: Dict):
        """
        Inicializa el conversor con una definición de AFN.
        
        Args:
            afn_definition: Diccionario con la definición del AFN
        """
        self.afn = afn_definition
        self.explanation: List[str] = []
    
    def convert(self) -> Dict:
        """
        Convierte el AFN a un AFD usando construcción de subconjuntos.
        
        Returns:
            Diccionario con la definición del AFD
        """
        self.explanation = []
        self.explanation.append("Iniciando conversión de AFN a AFD (construcción de subconjuntos)")
        
        # Obtener información del AFN
        afn_states = self.afn['states']
        afn_alphabet = self.afn['alphabet']
        afn_transitions = self.afn['transitions']
        afn_initial = self.afn['initial_state']
        afn_finals = self.afn['final_states']
        
        # Calcular cierre epsilon del estado inicial
        initial_closure = self._epsilon_closure({afn_initial}, afn_transitions)
        self.explanation.append(f"Cierre epsilon del estado inicial: {initial_closure}")
        
        # Construir estados del AFD (subconjuntos de estados del AFN)
        afd_states = {}
        afd_states[frozenset(initial_closure)] = 'q0'
        state_counter = 1
        
        queue = [initial_closure]
        afd_transitions = []
        afd_final_states = set()
        
        # Verificar si el estado inicial es final
        if initial_closure & afn_finals:
            afd_final_states.add('q0')
        
        while queue:
            current_set = queue.pop(0)
            current_state_name = afd_states[frozenset(current_set)]
            
            # Para cada símbolo del alfabeto
            for symbol in afn_alphabet:
                # Calcular el conjunto de estados alcanzables
                next_set = set()
                for state in current_set:
                    # Buscar transiciones con este símbolo
                    for trans in afn_transitions:
                        if len(trans) >= 3 and trans[0] == state and trans[1] == symbol:
                            next_set.add(trans[2])
                
                # Calcular cierre epsilon del conjunto siguiente
                if next_set:
                    next_closure = self._epsilon_closure(next_set, afn_transitions)
                    
                    # Verificar si este conjunto ya existe
                    next_key = frozenset(next_closure)
                    if next_key not in afd_states:
                        # Crear nuevo estado
                        new_state_name = f"q{state_counter}"
                        afd_states[next_key] = new_state_name
                        state_counter += 1
                        queue.append(next_closure)
                        self.explanation.append(f"Nuevo estado creado: {new_state_name} = {next_closure}")
                    
                    next_state_name = afd_states[next_key]
                    afd_transitions.append((current_state_name, symbol, next_state_name))
                    
                    # Verificar si es estado final
                    if next_closure & afn_finals and next_state_name not in afd_final_states:
                        afd_final_states.add(next_state_name)
        
        self.explanation.append(f"AFD construido con {len(afd_states)} estados")
        
        return {
            'states': set(afd_states.values()),
            'alphabet': afn_alphabet,
            'transitions': afd_transitions,
            'initial_state': 'q0',
            'final_states': afd_final_states
        }
    
    def _epsilon_closure(self, states: Set[str], transitions: List[Tuple]) -> Set[str]:
        """
        Calcula el cierre epsilon de un conjunto de estados.
        
        Args:
            states: Conjunto de estados inicial
            transitions: Lista de transiciones del AFN
            
        Returns:
            Conjunto de estados en el cierre epsilon
        """
        closure = set(states)
        queue = list(states)
        
        while queue:
            current = queue.pop(0)
            
            # Buscar transiciones epsilon desde current
            for trans in transitions:
                if len(trans) >= 3 and trans[0] == current and trans[1] == 'ε':
                    next_state = trans[2]
                    if next_state not in closure:
                        closure.add(next_state)
                        queue.append(next_state)
        
        return closure
    
    def get_explanation(self) -> List[str]:
        """
        Obtiene la explicación del proceso de conversión.
        
        Returns:
            Lista de strings con la explicación
        """
        return self.explanation.copy()


class AFDToGrammarConverter:
    """
    Convierte Autómatas Finitos Deterministas a Gramáticas Regulares.
    """
    
    def __init__(self, afd_definition: Dict):
        """
        Inicializa el conversor con una definición de AFD.
        
        Args:
            afd_definition: Diccionario con la definición del AFD
        """
        self.afd = afd_definition
        self.explanation: List[str] = []
    
    def convert(self) -> str:
        """
        Convierte el AFD a una gramática regular.
        
        Returns:
            String con la gramática en formato texto
        """
        self.explanation = []
        self.explanation.append("Iniciando conversión de AFD a Gramática Regular")
        
        states = self.afd['states']
        alphabet = self.afd['alphabet']
        transitions = self.afd['transitions']
        initial_state = self.afd['initial_state']
        final_states = self.afd['final_states']
        
        productions = []
        
        # Crear producción para el estado inicial
        # Si el estado inicial es final, agregar producción epsilon
        if initial_state in final_states:
            productions.append(f"{initial_state} → ε")
            self.explanation.append(f"Estado inicial '{initial_state}' es final, agregando producción epsilon")
        
        # Para cada transición, crear una producción
        for trans in transitions:
            if len(trans) >= 3:
                from_state, symbol, to_state = trans[0], trans[1], trans[2]
                
                # Crear producción: from_state → symbol to_state
                production = f"{from_state} → {symbol}{to_state}"
                productions.append(production)
                
                # Si el estado destino es final, agregar producción terminal
                if to_state in final_states:
                    terminal_prod = f"{from_state} → {symbol}"
                    if terminal_prod not in productions:
                        productions.append(terminal_prod)
        
        grammar_text = "\n".join(productions)
        self.explanation.append(f"Gramática generada con {len(productions)} producciones")
        
        return grammar_text
    
    def get_explanation(self) -> List[str]:
        """
        Obtiene la explicación del proceso de conversión.
        
        Returns:
            Lista de strings con la explicación
        """
        return self.explanation.copy()


def regex_to_grammar(regex: str) -> Tuple[str, List[str]]:
    """
    Convierte una expresión regular a una gramática regular.
    
    Args:
        regex: Expresión regular
        
    Returns:
        Tupla (gramática, explicación)
    """
    # Paso 1: Regex → AFN
    regex_converter = RegexToAFNConverter(regex)
    afn = regex_converter.convert()
    explanation = regex_converter.get_explanation()
    
    # Paso 2: AFN → AFD
    afn_to_afd = AFNToAFDConverter(afn)
    afd = afn_to_afd.convert()
    explanation.extend(afn_to_afd.get_explanation())
    
    # Paso 3: AFD → Gramática
    afd_to_grammar = AFDToGrammarConverter(afd)
    grammar = afd_to_grammar.convert()
    explanation.extend(afd_to_grammar.get_explanation())
    
    return grammar, explanation


# Ejemplos de uso
if __name__ == "__main__":
    # Ejemplo: Convertir regex a gramática
    print("="*60)
    print("EJEMPLO: Conversión de Expresión Regular a Gramática")
    print("="*60)
    
    regex = "ab*"
    grammar, explanation = regex_to_grammar(regex)
    
    print(f"\nExpresión Regular: {regex}")
    print(f"\nGramática resultante:\n{grammar}")
    print("\nExplicación del proceso:")
    for line in explanation:
        print(f"  {line}")

