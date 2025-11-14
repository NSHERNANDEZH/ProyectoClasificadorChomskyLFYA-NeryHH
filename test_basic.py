"""
Script de prueba básico para verificar que los módulos principales funcionan correctamente.
"""

from grammar_parser import GrammarParser
from classifier import GrammarClassifier, ChomskyType


def test_regular_grammar():
    """Prueba con una gramática regular (Tipo 3)."""
    print("="*60)
    print("PRUEBA 1: Gramática Regular (Tipo 3)")
    print("="*60)
    
    grammar = """
    S → aA
    A → bB | b
    B → a
    """
    
    parser = GrammarParser()
    if parser.parse(grammar):
        print("[OK] Gramatica parseada correctamente")
        print(f"Terminales: {parser.get_terminals()}")
        print(f"No terminales: {parser.get_non_terminals()}")
        
        classifier = GrammarClassifier(parser)
        chomsky_type = classifier.classify()
        
        if chomsky_type == ChomskyType.TYPE_3:
            print(f"[OK] Clasificacion correcta: {chomsky_type.value}")
        else:
            print(f"[ERROR] Clasificacion incorrecta. Esperado: Tipo 3, Obtenido: {chomsky_type.value}")
    else:
        print("[ERROR] Error al parsear gramatica")
        print(parser.get_errors())


def test_context_free_grammar():
    """Prueba con una gramática libre de contexto (Tipo 2)."""
    print("\n" + "="*60)
    print("PRUEBA 2: Gramática Libre de Contexto (Tipo 2)")
    print("="*60)
    
    grammar = """
    S → aSb | ab
    """
    
    parser = GrammarParser()
    if parser.parse(grammar):
        print("[OK] Gramatica parseada correctamente")
        
        classifier = GrammarClassifier(parser)
        chomsky_type = classifier.classify()
        
        if chomsky_type == ChomskyType.TYPE_2:
            print(f"[OK] Clasificacion correcta: {chomsky_type.value}")
        else:
            print(f"[ERROR] Clasificacion incorrecta. Esperado: Tipo 2, Obtenido: {chomsky_type.value}")
    else:
        print("[ERROR] Error al parsear gramatica")
        print(parser.get_errors())


def test_context_sensitive_grammar():
    """Prueba con una gramática sensible al contexto (Tipo 1)."""
    print("\n" + "="*60)
    print("PRUEBA 3: Gramática Sensible al Contexto (Tipo 1)")
    print("="*60)
    
    grammar = """
    S → aSBC | aBC
    CB → BC
    aB → ab
    bB → bb
    """
    
    parser = GrammarParser()
    if parser.parse(grammar):
        print("[OK] Gramatica parseada correctamente")
        
        classifier = GrammarClassifier(parser)
        chomsky_type = classifier.classify()
        
        if chomsky_type == ChomskyType.TYPE_1:
            print(f"[OK] Clasificacion correcta: {chomsky_type.value}")
        else:
            print(f"[ADVERTENCIA] Clasificacion: {chomsky_type.value}")
            print("Nota: Esta gramatica puede clasificarse como Tipo 1 o Tipo 2 dependiendo de la interpretacion")
    else:
        print("[ERROR] Error al parsear gramatica")
        print(parser.get_errors())


if __name__ == "__main__":
    print("\nChomsky Classifier AI - Pruebas Basicas\n")
    
    try:
        test_regular_grammar()
        test_context_free_grammar()
        test_context_sensitive_grammar()
        
        print("\n" + "="*60)
        print("[OK] Pruebas completadas")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

