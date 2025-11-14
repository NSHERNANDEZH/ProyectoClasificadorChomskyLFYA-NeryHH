"""
Módulo Modo Tutor/Quiz Interactivo.

Este módulo implementa un sistema de ejercicios interactivos donde:
- Se generan gramáticas aleatorias
- El usuario debe clasificarlas
- Se compara la respuesta con la correcta
- Se proporciona retroalimentación inmediata
- Se lleva un sistema de puntuación
"""

import random
from typing import Dict, List, Tuple, Optional
from grammar_parser import GrammarParser
from classifier import GrammarClassifier, ChomskyType
from example_generator import generate_example, ExampleGenerator


class QuizMode:
    """
    Modo Quiz/Tutor interactivo para practicar clasificación de gramáticas.
    """
    
    def __init__(self):
        """Inicializa el modo quiz."""
        self.score = 0
        self.total_questions = 0
        self.current_question: Optional[Dict] = None
        self.questions_history: List[Dict] = []
    
    def generate_question(self, difficulty: str = "medium") -> Dict:
        """
        Genera una pregunta aleatoria.
        
        Args:
            difficulty: Nivel de dificultad ("easy", "medium", "hard")
            
        Returns:
            Diccionario con la pregunta generada
        """
        # Seleccionar tipo aleatorio
        types = [ChomskyType.TYPE_3, ChomskyType.TYPE_2, ChomskyType.TYPE_1, ChomskyType.TYPE_0]
        
        if difficulty == "easy":
            # Solo tipos 3 y 2 para principiantes
            types = [ChomskyType.TYPE_3, ChomskyType.TYPE_2]
        elif difficulty == "hard":
            # Incluir todos los tipos
            types = [ChomskyType.TYPE_3, ChomskyType.TYPE_2, ChomskyType.TYPE_1, ChomskyType.TYPE_0]
        
        selected_type = random.choice(types)
        
        # Generar gramática
        complexity_map = {
            "easy": "simple",
            "medium": "medium",
            "hard": "complex"
        }
        complexity = complexity_map.get(difficulty, "medium")
        
        generator = ExampleGenerator()
        grammar, is_valid, explanation = generator.generate_and_validate(selected_type, complexity)
        
        # Si no es válida, intentar generar otra
        attempts = 0
        while not is_valid and attempts < 3:
            selected_type = random.choice(types)
            grammar, is_valid, explanation = generator.generate_and_validate(selected_type, complexity)
            attempts += 1
        
        # Parsear y clasificar para obtener la respuesta correcta
        parser = GrammarParser()
        if parser.parse(grammar):
            classifier = GrammarClassifier(parser)
            correct_answer = classifier.classify()
        else:
            # Si falla el parseo, usar el tipo esperado
            correct_answer = selected_type
        
        question = {
            'grammar': grammar,
            'correct_answer': correct_answer,
            'difficulty': difficulty,
            'explanation': explanation,
            'answered': False,
            'user_answer': None,
            'is_correct': False
        }
        
        self.current_question = question
        return question
    
    def submit_answer(self, user_answer: ChomskyType) -> Dict:
        """
        Procesa la respuesta del usuario.
        
        Args:
            user_answer: Tipo de Chomsky seleccionado por el usuario
            
        Returns:
            Diccionario con el resultado de la respuesta
        """
        if not self.current_question:
            return {'error': 'No hay pregunta activa'}
        
        self.current_question['user_answer'] = user_answer
        self.current_question['answered'] = True
        
        is_correct = (user_answer == self.current_question['correct_answer'])
        self.current_question['is_correct'] = is_correct
        
        if is_correct:
            self.score += 1
        self.total_questions += 1
        
        # Agregar a historial
        self.questions_history.append(self.current_question.copy())
        
        # Generar retroalimentación
        feedback = self._generate_feedback(self.current_question)
        
        return {
            'is_correct': is_correct,
            'correct_answer': self.current_question['correct_answer'],
            'user_answer': user_answer,
            'feedback': feedback,
            'score': self.score,
            'total': self.total_questions,
            'percentage': round((self.score / self.total_questions) * 100, 1) if self.total_questions > 0 else 0
        }
    
    def _generate_feedback(self, question: Dict) -> str:
        """
        Genera retroalimentación para la respuesta del usuario.
        
        Args:
            question: Diccionario con la pregunta y respuesta
            
        Returns:
            String con la retroalimentación
        """
        feedback_parts = []
        
        if question['is_correct']:
            feedback_parts.append("¡Correcto! Has clasificado la gramática correctamente.")
        else:
            feedback_parts.append(f"Incorrecto. La respuesta correcta es: {question['correct_answer'].value}")
            feedback_parts.append(f"Tu respuesta fue: {question['user_answer'].value}")
        
        # Agregar explicación
        if question.get('explanation'):
            feedback_parts.append("\nExplicación:")
            for line in question['explanation'][:5]:  # Primeras 5 líneas
                if line.strip():
                    feedback_parts.append(f"  {line}")
        
        return "\n".join(feedback_parts)
    
    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas del quiz.
        
        Returns:
            Diccionario con estadísticas
        """
        if self.total_questions == 0:
            return {
                'score': 0,
                'total': 0,
                'percentage': 0,
                'correct': 0,
                'incorrect': 0
            }
        
        correct = self.score
        incorrect = self.total_questions - self.score
        
        return {
            'score': self.score,
            'total': self.total_questions,
            'percentage': round((self.score / self.total_questions) * 100, 1),
            'correct': correct,
            'incorrect': incorrect
        }
    
    def reset_quiz(self):
        """Reinicia el quiz."""
        self.score = 0
        self.total_questions = 0
        self.current_question = None
        self.questions_history = []
    
    def get_current_question(self) -> Optional[Dict]:
        """
        Obtiene la pregunta actual.
        
        Returns:
            Diccionario con la pregunta actual o None
        """
        return self.current_question


def create_quiz_session(difficulty: str = "medium") -> QuizMode:
    """
    Función de conveniencia para crear una sesión de quiz.
    
    Args:
        difficulty: Nivel de dificultad
        
    Returns:
        Instancia de QuizMode
    """
    quiz = QuizMode()
    quiz.generate_question(difficulty)
    return quiz


# Ejemplos de uso
if __name__ == "__main__":
    print("="*60)
    print("Modo Quiz - Prueba")
    print("="*60)
    
    quiz = QuizMode()
    question = quiz.generate_question("medium")
    
    print(f"\nGramática a clasificar:")
    print(question['grammar'])
    print(f"\nRespuesta correcta: {question['correct_answer'].value}")
    
    # Simular respuesta del usuario
    user_answer = ChomskyType.TYPE_2
    result = quiz.submit_answer(user_answer)
    
    print(f"\nResultado: {'Correcto' if result['is_correct'] else 'Incorrecto'}")
    print(f"Puntuación: {result['score']}/{result['total']} ({result['percentage']}%)")
    print(f"\nRetroalimentación:")
    print(result['feedback'])

