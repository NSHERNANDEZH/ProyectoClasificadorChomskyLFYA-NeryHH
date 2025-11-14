"""
Módulo parser de definiciones de autómatas.

Parsea definiciones de autómatas en formato texto estructurado.
"""

import re
from typing import Dict, List, Set, Tuple, Optional


class AutomataParser:
    """
    Parser para definiciones de autómatas en formato texto.
    """
    
    def __init__(self):
        """Inicializa el parser."""
        self.states: Set[str] = set()
        self.alphabet: Set[str] = set()
        self.transitions: List[Tuple] = []
        self.initial_state: Optional[str] = None
        self.final_states: Set[str] = set()
        self.stack_alphabet: Optional[Set[str]] = None
        self.tape_alphabet: Optional[Set[str]] = None
        self.errors: List[str] = []
    
    def parse(self, definition_text: str) -> bool:
        """
        Parsea una definición de autómata desde texto.
        
        Args:
            definition_text: Texto con la definición del autómata
            
        Returns:
            True si el parseo fue exitoso, False en caso contrario
        """
        self.states = set()
        self.alphabet = set()
        self.transitions = []
        self.initial_state = None
        self.final_states = set()
        self.stack_alphabet = None
        self.tape_alphabet = None
        self.errors = []
        
        lines = [line.strip() for line in definition_text.split('\n') if line.strip()]
        
        for line in lines:
            # Parsear estados
            if line.lower().startswith('estados:'):
                states_str = line.split(':', 1)[1].strip()
                self.states = {s.strip() for s in states_str.split(',')}
            
            # Parsear alfabeto
            elif line.lower().startswith('alfabeto:'):
                alphabet_str = line.split(':', 1)[1].strip()
                self.alphabet = {a.strip() for a in alphabet_str.split(',')}
            
            # Parsear alfabeto de pila
            elif 'alfabeto de pila' in line.lower():
                stack_str = line.split(':', 1)[1].strip()
                self.stack_alphabet = {s.strip() for s in stack_str.split(',')}
            
            # Parsear alfabeto de cinta
            elif 'alfabeto de cinta' in line.lower():
                tape_str = line.split(':', 1)[1].strip()
                self.tape_alphabet = {t.strip() for t in tape_str.split(',')}
            
            # Parsear estado inicial
            elif 'estado inicial' in line.lower():
                self.initial_state = line.split(':', 1)[1].strip()
            
            # Parsear estados finales
            elif 'estados finales' in line.lower():
                finals_str = line.split(':', 1)[1].strip()
                self.final_states = {f.strip() for f in finals_str.split(',')}
            
            # Parsear transiciones
            elif line.lower().startswith('transiciones:') or ',' in line:
                if not line.lower().startswith('transiciones:'):
                    # Es una transición
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        self.transitions.append(tuple(parts))
        
        # Validar
        if not self.states:
            self.errors.append("No se encontraron estados")
        if not self.alphabet:
            self.errors.append("No se encontró alfabeto")
        if not self.initial_state:
            self.errors.append("No se encontró estado inicial")
        
        return len(self.errors) == 0
    
    def get_definition(self) -> Dict:
        """
        Obtiene la definición del autómata como diccionario.
        
        Returns:
            Diccionario con la definición
        """
        result = {
            'states': self.states,
            'alphabet': self.alphabet,
            'transitions': self.transitions,
            'initial_state': self.initial_state,
            'final_states': self.final_states
        }
        
        if self.stack_alphabet:
            result['stack_alphabet'] = self.stack_alphabet
        
        if self.tape_alphabet:
            result['tape_alphabet'] = self.tape_alphabet
        
        return result
    
    def get_errors(self) -> List[str]:
        """
        Obtiene la lista de errores.
        
        Returns:
            Lista de errores
        """
        return self.errors.copy()

