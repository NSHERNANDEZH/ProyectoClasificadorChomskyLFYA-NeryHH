"""
Módulo generador de reportes PDF.

Genera reportes completos en formato PDF que incluyen:
- Gramática/autómata analizado
- Clasificación y explicación
- Diagramas visuales
- Observaciones adicionales
- Fecha y hora del análisis
"""

from datetime import datetime
from typing import Dict, List, Optional
import os

# Verificar si reportlab está instalado
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ADVERTENCIA: reportlab no está instalado. La generación de PDFs no estará disponible.")
    print("Para instalar: pip install reportlab")

from grammar_parser import GrammarParser
from classifier import GrammarClassifier, ChomskyType
from automata_analyzer import AutomatonAnalyzer, AutomatonType


class PDFReporter:
    """
    Generador de reportes PDF para análisis de gramáticas y autómatas.
    """
    
    def __init__(self, output_path: str = "reporte.pdf"):
        """
        Inicializa el generador de reportes.
        
        Args:
            output_path: Ruta del archivo PDF de salida
        """
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el reporte."""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Texto de código
        self.styles.add(ParagraphStyle(
            name='CodeStyle',
            parent=self.styles['Code'],
            fontSize=10,
            fontName='Courier',
            leftIndent=20,
            rightIndent=20,
            backColor=colors.HexColor('#f5f5f5')
        ))
    
    def generate_grammar_report(self, grammar_text: str, parser: GrammarParser, 
                                classifier: GrammarClassifier, 
                                diagram_paths: Optional[Dict[str, str]] = None) -> str:
        """
        Genera un reporte PDF para una gramática analizada.
        
        Args:
            grammar_text: Texto de la gramática original
            parser: GrammarParser con la gramática parseada
            classifier: GrammarClassifier con la clasificación
            diagram_paths: Diccionario con rutas de diagramas (opcional)
            
        Returns:
            Ruta del archivo PDF generado
            
        Raises:
            ImportError: Si reportlab no está instalado
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab no está instalado. "
                "Por favor ejecuta: pip install reportlab"
            )
        
        doc = SimpleDocTemplate(self.output_path, pagesize=A4)
        story = []
        
        # Título
        story.append(Paragraph("Reporte de Análisis de Gramática", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Información de fecha y hora
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        story.append(Paragraph(f"<b>Fecha de análisis:</b> {fecha}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Sección: Gramática Original
        story.append(Paragraph("Gramática Analizada", self.styles['CustomHeading2']))
        story.append(Spacer(1, 0.1*inch))
        
        # Mostrar gramática en formato código
        grammar_lines = grammar_text.strip().split('\n')
        for line in grammar_lines:
            if line.strip():
                story.append(Paragraph(f"<font face='Courier'>{line.strip()}</font>", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Sección: Información Básica
        story.append(Paragraph("Información Básica", self.styles['CustomHeading2']))
        
        terminals = parser.get_terminals()
        non_terminals = parser.get_non_terminals()
        start_symbol = parser.get_start_symbol()
        
        info_data = [
            ['Símbolo inicial:', start_symbol or 'N/A'],
            ['Símbolos terminales:', ', '.join(sorted(terminals)) if terminals else 'Ninguno'],
            ['Símbolos no terminales:', ', '.join(sorted(non_terminals))],
            ['Número de producciones:', str(len(parser.get_productions()))]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Sección: Clasificación
        story.append(Paragraph("Clasificación según Jerarquía de Chomsky", self.styles['CustomHeading2']))
        
        chomsky_type = classifier.get_classification()
        if chomsky_type:
            type_info = {
                ChomskyType.TYPE_3: {
                    'name': 'Tipo 3 - Regular',
                    'description': 'Genera lenguajes regulares. Puede ser reconocida por autómatas finitos.',
                    'color': colors.HexColor('#28a745')
                },
                ChomskyType.TYPE_2: {
                    'name': 'Tipo 2 - Libre de Contexto',
                    'description': 'Genera lenguajes libres de contexto. Puede ser reconocida por autómatas de pila.',
                    'color': colors.HexColor('#ffc107')
                },
                ChomskyType.TYPE_1: {
                    'name': 'Tipo 1 - Sensible al Contexto',
                    'description': 'Genera lenguajes sensibles al contexto. Requiere máquinas de Turing lineales acotadas.',
                    'color': colors.HexColor('#fd7e14')
                },
                ChomskyType.TYPE_0: {
                    'name': 'Tipo 0 - Recursivamente Enumerable',
                    'description': 'Genera lenguajes recursivamente enumerables. Requiere máquinas de Turing completas.',
                    'color': colors.HexColor('#dc3545')
                }
            }
            
            info = type_info.get(chomsky_type, {})
            story.append(Paragraph(f"<b>{info.get('name', chomsky_type.value)}</b>", self.styles['Heading3']))
            story.append(Paragraph(info.get('description', ''), self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Sección: Explicación del Proceso
        story.append(Paragraph("Explicación del Proceso de Clasificación", self.styles['CustomHeading2']))
        
        explanation = classifier.get_explanation()
        for line in explanation:
            if line.strip():
                # Formatear según el tipo de línea
                if line.startswith("✓"):
                    story.append(Paragraph(f"<font color='green'>{line}</font>", self.styles['Normal']))
                elif line.startswith("✗"):
                    story.append(Paragraph(f"<font color='red'>{line}</font>", self.styles['Normal']))
                elif line.startswith("---"):
                    story.append(Paragraph(f"<b>{line}</b>", self.styles['Normal']))
                else:
                    story.append(Paragraph(line, self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Sección: Producciones
        story.append(Paragraph("Producciones", self.styles['CustomHeading2']))
        
        productions = parser.get_productions()
        for left, bodies in productions.items():
            bodies_str = " | ".join(bodies)
            story.append(Paragraph(f"<font face='Courier'><b>{left}</b> → {bodies_str}</font>", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Sección: Advertencias y Errores
        warnings = parser.get_warnings()
        violations = classifier.get_violations()
        problematic = classifier.get_problematic_productions()
        
        if warnings or violations or problematic:
            story.append(Paragraph("Advertencias y Observaciones", self.styles['CustomHeading2']))
            
            if warnings:
                story.append(Paragraph("<b>Advertencias:</b>", self.styles['Normal']))
                for warning in warnings:
                    story.append(Paragraph(f"• {warning}", self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            if violations:
                story.append(Paragraph("<b>Violaciones de restricciones:</b>", self.styles['Normal']))
                for violation in violations:
                    story.append(Paragraph(f"• <b>{violation['production']}</b>: {violation['reason']}", self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            if problematic:
                story.append(Paragraph("<b>Producciones problemáticas:</b>", self.styles['Normal']))
                for prod in problematic:
                    story.append(Paragraph(f"• {prod}", self.styles['Normal']))
        
        # Agregar diagramas si están disponibles
        if diagram_paths:
            story.append(PageBreak())
            story.append(Paragraph("Diagramas Visuales", self.styles['CustomHeading2']))
            
            for diagram_name, diagram_path in diagram_paths.items():
                if os.path.exists(diagram_path):
                    story.append(Paragraph(f"<b>{diagram_name}</b>", self.styles['Heading3']))
                    try:
                        img = Image(diagram_path, width=5*inch, height=3.75*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))
                    except Exception as e:
                        story.append(Paragraph(f"Error al cargar diagrama: {str(e)}", self.styles['Normal']))
        
        # Pie de página
        story.append(PageBreak())
        story.append(Paragraph("Chomsky Classifier AI", self.styles['CustomTitle']))
        story.append(Paragraph("Sistema de Clasificación de Gramáticas Formales", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Desarrollado para el curso de Lenguajes y Autómatas", self.styles['Normal']))
        
        # Generar PDF
        doc.build(story)
        return self.output_path
    
    def generate_automaton_report(self, automaton_definition: Dict, analyzer: AutomatonAnalyzer,
                                  diagram_path: Optional[str] = None) -> str:
        """
        Genera un reporte PDF para un autómata analizado.
        
        Args:
            automaton_definition: Definición del autómata
            analyzer: AutomatonAnalyzer con el análisis
            diagram_path: Ruta del diagrama (opcional)
            
        Returns:
            Ruta del archivo PDF generado
            
        Raises:
            ImportError: Si reportlab no está instalado
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab no está instalado. "
                "Por favor ejecuta: pip install reportlab"
            )
        
        doc = SimpleDocTemplate(self.output_path, pagesize=A4)
        story = []
        
        # Título
        story.append(Paragraph("Reporte de Análisis de Autómata", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Información de fecha y hora
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        story.append(Paragraph(f"<b>Fecha de análisis:</b> {fecha}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Sección: Tipo de Autómata
        story.append(Paragraph("Tipo de Autómata", self.styles['CustomHeading2']))
        
        automaton_type = analyzer.get_automaton_type()
        if automaton_type:
            story.append(Paragraph(f"<b>{automaton_type.value}</b>", self.styles['Heading3']))
        
        analysis = analyzer.get_analysis()
        if 'chomsky_type' in analysis:
            story.append(Paragraph(f"<b>Clasificación Chomsky:</b> {analysis['chomsky_type']}", self.styles['Normal']))
        if 'computational_power' in analysis:
            story.append(Paragraph(f"<b>Poder de cómputo:</b> {analysis['computational_power']}", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Sección: Información del Autómata
        story.append(Paragraph("Información del Autómata", self.styles['CustomHeading2']))
        
        info_data = [
            ['Estados:', str(len(automaton_definition.get('states', set())))],
            ['Alfabeto:', ', '.join(sorted(automaton_definition.get('alphabet', set())))],
            ['Estado inicial:', automaton_definition.get('initial_state', 'N/A')],
            ['Estados finales:', ', '.join(sorted(automaton_definition.get('final_states', set())))],
            ['Número de transiciones:', str(len(automaton_definition.get('transitions', [])))],
        ]
        
        if 'num_reachable_states' in analysis:
            info_data.append(['Estados alcanzables:', str(analysis['num_reachable_states'])])
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Sección: Advertencias
        warnings = analyzer.get_warnings()
        errors = analyzer.get_errors()
        
        if warnings or errors:
            story.append(Paragraph("Advertencias y Errores", self.styles['CustomHeading2']))
            
            if errors:
                story.append(Paragraph("<b>Errores:</b>", self.styles['Normal']))
                for error in errors:
                    story.append(Paragraph(f"• <font color='red'>{error}</font>", self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            if warnings:
                story.append(Paragraph("<b>Advertencias:</b>", self.styles['Normal']))
                for warning in warnings:
                    story.append(Paragraph(f"• {warning}", self.styles['Normal']))
        
        # Agregar diagrama si está disponible
        if diagram_path and os.path.exists(diagram_path):
            story.append(PageBreak())
            story.append(Paragraph("Diagrama del Autómata", self.styles['CustomHeading2']))
            try:
                img = Image(diagram_path, width=5*inch, height=3.75*inch)
                story.append(img)
            except Exception as e:
                story.append(Paragraph(f"Error al cargar diagrama: {str(e)}", self.styles['Normal']))
        
        # Pie de página
        story.append(PageBreak())
        story.append(Paragraph("Chomsky Classifier AI", self.styles['CustomTitle']))
        story.append(Paragraph("Sistema de Clasificación de Gramáticas Formales", self.styles['Normal']))
        
        # Generar PDF
        doc.build(story)
        return self.output_path


def generate_grammar_pdf_report(grammar_text: str, output_path: str = "reporte_gramatica.pdf",
                                 diagram_paths: Optional[Dict[str, str]] = None) -> str:
    """
    Función de conveniencia para generar un reporte PDF de gramática.
    
    Args:
        grammar_text: Texto de la gramática
        output_path: Ruta del archivo PDF de salida
        diagram_paths: Diccionario con rutas de diagramas (opcional)
        
    Returns:
        Ruta del archivo PDF generado
    """
    # Parsear y clasificar
    parser = GrammarParser()
    if not parser.parse(grammar_text):
        raise ValueError(f"Error al parsear gramática: {parser.get_errors()}")
    
    classifier = GrammarClassifier(parser)
    classifier.classify()
    
    # Generar reporte
    reporter = PDFReporter(output_path)
    return reporter.generate_grammar_report(grammar_text, parser, classifier, diagram_paths)


# Ejemplos de uso
if __name__ == "__main__":
    # Ejemplo: Generar reporte de gramática
    print("Generando reporte PDF de ejemplo...")
    
    grammar = """
    S → aSb | ab
    """
    
    try:
        pdf_path = generate_grammar_pdf_report(grammar, "ejemplo_reporte.pdf")
        print(f"Reporte generado exitosamente: {pdf_path}")
    except Exception as e:
        print(f"Error al generar reporte: {e}")

