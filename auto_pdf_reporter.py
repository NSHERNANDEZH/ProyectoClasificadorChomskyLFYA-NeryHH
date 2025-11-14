"""
Módulo de Generación Automática de Reportes PDF.

Este módulo genera automáticamente reportes PDF completos después de cada análisis,
incluyendo:
- Fecha y hora del análisis
- Gramática/autómata analizado
- Tipo de lenguaje detectado
- Justificación paso a paso
- Diagramas visuales (si aplica)
- Información adicional relevante

Usa reportlab para la generación de PDFs profesionales.
"""

from datetime import datetime
from typing import Dict, Optional
import os

# Verificar si reportlab está instalado
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
        Table, TableStyle, Image
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ADVERTENCIA: reportlab no está instalado. La generación de PDFs no estará disponible.")
    print("Para instalar: pip install reportlab")

from grammar_parser import GrammarParser, parse_grammar_from_text
from classifier import GrammarClassifier, ChomskyType
from visualizer import visualize_grammar_from_text


class AutoPDFReporter:
    """
    Generador automático de reportes PDF para análisis de gramáticas y autómatas.
    
    Genera reportes completos y profesionales con toda la información del análisis.
    """
    
    def __init__(self, output_dir: str = "reportes"):
        """
        Inicializa el generador automático de reportes.
        
        Args:
            output_dir: Directorio donde se guardarán los reportes
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
        else:
            self.styles = None
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para los reportes."""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=20,
            spaceBefore=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo de sección
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#e0e0e0'),
            borderPadding=8,
            backColor=colors.HexColor('#f5f5f5')
        ))
        
        # Texto de código/gramática
        self.styles.add(ParagraphStyle(
            name='CodeText',
            parent=self.styles['Code'],
            fontSize=11,
            fontName='Courier',
            leftIndent=15,
            rightIndent=15,
            backColor=colors.HexColor('#fafafa'),
            borderWidth=1,
            borderColor=colors.HexColor('#e0e0e0'),
            borderPadding=8
        ))
        
        # Texto de explicación
        self.styles.add(ParagraphStyle(
            name='ExplanationText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leftIndent=10
        ))
        
        # Texto de fecha/hora
        self.styles.add(ParagraphStyle(
            name='DateTimeText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_RIGHT,
            spaceAfter=15
        ))
    
    def _add_header_footer(self, canvas_obj, doc):
        """Agrega encabezado y pie de página al PDF."""
        canvas_obj.saveState()
        
        # Encabezado
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(colors.HexColor('#666666'))
        canvas_obj.drawString(2*cm, A4[1] - 1.5*cm, "Chomsky Classifier AI - Reporte de Análisis")
        
        # Pie de página
        page_num = canvas_obj.getPageNumber()
        canvas_obj.drawString(A4[0] - 4*cm, 1*cm, f"Página {page_num}")
        
        # Fecha en pie de página
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        canvas_obj.drawString(2*cm, 1*cm, f"Generado: {fecha}")
        
        canvas_obj.restoreState()
    
    def generate_grammar_report_auto(self, grammar_text: str, 
                                     include_diagrams: bool = True) -> str:
        """
        Genera automáticamente un reporte PDF completo para una gramática.
        
        Este método parsea, clasifica y genera el reporte automáticamente.
        
        Args:
            grammar_text: Texto de la gramática a analizar
            include_diagrams: Si True, incluye diagramas visuales
            
        Returns:
            Ruta del archivo PDF generado
            
        Raises:
            ImportError: Si reportlab no está instalado
            ValueError: Si hay errores al parsear la gramática
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab no está instalado. "
                "Por favor ejecuta: pip install reportlab"
            )
        
        # Parsear y clasificar automáticamente
        parser, errors = parse_grammar_from_text(grammar_text)
        if parser is None:
            raise ValueError(f"Error al parsear gramática: {errors}")
        
        classifier = GrammarClassifier(parser)
        chomsky_type = classifier.classify()
        
        # Generar diagramas si se solicitan
        diagram_paths = {}
        if include_diagrams:
            try:
                viz_results = visualize_grammar_from_text(grammar_text, output_dir="output")
                if 'dependencies' in viz_results:
                    diagram_paths['Grafo de Dependencias'] = viz_results['dependencies']
                if 'structure' in viz_results:
                    diagram_paths['Estructura de Producciones'] = viz_results['structure']
            except Exception as e:
                print(f"Advertencia: No se pudieron generar diagramas: {e}")
        
        # Generar nombre de archivo único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_gramatica_{timestamp}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        # Generar el reporte
        return self._generate_grammar_report_content(
            grammar_text, parser, classifier, chomsky_type, 
            diagram_paths, output_path
        )
    
    def _generate_grammar_report_content(self, grammar_text: str,
                                        parser: GrammarParser,
                                        classifier: GrammarClassifier,
                                        chomsky_type: ChomskyType,
                                        diagram_paths: Dict[str, str],
                                        output_path: str) -> str:
        """
        Genera el contenido completo del reporte PDF de gramática.
        
        Args:
            grammar_text: Texto de la gramática
            parser: GrammarParser con la gramática parseada
            classifier: GrammarClassifier con la clasificación
            chomsky_type: Tipo de Chomsky detectado
            diagram_paths: Diccionario con rutas de diagramas
            output_path: Ruta del archivo PDF de salida
            
        Returns:
            Ruta del archivo PDF generado
        """
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # ========== PORTADA ==========
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("Reporte de Análisis", self.styles['ReportTitle']))
        story.append(Paragraph("de Gramática Formal", self.styles['ReportTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Fecha y hora
        fecha_hora = datetime.now().strftime("%d de %B de %Y, %H:%M:%S")
        story.append(Paragraph(f"<i>{fecha_hora}</i>", self.styles['DateTimeText']))
        story.append(Spacer(1, 1*inch))
        
        # Información del tipo detectado
        type_info = self._get_type_info(chomsky_type)
        story.append(Paragraph(
            f"<b>Tipo Detectado:</b> {chomsky_type.value}",
            self.styles['SectionHeading']
        ))
        story.append(Paragraph(type_info['description'], self.styles['Normal']))
        
        story.append(PageBreak())
        
        # ========== GRAMÁTICA ORIGINAL ==========
        story.append(Paragraph("Gramática Analizada", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.2*inch))
        
        # Mostrar gramática en formato código
        grammar_lines = [l.strip() for l in grammar_text.strip().split('\n') if l.strip()]
        grammar_formatted = [f"<font face='Courier' size='11'>{self._escape_html(l)}</font>" for l in grammar_lines]
        story.append(Paragraph("<br/>".join(grammar_formatted), self.styles['CodeText']))
        story.append(Spacer(1, 0.3*inch))
        
        # ========== INFORMACIÓN BÁSICA ==========
        story.append(Paragraph("Información Básica", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.2*inch))
        
        terminals = parser.get_terminals()
        non_terminals = parser.get_non_terminals()
        start_symbol = parser.get_start_symbol()
        productions = parser.get_productions()
        
        info_data = [
            ['<b>Símbolo inicial:</b>', start_symbol or 'N/A'],
            ['<b>Símbolos terminales:</b>', ', '.join(sorted(terminals)) if terminals else 'Ninguno'],
            ['<b>Símbolos no terminales:</b>', ', '.join(sorted(non_terminals))],
            ['<b>Número de producciones:</b>', str(len(productions))],
            ['<b>Tipo de lenguaje:</b>', chomsky_type.value],
            ['<b>Máquina equivalente:</b>', type_info['machine']],
            ['<b>Poder de cómputo:</b>', type_info['power']]
        ]
        
        info_table = Table(info_data, colWidths=[3*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdbdbd'))
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ========== CLASIFICACIÓN DETALLADA ==========
        story.append(Paragraph("Clasificación según Jerarquía de Chomsky", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            f"<b>Tipo Detectado:</b> {chomsky_type.value}",
            self.styles['Heading3']
        ))
        story.append(Paragraph(type_info['description'], self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(
            f"<b>Máquina equivalente:</b> {type_info['machine']}",
            self.styles['Normal']
        ))
        story.append(Paragraph(
            f"<b>Poder de cómputo:</b> {type_info['power']}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # ========== JUSTIFICACIÓN PASO A PASO ==========
        story.append(Paragraph("Justificación del Resultado", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            "<b>Explicación detallada del proceso de clasificación:</b>",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.1*inch))
        
        explanation = classifier.get_explanation()
        for line in explanation:
            if not line.strip():
                continue
            
            safe_line = self._escape_html(line)
            # Formatear según el tipo de línea
            if line.startswith("✓") or "[OK]" in line:
                story.append(Paragraph(f"<font color='green'>{safe_line}</font>", self.styles['ExplanationText']))
            elif line.startswith("✗") or "[ERROR]" in line:
                story.append(Paragraph(f"<font color='red'>{safe_line}</font>", self.styles['ExplanationText']))
            elif line.startswith(("---", "==", "Tipo detectado", "Justificación")):
                story.append(Paragraph(f"<b>{safe_line}</b>", self.styles['ExplanationText']))
            else:
                story.append(Paragraph(safe_line, self.styles['ExplanationText']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # ========== PRODUCCIONES ==========
        story.append(Paragraph("Producciones de la Gramática", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.2*inch))
        
        for left, bodies in productions.items():
            bodies_str = " | ".join(bodies)
            safe_prod = self._escape_html(f"{left} → {bodies_str}")
            story.append(Paragraph(f"<font face='Courier' size='11'>{safe_prod}</font>", self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.3*inch))
        
        # ========== ADVERTENCIAS Y OBSERVACIONES ==========
        warnings = parser.get_warnings()
        violations = classifier.get_violations()
        problematic = classifier.get_problematic_productions()
        
        if warnings or violations or problematic:
            story.append(Paragraph("Advertencias y Observaciones", self.styles['SectionHeading']))
            story.append(Spacer(1, 0.2*inch))
            
            if warnings:
                story.append(Paragraph("<b>Advertencias detectadas:</b>", self.styles['Normal']))
                story.extend([Paragraph(f"• {self._escape_html(w)}", self.styles['Normal']) for w in warnings])
                story.append(Spacer(1, 0.1*inch))
            
            if violations:
                story.append(Paragraph("<b>Violaciones de restricciones:</b>", self.styles['Normal']))
                for v in violations:
                    prod = self._escape_html(v['production'])
                    reason = self._escape_html(v['reason'])
                    story.append(Paragraph(f"• <b>{prod}</b>: {reason}", self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            if problematic:
                story.append(Paragraph("<b>Producciones problemáticas:</b>", self.styles['Normal']))
                story.extend([Paragraph(f"• {self._escape_html(p)}", self.styles['Normal']) for p in problematic])
        
        # ========== DIAGRAMAS VISUALES ==========
        if diagram_paths:
            story.append(PageBreak())
            story.append(Paragraph("Representación Visual", self.styles['SectionHeading']))
            story.append(Spacer(1, 0.2*inch))
            
            for diagram_name, diagram_path in diagram_paths.items():
                if not os.path.exists(diagram_path):
                    continue
                
                story.append(Paragraph(f"<b>{diagram_name}</b>", self.styles['Heading3']))
                story.append(Spacer(1, 0.1*inch))
                try:
                    img = Image(diagram_path, width=14*cm, height=10.5*cm)
                    story.append(img)
                    story.append(Spacer(1, 0.3*inch))
                except Exception as e:
                    story.append(Paragraph(f"Error al cargar diagrama: {str(e)}", self.styles['Normal']))
        
        # ========== PIE DE PÁGINA ==========
        story.append(PageBreak())
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("Chomsky Classifier AI", self.styles['ReportTitle']))
        story.append(Paragraph(
            "Sistema de Clasificación de Gramáticas Formales",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            "Desarrollado para el curso de Lenguajes y Autómatas",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f"Reporte generado automáticamente el {fecha_hora}",
            self.styles['DateTimeText']
        ))
        
        # Generar PDF con encabezado y pie de página
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return output_path
    
    def _get_type_info(self, chomsky_type: ChomskyType) -> Dict[str, str]:
        """
        Obtiene información detallada sobre un tipo de Chomsky.
        
        Args:
            chomsky_type: Tipo de Chomsky
            
        Returns:
            Diccionario con información del tipo
        """
        type_info_map = {
            ChomskyType.TYPE_3: {
                'description': 'Genera lenguajes regulares. Puede ser reconocida por autómatas finitos (AFD/AFN).',
                'machine': 'Autómata Finito (Determinista o No Determinista)',
                'power': 'Menor poder expresivo - Solo puede reconocer lenguajes regulares'
            },
            ChomskyType.TYPE_2: {
                'description': 'Genera lenguajes libres de contexto. Puede ser reconocida por autómatas de pila.',
                'machine': 'Autómata de Pila (Pushdown Automaton)',
                'power': 'Poder expresivo medio - Puede reconocer lenguajes libres de contexto'
            },
            ChomskyType.TYPE_1: {
                'description': 'Genera lenguajes sensibles al contexto. Requiere máquinas de Turing lineales acotadas.',
                'machine': 'Máquina de Turing Lineal Acotada (LBA)',
                'power': 'Alto poder expresivo - Puede reconocer lenguajes sensibles al contexto'
            },
            ChomskyType.TYPE_0: {
                'description': 'Genera lenguajes recursivamente enumerables. Requiere máquinas de Turing completas.',
                'machine': 'Máquina de Turing (Turing Machine)',
                'power': 'Máximo poder expresivo - Puede reconocer cualquier lenguaje recursivamente enumerable'
            }
        }
        
        return type_info_map.get(chomsky_type, {
            'description': 'Tipo desconocido',
            'machine': 'N/A',
            'power': 'N/A'
        })
    
    def _escape_html(self, text: str) -> str:
        """Escapa caracteres especiales HTML."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))


def generate_auto_pdf_report(grammar_text: str, 
                             output_dir: str = "reportes",
                             include_diagrams: bool = True) -> str:
    """
    Función de conveniencia para generar automáticamente un reporte PDF.
    
    Esta función parsea, clasifica y genera el reporte automáticamente.
    
    Args:
        grammar_text: Texto de la gramática a analizar
        output_dir: Directorio donde guardar el reporte
        include_diagrams: Si True, incluye diagramas visuales
        
    Returns:
        Ruta del archivo PDF generado
        
    Example:
        >>> grammar = "S -> aSb | ab"
        >>> pdf_path = generate_auto_pdf_report(grammar)
        >>> print(f"Reporte generado: {pdf_path}")
    """
    reporter = AutoPDFReporter(output_dir)
    return reporter.generate_grammar_report_auto(grammar_text, include_diagrams)


# Ejemplo de uso
if __name__ == "__main__":
    print("Generador Automático de Reportes PDF")
    print("=" * 50)
    
    # Ejemplo de gramática
    grammar = """S -> aSb | ab"""
    
    try:
        pdf_path = generate_auto_pdf_report(grammar, include_diagrams=True)
        print(f"\n[OK] Reporte generado exitosamente:")
        print(f"    {pdf_path}")
    except ImportError as e:
        print(f"\n[ERROR] {e}")
    except Exception as e:
        print(f"\n[ERROR] Error al generar reporte: {e}")

