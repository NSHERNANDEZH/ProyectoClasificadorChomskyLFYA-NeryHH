"""
Módulo generador automático de ejemplos de gramáticas.

Genera gramáticas aleatorias de cada tipo de la Jerarquía de Chomsky,
validando que cumplan las restricciones correspondientes.
"""

import random
from typing import Dict, List, Set, Tuple
from grammar_parser import GrammarParser
from classifier import GrammarClassifier, ChomskyType


class ExampleGenerator:
    """
    Generador de ejemplos de gramáticas por tipo de Chomsky.
    """
    
    def __init__(self):
        """Inicializa el generador."""
        self.terminals = ['a', 'b', 'c']
        self.non_terminal_counter = 0
    
    def generate_type_3(self, complexity: str = "simple") -> str:
        """
        Genera una gramática regular (Tipo 3).
        
        Args:
            complexity: Nivel de complejidad ("simple", "medium", "complex")
            
        Returns:
            String con la gramática en formato texto
        """
        num_productions = {
            "simple": 3,
            "medium": 5,
            "complex": 8
        }.get(complexity, 3)
        
        productions = []
        start_symbol = 'S'
        used_nts = {start_symbol}
        
        # Generar producciones regulares (forma derecha)
        current_nt = start_symbol
        
        for i in range(num_productions):
            # Decidir si terminar o continuar
            if i < num_productions - 1:
                # Crear producción que lleva a otro no terminal
                next_nt = self._get_next_nt(used_nts)
                terminal = random.choice(self.terminals)
                productions.append(f"{current_nt} → {terminal}{next_nt}")
                current_nt = next_nt
            else:
                # Última producción: terminal o epsilon
                terminal = random.choice(self.terminals)
                productions.append(f"{current_nt} → {terminal}")
        
        return "\n".join(productions)
    
    def generate_type_2(self, complexity: str = "simple") -> str:
        """
        Genera una gramática libre de contexto (Tipo 2).
        
        Args:
            complexity: Nivel de complejidad ("simple", "medium", "complex")
            
        Returns:
            String con la gramática en formato texto
        """
        num_productions = {
            "simple": 2,
            "medium": 4,
            "complex": 6
        }.get(complexity, 2)
        
        productions = []
        start_symbol = 'S'
        
        # Ejemplo simple: S → aSb | ab
        if complexity == "simple":
            productions.append("S → aSb | ab")
        else:
            # Generar producciones más complejas
            for i in range(num_productions):
                nt = 'S' if i == 0 else self._get_next_nt({'S'})
                # Generar cuerpo con terminales y no terminales
                body_parts = []
                num_parts = random.randint(1, 3)
                for _ in range(num_parts):
                    if random.random() < 0.5:
                        body_parts.append(random.choice(self.terminals))
                    else:
                        body_parts.append('S')
                body = ''.join(body_parts)
                productions.append(f"{nt} → {body}")
        
        return "\n".join(productions)
    
    def generate_type_1(self, complexity: str = "simple") -> str:
        """
        Genera una gramática sensible al contexto (Tipo 1).
        
        Args:
            complexity: Nivel de complejidad ("simple", "medium", "complex")
            
        Returns:
            String con la gramática en formato texto
        """
        # Ejemplo clásico: a^n b^n c^n
        if complexity == "simple":
            return """S → aSBC | aBC
CB → BC
aB → ab
bB → bb
bC → bc
cC → cc"""
        else:
            # Generar gramática más compleja
            productions = [
                "S → aSBC | aBC",
                "CB → BC",
                "aB → ab",
                "bB → bb",
                "bC → bc",
                "cC → cc"
            ]
            return "\n".join(productions)
    
    def generate_type_0(self, complexity: str = "simple") -> str:
        """
        Genera una gramática recursivamente enumerable (Tipo 0).
        
        Args:
            complexity: Nivel de complejidad ("simple", "medium", "complex")
            
        Returns:
            String con la gramática en formato texto
        """
        if complexity == "simple":
            return """S → ACaB
Ca → aaC
CB → DB | E"""
        else:
            productions = [
                "S → ACaB",
                "Ca → aaC",
                "CB → DB | E",
                "aD → Da",
                "AD → AC",
                "aE → Ea",
                "AE → ε"
            ]
            return "\n".join(productions)
    
    def _get_next_nt(self, used_nts: Set[str]) -> str:
        """
        Genera el siguiente símbolo no terminal.
        
        Args:
            used_nts: Conjunto de no terminales ya usados
            
        Returns:
            Nuevo símbolo no terminal
        """
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for letter in letters:
            if letter not in used_nts:
                used_nts.add(letter)
                return letter
        
        # Si se agotaron las letras, usar con número
        self.non_terminal_counter += 1
        return f"X{self.non_terminal_counter}"
    
    def generate_and_validate(self, chomsky_type: ChomskyType, complexity: str = "simple") -> Tuple[str, bool, List[str]]:
        """
        Genera una gramática y valida que sea del tipo correcto.
        
        Args:
            chomsky_type: Tipo de Chomsky deseado
            complexity: Nivel de complejidad
            
        Returns:
            Tupla (gramática, es_válida, explicación)
        """
        # Generar gramática
        if chomsky_type == ChomskyType.TYPE_3:
            grammar_text = self.generate_type_3(complexity)
        elif chomsky_type == ChomskyType.TYPE_2:
            grammar_text = self.generate_type_2(complexity)
        elif chomsky_type == ChomskyType.TYPE_1:
            grammar_text = self.generate_type_1(complexity)
        else:  # TYPE_0
            grammar_text = self.generate_type_0(complexity)
        
        # Validar
        parser = GrammarParser()
        if not parser.parse(grammar_text):
            return grammar_text, False, parser.get_errors()
        
        classifier = GrammarClassifier(parser)
        detected_type = classifier.classify()
        
        is_valid = (detected_type == chomsky_type)
        explanation = classifier.get_explanation()
        
        return grammar_text, is_valid, explanation


def generate_example(chomsky_type: ChomskyType, complexity: str = "simple") -> Dict:
    """
    Función de conveniencia para generar un ejemplo.
    
    Args:
        chomsky_type: Tipo de Chomsky
        complexity: Nivel de complejidad
        
    Returns:
        Diccionario con la gramática y validación
    """
    generator = ExampleGenerator()
    grammar, is_valid, explanation = generator.generate_and_validate(chomsky_type, complexity)
    
    return {
        'grammar': grammar,
        'is_valid': is_valid,
        'explanation': explanation,
        'requested_type': chomsky_type.value,
        'complexity': complexity
    }


# Ejemplos de uso
if __name__ == "__main__":
    from classifier import ChomskyType
    
    print("="*60)
    print("Generador de Ejemplos de Gramáticas")
    print("="*60)
    
    # Generar ejemplo de Tipo 3
    print("\nGenerando gramática Tipo 3 (Regular)...")
    example3 = generate_example(ChomskyType.TYPE_3, "simple")
    print(f"Gramática:\n{example3['grammar']}")
    print(f"Válida: {example3['is_valid']}")
    
    # Generar ejemplo de Tipo 2
    print("\nGenerando gramática Tipo 2 (Libre de Contexto)...")
    example2 = generate_example(ChomskyType.TYPE_2, "simple")
    print(f"Gramática:\n{example2['grammar']}")
    print(f"Válida: {example2['is_valid']}")

