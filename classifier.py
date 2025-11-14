"""
Módulo clasificador de gramáticas según la Jerarquía de Chomsky.

Este módulo clasifica gramáticas formales en uno de los cuatro tipos:
- Tipo 0: Recursivamente Enumerable (sin restricciones)
- Tipo 1: Sensible al Contexto (αAβ → αγβ, |γ| >= 1)
- Tipo 2: Libre de Contexto (A → α)
- Tipo 3: Regular (A → aB | a o A → Ba | a)

Incluye modo explicativo que justifica la clasificación paso a paso.
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from enum import Enum
from grammar_parser import GrammarParser


class ChomskyType(Enum):
    """Tipos de la Jerarquía de Chomsky."""
    TYPE_0 = "Tipo 0 - Recursivamente Enumerable"
    TYPE_1 = "Tipo 1 - Sensible al Contexto"
    TYPE_2 = "Tipo 2 - Libre de Contexto"
    TYPE_3 = "Tipo 3 - Regular"


class GrammarClassifier:
    """
    Clasificador de gramáticas según la Jerarquía de Chomsky.
    
    Implementa algoritmos para determinar el tipo más restrictivo
    que una gramática puede tener, con explicaciones detalladas.
    """
    
    def __init__(self, parser: GrammarParser):
        """
        Inicializa el clasificador con un parser de gramática.
        
        Args:
            parser: GrammarParser con la gramática ya parseada
        """
        self.parser = parser
        self.productions = parser.get_productions()
        self.terminals = parser.get_terminals()
        self.non_terminals = parser.get_non_terminals()
        self.start_symbol = parser.get_start_symbol()
        self.classification: Optional[ChomskyType] = None
        self.explanation: List[str] = []
        self.violations: List[Dict] = []
        self.problematic_productions: List[str] = []
    
    def classify(self) -> ChomskyType:
        """
        Clasifica la gramática según la Jerarquía de Chomsky.
        
        Returns:
            Tipo de Chomsky más restrictivo que cumple la gramática
        """
        self.explanation = []
        self.violations = []
        self.problematic_productions = []
        
        if not self.productions:
            self.explanation.append("ERROR: La gramática está vacía")
            self.classification = None
            return None
        
        self.explanation.append("Iniciando clasificación de la gramática...")
        self.explanation.append(f"Símbolo inicial: {self.start_symbol}")
        self.explanation.append(f"Número de producciones: {len(self.productions)}")
        
        # Intentar clasificar desde el tipo más restrictivo al menos restrictivo
        # Tipo 3 (Regular) → Tipo 2 (Libre de Contexto) → Tipo 1 (Sensible al Contexto) → Tipo 0
        
        if self._is_type_3():
            self.classification = ChomskyType.TYPE_3
            self.explanation.append("\nTipo detectado: Tipo 3 (Gramática Regular)")
            self.explanation.append("\nJustificación: todas las producciones son del tipo A → aB o A → a")
            return ChomskyType.TYPE_3
        
        if self._is_type_2():
            self.classification = ChomskyType.TYPE_2
            self.explanation.append("\nTipo detectado: Tipo 2 (Gramática Libre de Contexto)")
            self.explanation.append("\nJustificación: las producciones son del tipo A → β con una sola variable en el lado izquierdo.")
            return ChomskyType.TYPE_2
        
        if self._is_type_1():
            self.classification = ChomskyType.TYPE_1
            self.explanation.append("\nTipo detectado: Tipo 1 (Gramática Sensible al Contexto)")
            self.explanation.append("\nJustificación: las producciones cumplen con la forma αAβ → αγβ donde |γ| >= 1.")
            return ChomskyType.TYPE_1
        
        # Si no cumple ninguna restricción, es Tipo 0
        self.classification = ChomskyType.TYPE_0
        self.explanation.append("\nTipo detectado: Tipo 0 (Gramática Recursivamente Enumerable)")
        self.explanation.append("\nJustificación:")
        
        # Analizar por qué no es Tipo 1, 2 o 3
        reasons = []
        
        # Verificar violaciones de Tipo 1
        for left, bodies in self.productions.items():
            for body in bodies:
                if body in ['ε', 'λ', ''] and left != self.start_symbol:
                    reasons.append(f"• Existe una producción {left} → ε que NO está permitida en las gramáticas Tipo 1 salvo casos especiales (que aquí no se cumplen).")
                elif len(body) < len(left):
                    reasons.append(f"• La producción {left} → {body} NO cumple |α| ≤ |β| (|{left}| = {len(left)} > |{body}| = {len(body)}). Esto rompe la condición de expansión de las gramáticas sensibles al contexto.")
        
        # Verificar violaciones de Tipo 2
        for left, bodies in self.productions.items():
            if len(left) > 1 or not re.match(r'^[A-Z][a-zA-Z0-9]*$', left):
                reasons.append(f"• La producción {left} → ... tiene múltiples símbolos en el lado izquierdo, violando la estructura A → β de Tipo 2.")
        
        if reasons:
            self.explanation.append("\n".join(reasons))
        
        self.explanation.append("\nConclusión: La gramática NO puede ser Tipo 1, Tipo 2 ni Tipo 3.")
        self.explanation.append("Por lo tanto, pertenece al Tipo 0.")
        return ChomskyType.TYPE_0
    
    def _is_type_3(self) -> bool:
        """
        Verifica si la gramática es Tipo 3 (Regular).
        
        Tipo 3: Forma A → aB | a (derecha) o A → Ba | a (izquierda)
        También puede ser A → ε
        
        Returns:
            True si es Tipo 3, False en caso contrario
        """
        self.explanation.append("\n--- Verificando Tipo 3 (Regular) ---")
        
        is_regular = True
        violations = []
        
        for left, bodies in self.productions.items():
            for body in bodies:
                # Verificar si es epsilon
                if body in ['ε', 'λ', '']:
                    # Epsilon solo está permitido si es el símbolo inicial
                    if left != self.start_symbol:
                        is_regular = False
                        violations.append({
                            'production': f"{left} → {body}",
                            'reason': "Producción epsilon solo permitida para símbolo inicial"
                        })
                        self.problematic_productions.append(f"{left} → {body}")
                    continue
                
                # Verificar forma regular
                # Forma derecha: A → aB o A → a
                # Forma izquierda: A → Ba o A → a
                # Donde 'a' es terminal y 'B' es no terminal
                
                # Buscar no terminales que realmente existen en la gramática
                non_terminals_in_body = []
                for nt in self.non_terminals:
                    if nt in body:
                        # Verificar que no sea parte de un no terminal más largo
                        pos = 0
                        while True:
                            pos = body.find(nt, pos)
                            if pos == -1:
                                break
                            # Verificar que no sea parte de otro no terminal
                            before_ok = (pos == 0 or body[pos-1].islower() or not body[pos-1].isalnum())
                            after_ok = (pos + len(nt) == len(body) or 
                                       body[pos + len(nt)].islower() or 
                                       not body[pos + len(nt)].isalnum())
                            if before_ok and after_ok:
                                if nt not in non_terminals_in_body:
                                    non_terminals_in_body.append(nt)
                            pos += len(nt)
                
                if len(non_terminals_in_body) > 1:
                    # Más de un no terminal: no es regular
                    is_regular = False
                    violations.append({
                        'production': f"{left} → {body}",
                        'reason': f"Contiene más de un símbolo no terminal: {non_terminals_in_body}"
                    })
                    self.problematic_productions.append(f"{left} → {body}")
                    continue
                
                if len(non_terminals_in_body) == 1:
                    # Debe ser de la forma aB (derecha) o Ba (izquierda)
                    # NO puede ser aBb (terminales a ambos lados)
                    nt = non_terminals_in_body[0]
                    nt_pos = body.find(nt)
                    
                    # Verificar si es forma derecha (aB) o izquierda (Ba)
                    is_right_linear = nt_pos == len(body) - len(nt)  # No terminal al final
                    is_left_linear = nt_pos == 0  # No terminal al inicio
                    
                    if not (is_right_linear or is_left_linear):
                        # El no terminal está en el medio: no es regular
                        is_regular = False
                        violations.append({
                            'production': f"{left} → {body}",
                            'reason': f"El no terminal '{nt}' está en el medio (no es forma derecha ni izquierda)"
                        })
                        self.problematic_productions.append(f"{left} → {body}")
                        continue
                    
                    # Verificar que solo haya terminales antes/después del no terminal
                    if is_right_linear:
                        # Forma derecha: aB - verificar que el prefijo sea solo terminales
                        prefix = body[:nt_pos]
                        if prefix and not self._is_terminal_string(prefix):
                            is_regular = False
                            violations.append({
                                'production': f"{left} → {body}",
                                'reason': f"El prefijo '{prefix}' contiene símbolos no terminales"
                            })
                            self.problematic_productions.append(f"{left} → {body}")
                    else:  # is_left_linear
                        # Forma izquierda: Ba - verificar que el sufijo sea solo terminales
                        suffix = body[nt_pos + len(nt):]
                        if suffix and not self._is_terminal_string(suffix):
                            is_regular = False
                            violations.append({
                                'production': f"{left} → {body}",
                                'reason': f"El sufijo '{suffix}' contiene símbolos no terminales"
                            })
                            self.problematic_productions.append(f"{left} → {body}")
                else:
                    # No hay no terminales: debe ser solo terminales (A → a)
                    if not self._is_terminal_string(body):
                        is_regular = False
                        violations.append({
                            'production': f"{left} → {body}",
                            'reason': "El cuerpo contiene símbolos no terminales"
                        })
                        self.problematic_productions.append(f"{left} → {body}")
        
        # Verificar consistencia: todas las producciones deben ser del mismo tipo (derecha o izquierda)
        if is_regular and len(self.productions) > 1:
            is_right_linear_grammar = None
            for left, bodies in self.productions.items():
                for body in bodies:
                    if body in ['ε', 'λ', '']:
                        continue
                    
                    # Buscar no terminales usando la misma lógica que arriba
                    found_nts = []
                    for nt in self.non_terminals:
                        if nt in body:
                            pos = 0
                            while True:
                                pos = body.find(nt, pos)
                                if pos == -1:
                                    break
                                before_ok = (pos == 0 or body[pos-1].islower() or not body[pos-1].isalnum())
                                after_ok = (pos + len(nt) == len(body) or 
                                           body[pos + len(nt)].islower() or 
                                           not body[pos + len(nt)].isalnum())
                                if before_ok and after_ok:
                                    if nt not in found_nts:
                                        found_nts.append(nt)
                                pos += len(nt)
                    
                    if found_nts:
                        # Usar el primer no terminal encontrado
                        nt = found_nts[0]
                        nt_pos = body.find(nt)
                        is_right = (nt_pos == len(body) - len(nt))
                        if is_right_linear_grammar is None:
                            is_right_linear_grammar = is_right
                        elif is_right_linear_grammar != is_right:
                            is_regular = False
                            violations.append({
                                'production': f"{left} → {body}",
                                'reason': "Mezcla de formas derecha e izquierda en la gramática"
                            })
                            self.problematic_productions.append(f"{left} → {body}")
        
        if violations:
            self.violations.extend(violations)
            self.explanation.append(f"✗ No es Tipo 3. Violaciones encontradas: {len(violations)}")
            for v in violations:
                self.explanation.append(f"  - {v['production']}: {v['reason']}")
        else:
            self.explanation.append("✓ Cumple todas las condiciones de Tipo 3 (Regular)")
            self.explanation.append("\nJustificación detallada:")
            self.explanation.append("Todas las producciones son del tipo A → aB o A → a (forma derecha)")
            self.explanation.append("o del tipo A → Ba o A → a (forma izquierda), donde:")
            self.explanation.append("- A es un símbolo no terminal")
            self.explanation.append("- a es un símbolo terminal")
            self.explanation.append("- B es un símbolo no terminal")
            self.explanation.append("\nProducciones analizadas:")
            for left, bodies in self.productions.items():
                for body in bodies:
                    if body not in ['ε', 'λ', '']:
                        # Verificar forma
                        nts = []
                        for nt in self.non_terminals:
                            if nt in body:
                                nts.append(nt)
                        if len(nts) == 0:
                            self.explanation.append(f"  {left} → {body} ✓ (A → a)")
                        elif len(nts) == 1:
                            nt = nts[0]
                            if body.endswith(nt):
                                self.explanation.append(f"  {left} → {body} ✓ (A → aB)")
                            elif body.startswith(nt):
                                self.explanation.append(f"  {left} → {body} ✓ (A → Ba)")
                            else:
                                self.explanation.append(f"  {left} → {body} ✓")
                        else:
                            self.explanation.append(f"  {left} → {body} ✓")
        
        return is_regular
    
    def _has_multiple_nonterminals(self, left: str) -> bool:
        """
        Verifica si el lado izquierdo contiene múltiples símbolos (terminales o no terminales).
        
        Para Tipo 2, el lado izquierdo debe ser UN SOLO no terminal.
        Cualquier cosa que no sea un solo no terminal invalida Tipo 2.
        
        Detecta casos como:
        - "AB", "ABC", "CB" (múltiples no terminales)
        - "aB", "Ca", "ACaB" (terminales mezclados con no terminales)
        - "AB CD" (múltiples símbolos con espacios)
        
        Args:
            left: Lado izquierdo de la producción
            
        Returns:
            True si contiene múltiples símbolos, False si es un solo no terminal
        """
        # Si tiene espacios, claramente tiene múltiples símbolos
        if len(left.split()) > 1:
            return True
        
        # Un solo no terminal válido es: [A-Z][a-zA-Z0-9]*
        # Patrón: empieza con mayúscula, seguido opcionalmente de minúsculas/números
        
        # Verificar si es exactamente un solo no terminal
        if re.match(r'^[A-Z][a-zA-Z0-9]*$', left):
            # Es un patrón válido de no terminal, pero necesitamos verificar
            # si realmente es UN SOLO no terminal o múltiples concatenados
            
            # Contar letras mayúsculas consecutivas al inicio
            uppercase_count = 0
            for char in left:
                if char.isupper():
                    uppercase_count += 1
                else:
                    break
            
            # Si hay más de una mayúscula consecutiva, son múltiples no terminales
            # Ejemplos: "AB" (2 mayúsculas), "CB" (2 mayúsculas), "ABC" (3 mayúsculas)
            if uppercase_count > 1:
                return True
            
            # Si tiene una mayúscula seguida de minúsculas/números, es un solo no terminal
            # Ejemplos: "S", "A1", "Bx", "State"
            # Pero si después de las minúsculas hay otra mayúscula, son múltiples
            # Ejemplo: "AaB" sería múltiples (A, a, B)
            if len(left) > 1:
                # Buscar si hay otra mayúscula después de minúsculas/números
                for i in range(1, len(left)):
                    if left[i].isupper():
                        # Hay otra mayúscula, son múltiples símbolos
                        return True
        else:
            # No coincide con el patrón de un solo no terminal
            # Puede ser:
            # - Terminales mezclados: "aB", "Ca", "ab"
            # - Múltiples símbolos: "ACaB", "aBC"
            # - Caracteres especiales
            return True
        
        return False
    
    def _is_type_2(self) -> bool:
        """
        Verifica si la gramática es Tipo 2 (Libre de Contexto).
        
        Tipo 2: Forma A → α donde A es un solo símbolo no terminal
        
        Returns:
            True si es Tipo 2, False en caso contrario
        """
        self.explanation.append("\n--- Verificando Tipo 2 (Libre de Contexto) ---")
        
        is_cf = True
        violations = []
        
        for left, bodies in self.productions.items():
            # Verificar que el lado izquierdo sea un solo símbolo no terminal
            # Primero verificar si tiene espacios (múltiples símbolos separados)
            if len(left.split()) > 1:
                is_cf = False
                violations.append({
                    'production': f"{left} → ...",
                    'reason': f"El lado izquierdo contiene múltiples símbolos separados por espacios: '{left}'"
                })
                self.problematic_productions.append(f"{left} → ...")
                continue
            
            # Verificar si contiene múltiples no terminales concatenados (ej: "AB", "ABC")
            if self._has_multiple_nonterminals(left):
                is_cf = False
                violations.append({
                    'production': f"{left} → ...",
                    'reason': f"El lado izquierdo contiene múltiples símbolos no terminales: '{left}' (ej: AB, ABC)"
                })
                self.problematic_productions.append(f"{left} → ...")
                continue
            
            # Verificar que sea un no terminal válido
            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', left):
                is_cf = False
                violations.append({
                    'production': f"{left} → ...",
                    'reason': f"'{left}' no es un símbolo no terminal válido"
                })
                self.problematic_productions.append(f"{left} → ...")
                continue
        
        if violations:
            self.violations.extend(violations)
            self.explanation.append(f"✗ No es Tipo 2. Violaciones encontradas: {len(violations)}")
            for v in violations:
                self.explanation.append(f"  - {v['production']}: {v['reason']}")
        else:
            self.explanation.append("✓ Cumple todas las condiciones de Tipo 2 (Libre de Contexto)")
            self.explanation.append("\nLa gramática cumple todas las reglas de una GLC:")
            self.explanation.append("\n1. Cada producción tiene exactamente un símbolo no terminal en el lado izquierdo")
            self.explanation.append("\nProducciones analizadas:")
            for left, bodies in self.productions.items():
                for body in bodies:
                    self.explanation.append(f"  {left} → {body}")
            self.explanation.append("\nTodas respetan la forma A → β, donde A es un solo no terminal.")
            self.explanation.append("\n2. No se requiere ningún límite en la estructura del lado derecho")
            self.explanation.append("   Aquí pueden aparecer terminales, no terminales o ambos, sin restricción.")
            self.explanation.append("\n3. No hay producciones que rompan el requisito del lado izquierdo simple")
            self.explanation.append("   No aparece algo como AB → aB")
            self.explanation.append("   No aparece algo como Aa → b")
            
            # Verificar si NO es Tipo 3
            self.explanation.append("\nPor lo tanto, la gramática pertenece al Tipo 2, pero NO al Tipo 3 porque:")
            for left, bodies in self.productions.items():
                for body in bodies:
                    if body not in ['ε', 'λ', '']:
                        # Verificar si es regular
                        nts = []
                        for nt in self.non_terminals:
                            if nt in body:
                                nts.append(nt)
                        if len(nts) > 1:
                            self.explanation.append(f"  {left} → {body} no cumple la forma A → aB ni A → a (tiene múltiples no terminales)")
                        elif len(nts) == 1:
                            nt = nts[0]
                            if not (body.endswith(nt) or body.startswith(nt)):
                                self.explanation.append(f"  {left} → {body} no cumple la forma A → aB ni A → a (no terminal en medio)")
        
        return is_cf
    
    def _is_type_1(self) -> bool:
        """
        Verifica si la gramática es Tipo 1 (Sensible al Contexto).
        
        Tipo 1: Forma αAβ → αγβ donde:
        - α, β son cadenas de terminales y no terminales (pueden ser vacías)
        - A es un símbolo no terminal
        - γ es una cadena no vacía (|γ| >= 1)
        - Excepción: S → ε está permitida si S no aparece en el lado derecho
        
        Returns:
            True si es Tipo 1, False en caso contrario
        """
        self.explanation.append("\n--- Verificando Tipo 1 (Sensible al Contexto) ---")
        
        is_cs = True
        violations = []
        
        # Verificar si S → ε está presente y si S aparece en el lado derecho
        has_epsilon_start = False
        start_in_right_side = False
        
        for left, bodies in self.productions.items():
            for body in bodies:
                if left == self.start_symbol and body in ['ε', 'λ', '']:
                    has_epsilon_start = True
                # Verificar si el símbolo inicial aparece en el lado derecho
                if self.start_symbol in body:
                    start_in_right_side = True
        
        if has_epsilon_start and start_in_right_side:
            is_cs = False
            violations.append({
                'production': f"{self.start_symbol} → ε",
                'reason': "S → ε no está permitida cuando S aparece en el lado derecho"
            })
        
        # Verificar cada producción
        for left, bodies in self.productions.items():
            for body in bodies:
                # Permitir S → ε si no viola la regla anterior
                if left == self.start_symbol and body in ['ε', 'λ', '']:
                    if not start_in_right_side:
                        continue
                
                # Verificar que |right| >= |left| (excepto para S → ε)
                if len(body) < len(left):
                    is_cs = False
                    violations.append({
                        'production': f"{left} → {body}",
                        'reason': f"|{body}| < |{left}|, viola la condición de no contracción"
                    })
                    self.problematic_productions.append(f"{left} → {body}")
                    continue
        
        if violations:
            self.violations.extend(violations)
            self.explanation.append(f"✗ No es Tipo 1. Violaciones encontradas: {len(violations)}")
            for v in violations:
                self.explanation.append(f"  - {v['production']}: {v['reason']}")
        else:
            self.explanation.append("✓ Cumple todas las condiciones de Tipo 1 (Sensible al Contexto)")
            self.explanation.append("\nLa gramática pertenece al Tipo 1 por estas razones:")
            
            # Verificar si hay producciones con múltiples símbolos a la izquierda
            has_multi_left = False
            multi_left_productions = []
            for left, bodies in self.productions.items():
                if len(left) > 1 or not re.match(r'^[A-Z][a-zA-Z0-9]*$', left):
                    has_multi_left = True
                    multi_left_productions.append(left)
            
            if has_multi_left:
                self.explanation.append("\n1. Existe al menos una producción donde el lado izquierdo tiene más de un símbolo no terminal")
                for left in multi_left_productions:
                    bodies = self.productions[left]
                    for body in bodies:
                        self.explanation.append(f"   {left} → {body}")
                self.explanation.append("   Esta forma NO es válida para Tipo 2, ya que viola la estructura A → β.")
            
            self.explanation.append("\n2. La gramática respeta la condición de crecimiento o mantenimiento de longitud")
            self.explanation.append("   |α| ≤ |β| (el lado derecho debe ser igual o mayor que el izquierdo)")
            self.explanation.append("\nLas demás reglas:")
            for left, bodies in self.productions.items():
                for body in bodies:
                    if body in ['ε', 'λ', '']:
                        if left == self.start_symbol:
                            self.explanation.append(f"  {left} → ε (permitida para símbolo inicial)")
                        else:
                            self.explanation.append(f"  {left} → ε (NO permitida en Tipo 1)")
                    else:
                        left_len = len(left)
                        body_len = len(body)
                        if body_len >= left_len:
                            self.explanation.append(f"  {left} → {body} → |{left}|={left_len} ≤ |{body}|={body_len} (crece o igual, permitido) ✓")
                        else:
                            self.explanation.append(f"  {left} → {body} → |{left}|={left_len} > |{body}|={body_len} (reduce, NO permitido) ✗")
            
            self.explanation.append("\nNO contiene reducciones prohibidas del tipo:")
            self.explanation.append("  A → ε (excepto casos especiales)")
            self.explanation.append("  AB → A")
            self.explanation.append("Ninguna producción reduce el tamaño de la cadena.")
            
            if has_multi_left:
                self.explanation.append("\n3. Por el punto (1), NO puede ser Tipo 2")
                self.explanation.append("   Tipo 2 requiere un único no terminal a la izquierda.")
                self.explanation.append(f"   Aquí la regla {multi_left_productions[0]} → ... invalida completamente que sea GLC.")
        
        return is_cs
    
    def _is_terminal_string(self, s: str) -> bool:
        """
        Verifica si una cadena contiene solo símbolos terminales.
        
        Args:
            s: Cadena a verificar
            
        Returns:
            True si contiene solo terminales, False en caso contrario
        """
        if not s:
            return True
        
        # Buscar no terminales (letras mayúsculas seguidas de letras/números)
        # Un no terminal es una letra mayúscula seguida opcionalmente de letras/números
        nt_pattern = r'[A-Z][a-zA-Z0-9]*'
        nts = re.findall(nt_pattern, s)
        
        # Si encontramos algún no terminal, no es una cadena de solo terminales
        if nts:
            return False
        
        # Verificar que no haya caracteres especiales que puedan ser problemáticos
        # Permitir letras minúsculas, dígitos, y algunos símbolos comunes
        # Rechazar letras mayúsculas solas (que serían no terminales)
        for char in s:
            if char.isupper():
                return False
        
        return True
    
    def get_explanation(self) -> List[str]:
        """
        Obtiene la explicación completa de la clasificación.
        
        Returns:
            Lista de strings con la explicación paso a paso
        """
        return self.explanation.copy()
    
    def get_violations(self) -> List[Dict]:
        """
        Obtiene la lista de violaciones encontradas.
        
        Returns:
            Lista de diccionarios con información de violaciones
        """
        return self.violations.copy()
    
    def get_problematic_productions(self) -> List[str]:
        """
        Obtiene la lista de producciones problemáticas.
        
        Returns:
            Lista de producciones que violan restricciones
        """
        return self.problematic_productions.copy()
    
    def get_classification(self) -> Optional[ChomskyType]:
        """
        Obtiene la clasificación de la gramática.
        
        Returns:
            Tipo de Chomsky o None si no se ha clasificado
        """
        return self.classification
    
    def analyze_production_for_type(self, left: str, body: str, target_type: ChomskyType) -> Dict:
        """
        Analiza una producción específica para un tipo de Chomsky.
        
        Args:
            left: Lado izquierdo de la producción
            body: Cuerpo de la producción
            target_type: Tipo de Chomsky a verificar
            
        Returns:
            Diccionario con el análisis
        """
        analysis = {
            'production': f"{left} → {body}",
            'target_type': target_type.value,
            'complies': False,
            'reasons': []
        }
        
        if target_type == ChomskyType.TYPE_3:
            # Verificar forma regular
            nts = re.findall(r'[A-Z][a-zA-Z0-9]*', body)
            if len(nts) <= 1:
                analysis['complies'] = True
                analysis['reasons'].append("Cumple con la forma regular")
            else:
                analysis['reasons'].append(f"Contiene {len(nts)} símbolos no terminales (máximo 1 permitido)")
        
        elif target_type == ChomskyType.TYPE_2:
            # Verificar que el lado izquierdo sea un solo no terminal
            if len(left.split()) == 1 and re.match(r'^[A-Z][a-zA-Z0-9]*$', left):
                analysis['complies'] = True
                analysis['reasons'].append("Lado izquierdo es un solo símbolo no terminal")
            else:
                analysis['reasons'].append("Lado izquierdo no es un solo símbolo no terminal")
        
        elif target_type == ChomskyType.TYPE_1:
            # Verificar condición de no contracción
            if len(body) >= len(left) or (left == self.start_symbol and body in ['ε', 'λ', '']):
                analysis['complies'] = True
                analysis['reasons'].append("Cumple con la condición de no contracción")
            else:
                analysis['reasons'].append(f"|{body}| < |{left}|, viola condición de no contracción")
        
        return analysis


def classify_grammar(grammar_text: str) -> Tuple[Optional[ChomskyType], List[str], GrammarParser]:
    """
    Clasifica una gramática desde texto.
    
    Args:
        grammar_text: Texto con la gramática
        
    Returns:
        Tupla (tipo, explicación, parser)
    """
    parser = GrammarParser()
    if not parser.parse(grammar_text):
        return None, parser.get_errors(), parser
    
    classifier = GrammarClassifier(parser)
    chomsky_type = classifier.classify()
    explanation = classifier.get_explanation()
    
    return chomsky_type, explanation, parser


# Ejemplos de uso
if __name__ == "__main__":
    # Ejemplo 1: Tipo 3 (Regular)
    print("="*60)
    print("EJEMPLO 1: Gramática Regular (Tipo 3)")
    print("="*60)
    grammar1 = """
    S → aA
    A → bB | b
    B → a
    """
    
    type1, expl1, parser1 = classify_grammar(grammar1)
    if type1:
        print(f"\nClasificación: {type1.value}\n")
        print("Explicación:")
        for line in expl1:
            print(f"  {line}")
    
    # Ejemplo 2: Tipo 2 (Libre de Contexto)
    print("\n" + "="*60)
    print("EJEMPLO 2: Gramática Libre de Contexto (Tipo 2)")
    print("="*60)
    grammar2 = """
    S → aSb | ab
    """
    
    type2, expl2, parser2 = classify_grammar(grammar2)
    if type2:
        print(f"\nClasificación: {type2.value}\n")
        print("Explicación:")
        for line in expl2:
            print(f"  {line}")
    
    # Ejemplo 3: Tipo 1 (Sensible al Contexto)
    print("\n" + "="*60)
    print("EJEMPLO 3: Gramática Sensible al Contexto (Tipo 1)")
    print("="*60)
    grammar3 = """
    S → aSBC | aBC
    CB → BC
    aB → ab
    bB → bb
    """
    
    type3, expl3, parser3 = classify_grammar(grammar3)
    if type3:
        print(f"\nClasificación: {type3.value}\n")
        print("Explicación:")
        for line in expl3:
            print(f"  {line}")

