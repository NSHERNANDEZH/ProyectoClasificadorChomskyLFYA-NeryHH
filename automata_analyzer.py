"""
Módulo analizador de autómatas formales.

Este módulo permite analizar y clasificar diferentes tipos de autómatas:
- AFD (Autómata Finito Determinista)
- AFN (Autómata Finito No Determinista)
- AP (Autómata de Pila)
- MT (Máquina de Turing)

Clasifica autómatas según su poder de cómputo y la Jerarquía de Chomsky.
"""

from typing import Dict, List, Set, Tuple, Optional, Any
from enum import Enum


class AutomatonType(Enum):
    """Tipos de autómatas."""
    AFD = "Autómata Finito Determinista"
    AFN = "Autómata Finito No Determinista"
    AP = "Autómata de Pila"
    MT = "Máquina de Turing"


class AutomatonAnalyzer:
    """
    Analizador de autómatas formales.
    
    Permite analizar y clasificar autómatas según su tipo
    y poder de cómputo.
    """
    
    def __init__(self, automaton_definition: Dict):
        """
        Inicializa el analizador con una definición de autómata.
        
        Args:
            automaton_definition: Diccionario con la definición del autómata
                - states: Set[str] - Conjunto de estados
                - alphabet: Set[str] - Alfabeto de entrada
                - transitions: List[Tuple] - Lista de transiciones
                - initial_state: str - Estado inicial
                - final_states: Set[str] - Estados finales
                - stack_alphabet: Optional[Set[str]] - Alfabeto de pila (para AP)
                - tape_alphabet: Optional[Set[str]] - Alfabeto de cinta (para MT)
        """
        self.definition = automaton_definition
        self.states = automaton_definition.get('states', set())
        self.alphabet = automaton_definition.get('alphabet', set())
        self.transitions = automaton_definition.get('transitions', [])
        self.initial_state = automaton_definition.get('initial_state')
        self.final_states = automaton_definition.get('final_states', set())
        self.stack_alphabet = automaton_definition.get('stack_alphabet')
        self.tape_alphabet = automaton_definition.get('tape_alphabet')
        
        self.automaton_type: Optional[AutomatonType] = None
        self.analysis: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def analyze(self) -> AutomatonType:
        """
        Analiza el autómata y determina su tipo.
        
        Returns:
            Tipo de autómata identificado
        """
        self.analysis = {}
        self.errors = []
        self.warnings = []
        
        # Validar definición básica
        if not self._validate_basic_definition():
            return None
        
        # Determinar tipo de autómata
        if self.tape_alphabet is not None:
            self.automaton_type = AutomatonType.MT
            self.analysis['type'] = "Máquina de Turing"
            self.analysis['chomsky_type'] = "Tipo 0 - Recursivamente Enumerable"
            self.analysis['computational_power'] = "Máximo poder de cómputo"
        elif self.stack_alphabet is not None:
            self.automaton_type = AutomatonType.AP
            self.analysis['type'] = "Autómata de Pila"
            self.analysis['chomsky_type'] = "Tipo 2 - Libre de Contexto"
            self.analysis['computational_power'] = "Poder expresivo medio"
        else:
            # Es un autómata finito (AFD o AFN)
            is_deterministic = self._is_deterministic()
            if is_deterministic:
                self.automaton_type = AutomatonType.AFD
                self.analysis['type'] = "Autómata Finito Determinista"
            else:
                self.automaton_type = AutomatonType.AFN
                self.analysis['type'] = "Autómata Finito No Determinista"
            
            self.analysis['chomsky_type'] = "Tipo 3 - Regular"
            self.analysis['computational_power'] = "Menor poder expresivo"
        
        # Análisis adicional
        self._analyze_structure()
        self._analyze_transitions()
        
        return self.automaton_type
    
    def _validate_basic_definition(self) -> bool:
        """
        Valida la definición básica del autómata.
        
        Returns:
            True si es válida, False en caso contrario
        """
        if not self.states:
            self.errors.append("El conjunto de estados no puede estar vacío")
            return False
        
        if not self.alphabet:
            self.errors.append("El alfabeto no puede estar vacío")
            return False
        
        if self.initial_state is None:
            self.errors.append("Debe especificarse un estado inicial")
            return False
        
        if self.initial_state not in self.states:
            self.errors.append(f"El estado inicial '{self.initial_state}' no está en el conjunto de estados")
            return False
        
        for state in self.final_states:
            if state not in self.states:
                self.errors.append(f"El estado final '{state}' no está en el conjunto de estados")
                return False
        
        if not self.transitions:
            self.warnings.append("No se definieron transiciones")
        
        return True
    
    def _is_deterministic(self) -> bool:
        """
        Verifica si el autómata finito es determinista.
        
        Returns:
            True si es determinista, False en caso contrario
        """
        # Para AFD: para cada estado y símbolo, debe haber exactamente una transición
        transition_dict = {}
        
        for transition in self.transitions:
            if len(transition) < 3:
                continue
            
            state_from = transition[0]
            symbol = transition[1]
            state_to = transition[2] if len(transition) > 2 else None
            
            key = (state_from, symbol)
            
            if key in transition_dict:
                # Ya existe una transición para este estado y símbolo: no es determinista
                return False
            
            transition_dict[key] = state_to
        
        # Verificar que todas las combinaciones estado-símbolo tengan transición
        for state in self.states:
            for symbol in self.alphabet:
                if (state, symbol) not in transition_dict:
                    # Falta una transición: puede ser no determinista o incompleto
                    self.warnings.append(f"Falta transición para estado '{state}' y símbolo '{symbol}'")
        
        return True
    
    def _analyze_structure(self):
        """Analiza la estructura del autómata."""
        self.analysis['num_states'] = len(self.states)
        self.analysis['num_transitions'] = len(self.transitions)
        self.analysis['num_final_states'] = len(self.final_states)
        self.analysis['alphabet_size'] = len(self.alphabet)
        
        # Estados alcanzables
        reachable_states = self._find_reachable_states()
        self.analysis['reachable_states'] = reachable_states
        self.analysis['num_reachable_states'] = len(reachable_states)
        
        unreachable = self.states - reachable_states
        if unreachable:
            self.warnings.append(f"Estados no alcanzables: {unreachable}")
        
        # Estados que pueden llegar a un estado final
        co_reachable_states = self._find_coreachable_states()
        self.analysis['coreachable_states'] = co_reachable_states
        self.analysis['num_coreachable_states'] = len(co_reachable_states)
        
        useless = self.states - (reachable_states & co_reachable_states)
        if useless:
            self.warnings.append(f"Estados inútiles (no alcanzables o no co-alcanzables): {useless}")
    
    def _find_reachable_states(self) -> Set[str]:
        """
        Encuentra todos los estados alcanzables desde el estado inicial.
        
        Returns:
            Conjunto de estados alcanzables
        """
        reachable = {self.initial_state}
        queue = [self.initial_state]
        
        while queue:
            current = queue.pop(0)
            
            # Buscar todas las transiciones desde current
            for transition in self.transitions:
                if len(transition) >= 3 and transition[0] == current:
                    next_state = transition[2]
                    if next_state not in reachable:
                        reachable.add(next_state)
                        queue.append(next_state)
        
        return reachable
    
    def _find_coreachable_states(self) -> Set[str]:
        """
        Encuentra todos los estados que pueden llegar a un estado final.
        
        Returns:
            Conjunto de estados co-alcanzables
        """
        coreachable = set(self.final_states)
        queue = list(self.final_states)
        
        # Construir grafo inverso (transiciones al revés)
        reverse_transitions = {}
        for transition in self.transitions:
            if len(transition) >= 3:
                from_state = transition[0]
                to_state = transition[2]
                if to_state not in reverse_transitions:
                    reverse_transitions[to_state] = []
                reverse_transitions[to_state].append(from_state)
        
        while queue:
            current = queue.pop(0)
            
            # Buscar estados que pueden llegar a current
            if current in reverse_transitions:
                for prev_state in reverse_transitions[current]:
                    if prev_state not in coreachable:
                        coreachable.add(prev_state)
                        queue.append(prev_state)
        
        return coreachable
    
    def _analyze_transitions(self):
        """Analiza las transiciones del autómata."""
        transition_dict = {}
        
        for transition in self.transitions:
            if len(transition) < 3:
                continue
            
            state_from = transition[0]
            symbol = transition[1]
            state_to = transition[2]
            
            if state_from not in transition_dict:
                transition_dict[state_from] = {}
            
            if symbol not in transition_dict[state_from]:
                transition_dict[state_from][symbol] = []
            
            transition_dict[state_from][symbol].append(state_to)
        
        self.analysis['transition_structure'] = transition_dict
        
        # Verificar transiciones epsilon (para AFN)
        has_epsilon = False
        for transition in self.transitions:
            if len(transition) >= 2 and transition[1] == 'ε':
                has_epsilon = True
                break
        
        self.analysis['has_epsilon_transitions'] = has_epsilon
        if has_epsilon and self.automaton_type == AutomatonType.AFD:
            self.warnings.append("Se encontraron transiciones epsilon en un autómata supuestamente determinista")
    
    def get_analysis(self) -> Dict[str, Any]:
        """
        Obtiene el análisis completo del autómata.
        
        Returns:
            Diccionario con el análisis
        """
        return self.analysis.copy()
    
    def get_errors(self) -> List[str]:
        """
        Obtiene la lista de errores encontrados.
        
        Returns:
            Lista de mensajes de error
        """
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """
        Obtiene la lista de advertencias encontradas.
        
        Returns:
            Lista de mensajes de advertencia
        """
        return self.warnings.copy()
    
    def get_automaton_type(self) -> Optional[AutomatonType]:
        """
        Obtiene el tipo de autómata identificado.
        
        Returns:
            Tipo de autómata o None
        """
        return self.automaton_type


def analyze_automaton(automaton_definition: Dict) -> Tuple[Optional[AutomatonType], Dict, List[str], List[str]]:
    """
    Función de conveniencia para analizar un autómata.
    
    Args:
        automaton_definition: Diccionario con la definición del autómata
        
    Returns:
        Tupla (tipo, análisis, errores, advertencias)
    """
    analyzer = AutomatonAnalyzer(automaton_definition)
    automaton_type = analyzer.analyze()
    analysis = analyzer.get_analysis()
    errors = analyzer.get_errors()
    warnings = analyzer.get_warnings()
    
    return automaton_type, analysis, errors, warnings


# Ejemplos de uso
if __name__ == "__main__":
    # Ejemplo 1: AFD
    print("="*60)
    print("EJEMPLO 1: Autómata Finito Determinista (AFD)")
    print("="*60)
    
    afd_definition = {
        'states': {'q0', 'q1', 'q2'},
        'alphabet': {'a', 'b'},
        'transitions': [
            ('q0', 'a', 'q1'),
            ('q0', 'b', 'q0'),
            ('q1', 'a', 'q2'),
            ('q1', 'b', 'q1'),
            ('q2', 'a', 'q2'),
            ('q2', 'b', 'q2')
        ],
        'initial_state': 'q0',
        'final_states': {'q2'}
    }
    
    type1, analysis1, errors1, warnings1 = analyze_automaton(afd_definition)
    if type1:
        print(f"Tipo: {type1.value}")
        print(f"Análisis: {analysis1}")
        if warnings1:
            print(f"Advertencias: {warnings1}")
    
    # Ejemplo 2: AFN
    print("\n" + "="*60)
    print("EJEMPLO 2: Autómata Finito No Determinista (AFN)")
    print("="*60)
    
    afn_definition = {
        'states': {'q0', 'q1', 'q2'},
        'alphabet': {'a', 'b'},
        'transitions': [
            ('q0', 'a', 'q0'),
            ('q0', 'a', 'q1'),
            ('q1', 'b', 'q2')
        ],
        'initial_state': 'q0',
        'final_states': {'q2'}
    }
    
    type2, analysis2, errors2, warnings2 = analyze_automaton(afn_definition)
    if type2:
        print(f"Tipo: {type2.value}")
        print(f"Análisis: {analysis2}")

