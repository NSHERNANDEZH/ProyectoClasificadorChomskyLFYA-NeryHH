"""
Chomsky Classifier AI - Sistema de Clasificación de Gramáticas Formales

Este paquete proporciona herramientas para analizar, clasificar y visualizar
gramáticas formales según la Jerarquía de Chomsky.
"""

__version__ = "1.0.0"
__author__ = "Chomsky Classifier AI Team"

from grammar_parser import GrammarParser
from classifier import GrammarClassifier, ChomskyType
from visualizer import GrammarVisualizer, AutomatonVisualizer
from automata_analyzer import AutomatonAnalyzer, AutomatonType, analyze_automaton
from automata_parser import AutomataParser
from converter import (
    RegexToAFNConverter,
    AFNToAFDConverter,
    AFDToGrammarConverter,
    regex_to_grammar
)
from example_generator import ExampleGenerator, generate_example
from pdf_reporter import PDFReporter, generate_grammar_pdf_report
from auto_pdf_reporter import AutoPDFReporter, generate_auto_pdf_report
from comparator import GrammarComparator, AutomatonComparator, compare_grammars, compare_automata
from quiz_mode import QuizMode, create_quiz_session

__all__ = [
    'GrammarParser',
    'GrammarClassifier',
    'ChomskyType',
    'GrammarVisualizer',
    'AutomatonVisualizer',
    'AutomatonAnalyzer',
    'AutomatonType',
    'analyze_automaton',
    'AutomataParser',
    'RegexToAFNConverter',
    'AFNToAFDConverter',
    'AFDToGrammarConverter',
    'regex_to_grammar',
    'ExampleGenerator',
    'generate_example',
    'PDFReporter',
    'generate_grammar_pdf_report',
    'AutoPDFReporter',
    'generate_auto_pdf_report',
    'GrammarComparator',
    'AutomatonComparator',
    'compare_grammars',
    'compare_automata',
    'QuizMode',
    'create_quiz_session'
]

