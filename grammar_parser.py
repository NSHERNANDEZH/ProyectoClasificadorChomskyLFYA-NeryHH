"""
Módulo para parsear y analizar gramáticas formales en formato BNF y reglas simples.

Este módulo permite:
- Parsear gramáticas en formato BNF (Backus-Naur Form)
- Parsear gramáticas en formato de reglas simples
- Extraer símbolos terminales y no terminales
- Validar la estructura de las producciones
- Normalizar el formato de las gramáticas
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from utils.helpers import (
    clean_grammar_text,
    parse_production,
    extract_symbols,
    is_epsilon_production,
    normalize_symbol,
    find_start_symbol
)
from utils.validators import (
    validate_grammar_format,
    validate_production,
    check_grammar_consistency
)


class GrammarParser:
    """
    Parser para gramáticas formales en diferentes formatos.
    
    Soporta:
    - Formato BNF estándar
    - Formato de reglas simples (S → aSb | ab)
    - Múltiples símbolos de producción (→, ->, ::=)
    """
    
    def __init__(self):
        """Inicializa el parser."""
        self.productions: Dict[str, List[str]] = {}
        self.terminals: Set[str] = set()
        self.non_terminals: Set[str] = set()
        self.start_symbol: Optional[str] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def parse(self, grammar_text: str) -> bool:
        """
        Parsea una gramática desde texto.
        
        Args:
            grammar_text: Texto con la gramática en formato BNF o reglas simples
            
        Returns:
            True si el parseo fue exitoso, False en caso contrario
            
        Example:
            >>> parser = GrammarParser()
            >>> grammar = "S → aSb | ab"
            >>> parser.parse(grammar)
            True
        """
        self.productions = {}
        self.terminals = set()
        self.non_terminals = set()
        self.errors = []
        self.warnings = []
        
        # Validar formato básico
        is_valid, error_msg = validate_grammar_format(grammar_text)
        if not is_valid:
            self.errors.append(error_msg)
            return False
        
        # Limpiar texto
        cleaned_text = clean_grammar_text(grammar_text)
        
        # Separar en líneas
        lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
        
        # Parsear cada línea
        for line_num, line in enumerate(lines, 1):
            try:
                left, bodies = parse_production(line)
                
                # Validar producción
                is_valid, error_msg = validate_production(left, bodies)
                if not is_valid:
                    self.errors.append(f"Línea {line_num}: {error_msg}")
                    continue
                
                # Agregar producción
                if left in self.productions:
                    # Si ya existe, combinar los cuerpos
                    self.productions[left].extend(bodies)
                else:
                    self.productions[left] = bodies
                
            except ValueError as e:
                self.errors.append(f"Línea {line_num}: {str(e)}")
                continue
        
        if self.errors:
            return False
        
        # Extraer símbolos
        self.terminals, self.non_terminals = extract_symbols(self.productions)
        
        # Encontrar símbolo inicial
        self.start_symbol = find_start_symbol(self.productions)
        
        # Verificar consistencia
        is_consistent, consistency_warnings = check_grammar_consistency(self.productions)
        self.warnings.extend(consistency_warnings)
        
        return True
    
    def get_productions(self) -> Dict[str, List[str]]:
        """
        Obtiene el diccionario de producciones parseadas.
        
        Returns:
            Diccionario {símbolo_no_terminal: [cuerpos]}
        """
        return self.productions.copy()
    
    def get_terminals(self) -> Set[str]:
        """
        Obtiene el conjunto de símbolos terminales.
        
        Returns:
            Conjunto de símbolos terminales
        """
        return self.terminals.copy()
    
    def get_non_terminals(self) -> Set[str]:
        """
        Obtiene el conjunto de símbolos no terminales.
        
        Returns:
            Conjunto de símbolos no terminales
        """
        return self.non_terminals.copy()
    
    def get_start_symbol(self) -> Optional[str]:
        """
        Obtiene el símbolo inicial de la gramática.
        
        Returns:
            Símbolo inicial o None
        """
        return self.start_symbol
    
    def get_errors(self) -> List[str]:
        """
        Obtiene la lista de errores encontrados durante el parseo.
        
        Returns:
            Lista de mensajes de error
        """
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """
        Obtiene la lista de advertencias encontradas durante el parseo.
        
        Returns:
            Lista de mensajes de advertencia
        """
        return self.warnings.copy()
    
    def format_grammar(self) -> str:
        """
        Formatea la gramática parseada en texto legible.
        
        Returns:
            String con la gramática formateada
        """
        if not self.productions:
            return ""
        
        lines = []
        if self.start_symbol and self.start_symbol in self.productions:
            bodies = self.productions[self.start_symbol]
            lines.append(f"{self.start_symbol} → {' | '.join(bodies)}")
        
        for nt, bodies in sorted(self.productions.items()):
            if nt != self.start_symbol:
                lines.append(f"{nt} → {' | '.join(bodies)}")
        
        return '\n'.join(lines)
    
    def analyze_production(self, left: str, body: str) -> Dict:
        """
        Analiza una producción individual y proporciona información detallada.
        
        Args:
            left: Símbolo no terminal del lado izquierdo
            body: Cuerpo de la producción
            
        Returns:
            Diccionario con información del análisis
        """
        analysis = {
            'left': left,
            'body': body,
            'is_epsilon': is_epsilon_production(body),
            'length': len(body),
            'has_terminal': False,
            'has_non_terminal': False,
            'terminals_in_body': [],
            'non_terminals_in_body': [],
            'structure': 'unknown'
        }
        
        if analysis['is_epsilon']:
            analysis['structure'] = 'epsilon'
            return analysis
        
        # Buscar símbolos terminales y no terminales
        terminals_found = []
        non_terminals_found = []
        
        # Buscar no terminales (letras mayúsculas seguidas de letras/números)
        nt_pattern = r'[A-Z][a-zA-Z0-9]*'
        nts = re.findall(nt_pattern, body)
        non_terminals_found = list(set(nts))
        
        # Buscar terminales (todo lo que no sea no terminal)
        # Simplificado: asumimos que los terminales son caracteres individuales
        # o secuencias entre comillas
        body_chars = list(body)
        for char in body_chars:
            if char.islower() or char.isdigit() or char in ['(', ')', '+', '*', '|', 'ε', 'λ']:
                if char not in terminals_found:
                    terminals_found.append(char)
        
        analysis['has_terminal'] = len(terminals_found) > 0
        analysis['has_non_terminal'] = len(non_terminals_found) > 0
        analysis['terminals_in_body'] = terminals_found
        analysis['non_terminals_in_body'] = non_terminals_found
        
        # Determinar estructura
        if not non_terminals_found:
            analysis['structure'] = 'terminal_only'
        elif not terminals_found:
            analysis['structure'] = 'non_terminal_only'
        else:
            analysis['structure'] = 'mixed'
        
        return analysis


def parse_grammar_from_text(text: str) -> Tuple[Optional[GrammarParser], List[str]]:
    """
    Función de conveniencia para parsear una gramática desde texto.
    
    Args:
        text: Texto con la gramática
        
    Returns:
        Tupla (parser, errores)
        - parser: GrammarParser con la gramática parseada o None si hubo errores
        - errores: Lista de errores encontrados
    """
    parser = GrammarParser()
    success = parser.parse(text)
    
    if success:
        return parser, []
    else:
        return None, parser.get_errors()


# Ejemplos de uso
if __name__ == "__main__":
    # Ejemplo 1: Gramática Regular (Tipo 3)
    grammar1 = """
    S → aA
    A → bB | b
    B → a
    """
    
    parser1 = GrammarParser()
    if parser1.parse(grammar1):
        print("Gramática 1 parseada correctamente:")
        print(parser1.format_grammar())
        print(f"Terminales: {parser1.get_terminals()}")
        print(f"No terminales: {parser1.get_non_terminals()}")
        print(f"Símbolo inicial: {parser1.get_start_symbol()}")
    else:
        print("Errores:", parser1.get_errors())
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 2: Gramática Libre de Contexto (Tipo 2)
    grammar2 = """
    S → aSb | ab
    """
    
    parser2 = GrammarParser()
    if parser2.parse(grammar2):
        print("Gramática 2 parseada correctamente:")
        print(parser2.format_grammar())
        print(f"Terminales: {parser2.get_terminals()}")
        print(f"No terminales: {parser2.get_non_terminals()}")
    else:
        print("Errores:", parser2.get_errors())
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 3: Análisis de producción individual
    parser3 = GrammarParser()
    parser3.parse("S → aSb")
    analysis = parser3.analyze_production('S', 'aSb')
    print("Análisis de producción S → aSb:")
    for key, value in analysis.items():
        print(f"  {key}: {value}")

