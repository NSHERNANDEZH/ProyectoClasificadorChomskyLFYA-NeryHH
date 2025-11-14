"""
Módulo comparador de gramáticas y autómatas.

Permite comparar dos gramáticas o autómatas para determinar:
- Si generan el mismo lenguaje
- Diferencias encontradas
- Comparación heurística hasta profundidad n
"""

from typing import Dict, List, Set, Tuple, Optional
from grammar_parser import GrammarParser
from classifier import GrammarClassifier, ChomskyType
from automata_analyzer import AutomatonAnalyzer


class GrammarComparator:
    """
    Comparador de gramáticas formales.
    
    Compara dos gramáticas para determinar si generan el mismo lenguaje
    y encuentra diferencias entre ellas.
    """
    
    def __init__(self, grammar1_text: str, grammar2_text: str):
        """
        Inicializa el comparador con dos gramáticas.
        
        Args:
            grammar1_text: Texto de la primera gramática
            grammar2_text: Texto de la segunda gramática
        """
        self.grammar1_text = grammar1_text
        self.grammar2_text = grammar2_text
        
        # Parsear gramáticas
        self.parser1 = GrammarParser()
        self.parser2 = GrammarParser()
        
        self.parser1.parse(grammar1_text)
        self.parser2.parse(grammar2_text)
        
        # Clasificar
        self.classifier1 = GrammarClassifier(self.parser1)
        self.classifier2 = GrammarClassifier(self.parser2)
        
        self.classifier1.classify()
        self.classifier2.classify()
        
        self.comparison_result: Dict = {}
        self.differences: List[str] = []
        self.similarities: List[str] = []
    
    def compare(self, max_depth: int = 5) -> Dict:
        """
        Compara las dos gramáticas.
        
        Args:
            max_depth: Profundidad máxima para comparación heurística
            
        Returns:
            Diccionario con los resultados de la comparación
        """
        self.comparison_result = {
            'grammar1_type': self.classifier1.get_classification(),
            'grammar2_type': self.classifier2.get_classification(),
            'same_type': False,
            'same_language': None,  # None = desconocido, True/False = resultado
            'differences': [],
            'similarities': [],
            'heuristic_comparison': {}
        }
        
        # Comparar tipos
        type1 = self.classifier1.get_classification()
        type2 = self.classifier2.get_classification()
        
        if type1 == type2:
            self.comparison_result['same_type'] = True
            self.similarities.append(f"Ambas gramáticas son de {type1.value}")
        else:
            self.differences.append(f"Tipos diferentes: {type1.value} vs {type2.value}")
        
        # Comparar estructura básica
        self._compare_structure()
        
        # Comparación heurística de lenguajes generados
        if max_depth > 0:
            self._heuristic_language_comparison(max_depth)
        
        self.comparison_result['differences'] = self.differences
        self.comparison_result['similarities'] = self.similarities
        
        return self.comparison_result
    
    def _compare_structure(self):
        """Compara la estructura básica de las gramáticas."""
        # Comparar símbolos terminales
        terminals1 = self.parser1.get_terminals()
        terminals2 = self.parser2.get_terminals()
        
        if terminals1 == terminals2:
            self.similarities.append(f"Alfabetos idénticos: {terminals1}")
        else:
            only_in_1 = terminals1 - terminals2
            only_in_2 = terminals2 - terminals1
            if only_in_1:
                self.differences.append(f"Símbolos terminales solo en gramática 1: {only_in_1}")
            if only_in_2:
                self.differences.append(f"Símbolos terminales solo en gramática 2: {only_in_2}")
        
        # Comparar símbolos no terminales
        non_terminals1 = self.parser1.get_non_terminals()
        non_terminals2 = self.parser2.get_non_terminals()
        
        if non_terminals1 == non_terminals2:
            self.similarities.append(f"Mismos símbolos no terminales: {non_terminals1}")
        else:
            only_in_1 = non_terminals1 - non_terminals2
            only_in_2 = non_terminals2 - non_terminals1
            if only_in_1:
                self.differences.append(f"Símbolos no terminales solo en gramática 1: {only_in_1}")
            if only_in_2:
                self.differences.append(f"Símbolos no terminales solo en gramática 2: {only_in_2}")
        
        # Comparar número de producciones
        productions1 = self.parser1.get_productions()
        productions2 = self.parser2.get_productions()
        
        num_prod1 = len(productions1)
        num_prod2 = len(productions2)
        
        if num_prod1 == num_prod2:
            self.similarities.append(f"Mismo número de producciones: {num_prod1}")
        else:
            self.differences.append(f"Número diferente de producciones: {num_prod1} vs {num_prod2}")
    
    def _heuristic_language_comparison(self, max_depth: int):
        """
        Comparación heurística de los lenguajes generados.
        
        Genera cadenas hasta una profundidad máxima y las compara.
        
        Args:
            max_depth: Profundidad máxima de derivación
        """
        # Generar cadenas de la gramática 1
        strings1 = self._generate_strings(self.parser1, max_depth)
        
        # Generar cadenas de la gramática 2
        strings2 = self._generate_strings(self.parser2, max_depth)
        
        # Comparar
        only_in_1 = strings1 - strings2
        only_in_2 = strings2 - strings1
        common = strings1 & strings2
        
        self.comparison_result['heuristic_comparison'] = {
            'strings_generated_1': len(strings1),
            'strings_generated_2': len(strings2),
            'common_strings': len(common),
            'only_in_1': len(only_in_1),
            'only_in_2': len(only_in_2),
            'sample_common': list(common)[:10],
            'sample_only_1': list(only_in_1)[:10],
            'sample_only_2': list(only_in_2)[:10]
        }
        
        if only_in_1 or only_in_2:
            if only_in_1:
                self.differences.append(f"Cadenas generadas solo por gramática 1 (muestra): {list(only_in_1)[:5]}")
            if only_in_2:
                self.differences.append(f"Cadenas generadas solo por gramática 2 (muestra): {list(only_in_2)[:5]}")
            self.comparison_result['same_language'] = False
        elif common:
            self.similarities.append(f"Las primeras {len(common)} cadenas generadas son comunes")
            # No podemos asegurar que sean iguales, solo que hasta esta profundidad coinciden
            self.comparison_result['same_language'] = None
    
    def _generate_strings(self, parser: GrammarParser, max_depth: int) -> Set[str]:
        """
        Genera cadenas hasta una profundidad máxima.
        
        Args:
            parser: GrammarParser con la gramática
            max_depth: Profundidad máxima
            
        Returns:
            Conjunto de cadenas generadas
        """
        strings = set()
        start_symbol = parser.get_start_symbol()
        productions = parser.get_productions()
        
        if not start_symbol or start_symbol not in productions:
            return strings
        
        # Generar recursivamente
        def derive(current: str, depth: int):
            if depth > max_depth:
                return
            
            # Si no hay símbolos no terminales, es una cadena terminal
            if not any(c.isupper() for c in current):
                strings.add(current)
                return
            
            # Buscar el primer no terminal
            for i, char in enumerate(current):
                if char.isupper():
                    # Buscar el no terminal completo
                    nt = char
                    j = i + 1
                    while j < len(current) and current[j].isalnum() and not current[j].islower():
                        nt += current[j]
                        j += 1
                    
                    if nt in productions:
                        # Reemplazar con todas las producciones posibles
                        for body in productions[nt]:
                            new_string = current[:i] + body + current[j:]
                            derive(new_string, depth + 1)
                    break
        
        derive(start_symbol, 0)
        return strings
    
    def get_comparison(self) -> Dict:
        """
        Obtiene el resultado de la comparación.
        
        Returns:
            Diccionario con los resultados
        """
        return self.comparison_result.copy()
    
    def get_differences(self) -> List[str]:
        """
        Obtiene la lista de diferencias encontradas.
        
        Returns:
            Lista de diferencias
        """
        return self.differences.copy()
    
    def get_similarities(self) -> List[str]:
        """
        Obtiene la lista de similitudes encontradas.
        
        Returns:
            Lista de similitudes
        """
        return self.similarities.copy()


class AutomatonComparator:
    """
    Comparador de autómatas formales.
    """
    
    def __init__(self, automaton1: Dict, automaton2: Dict):
        """
        Inicializa el comparador con dos autómatas.
        
        Args:
            automaton1: Definición del primer autómata
            automaton2: Definición del segundo autómata
        """
        self.automaton1 = automaton1
        self.automaton2 = automaton2
        
        self.analyzer1 = AutomatonAnalyzer(automaton1)
        self.analyzer2 = AutomatonAnalyzer(automaton2)
        
        self.analyzer1.analyze()
        self.analyzer2.analyze()
        
        self.comparison_result: Dict = {}
    
    def compare(self) -> Dict:
        """
        Compara los dos autómatas.
        
        Returns:
            Diccionario con los resultados de la comparación
        """
        self.comparison_result = {
            'automaton1_type': self.analyzer1.get_automaton_type(),
            'automaton2_type': self.analyzer2.get_automaton_type(),
            'same_type': False,
            'differences': [],
            'similarities': []
        }
        
        type1 = self.analyzer1.get_automaton_type()
        type2 = self.analyzer2.get_automaton_type()
        
        if type1 == type2:
            self.comparison_result['same_type'] = True
            self.comparison_result['similarities'].append(f"Ambos autómatas son de tipo {type1.value}")
        else:
            self.comparison_result['differences'].append(f"Tipos diferentes: {type1.value} vs {type2.value}")
        
        # Comparar estructura
        states1 = self.automaton1.get('states', set())
        states2 = self.automaton2.get('states', set())
        
        if len(states1) == len(states2):
            self.comparison_result['similarities'].append(f"Mismo número de estados: {len(states1)}")
        else:
            self.comparison_result['differences'].append(f"Número diferente de estados: {len(states1)} vs {len(states2)}")
        
        alphabet1 = self.automaton1.get('alphabet', set())
        alphabet2 = self.automaton2.get('alphabet', set())
        
        if alphabet1 == alphabet2:
            self.comparison_result['similarities'].append(f"Alfabetos idénticos: {alphabet1}")
        else:
            self.comparison_result['differences'].append(f"Alfabetos diferentes: {alphabet1} vs {alphabet2}")
        
        return self.comparison_result
    
    def get_comparison(self) -> Dict:
        """
        Obtiene el resultado de la comparación.
        
        Returns:
            Diccionario con los resultados
        """
        return self.comparison_result.copy()


def compare_grammars(grammar1_text: str, grammar2_text: str, max_depth: int = 5) -> Dict:
    """
    Función de conveniencia para comparar dos gramáticas.
    
    Args:
        grammar1_text: Texto de la primera gramática
        grammar2_text: Texto de la segunda gramática
        max_depth: Profundidad máxima para comparación heurística
        
    Returns:
        Diccionario con los resultados de la comparación
    """
    comparator = GrammarComparator(grammar1_text, grammar2_text)
    return comparator.compare(max_depth)


def compare_automata(automaton1: Dict, automaton2: Dict) -> Dict:
    """
    Función de conveniencia para comparar dos autómatas.
    
    Args:
        automaton1: Definición del primer autómata
        automaton2: Definición del segundo autómata
        
    Returns:
        Diccionario con los resultados de la comparación
    """
    comparator = AutomatonComparator(automaton1, automaton2)
    return comparator.compare()


# Ejemplos de uso
if __name__ == "__main__":
    # Ejemplo: Comparar dos gramáticas
    print("="*60)
    print("EJEMPLO: Comparación de Gramáticas")
    print("="*60)
    
    grammar1 = "S → aSb | ab"
    grammar2 = "S → aSb | ε"
    
    result = compare_grammars(grammar1, grammar2, max_depth=3)
    
    print(f"\nTipo gramática 1: {result['grammar1_type'].value if result['grammar1_type'] else 'N/A'}")
    print(f"Tipo gramática 2: {result['grammar2_type'].value if result['grammar2_type'] else 'N/A'}")
    print(f"Mismo tipo: {result['same_type']}")
    print(f"\nSimilitudes: {result['similarities']}")
    print(f"Diferencias: {result['differences']}")

