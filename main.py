"""
Interfaz principal de Chomsky Classifier AI usando Streamlit.

Esta aplicación permite:
- Analizar y clasificar gramáticas formales
- Visualizar gramáticas y autómatas
- Generar reportes explicativos
- Modo tutor interactivo
"""

import streamlit as st
import os
from typing import Optional
from grammar_parser import GrammarParser, parse_grammar_from_text
from classifier import GrammarClassifier, ChomskyType, classify_grammar
from visualizer import GrammarVisualizer, visualize_grammar_from_text
from pdf_reporter import PDFReporter
from comparator import compare_grammars, GrammarComparator
from example_generator import generate_example, ExampleGenerator
from quiz_mode import QuizMode, create_quiz_session
from automata_parser import AutomataParser
from automata_analyzer import analyze_automaton
from converter import regex_to_grammar
from auto_pdf_reporter import AutoPDFReporter, generate_auto_pdf_report


# Configuración de la página 
st.set_page_config(
    page_title="Clasificador de Chomsky IA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("Clasificador de Chomsky IA")
st.markdown("### Sistema Inteligente de Clasificación de Gramáticas Formales")
st.markdown("---")

# Sidebar con opciones
st.sidebar.title("Opciones")
mode = st.sidebar.radio(
    "Modo de operación:",
    ["Clasificador de Gramáticas", "Visualizador", "Comparador", "Generador de Ejemplos", "Modo Quiz/Tutor", "Ejemplos", "Ayuda"]
)

# Modo: Clasificador de Gramáticas
if mode == "Clasificador de Gramáticas":
    st.header("Clasificador de Gramáticas y Autómatas")
    st.markdown("Analiza gramáticas formales, autómatas o expresiones regulares y clasifícalos según la Jerarquía de Chomsky.")
    
    # Dropdown principal: Tipo de entrada
    input_type = st.selectbox(
        "Tipo de entrada:",
        ["Gramática", "Autómata", "Expresión Regular"],
        key="main_input_type"
    )
    
    # Inicializar session_state
    if 'input_text' not in st.session_state:
        st.session_state.input_text = ""
    if 'last_input_type' not in st.session_state:
        st.session_state.last_input_type = input_type
    if 'last_subtype' not in st.session_state:
        st.session_state.last_subtype = ""
    
    # Si cambió el tipo de entrada, resetear
    if input_type != st.session_state.last_input_type:
        st.session_state.input_text = ""
        st.session_state.last_input_type = input_type
        st.session_state.last_subtype = ""
    
    # Ejemplos según el tipo de entrada seleccionado
    if input_type == "Gramática":
        st.subheader("Ingresar Gramática")
        
        # Dropdown secundario: Tipo de gramática
        grammar_type = st.selectbox(
            "Tipo de gramática (ejemplo):",
            ["Seleccionar tipo...", "Tipo 3 - Regular", "Tipo 2 - Libre de Contexto", 
             "Tipo 1 - Sensible al Contexto", "Tipo 0 - Recursivamente Enumerable"],
            key="grammar_type_selector"
        )
        
        # Ejemplos específicos por tipo
        grammar_examples = {
            "Tipo 3 - Regular": """S → aA
A → b""",
            "Tipo 2 - Libre de Contexto": """S → aSb
S → ab""",
            "Tipo 1 - Sensible al Contexto": """S → aSBC | aBC
CB → BC
aB → ab
bB → bb
bC → bc
cC → cc""",
            "Tipo 0 - Recursivamente Enumerable": """S → aSb
S → T
TbA → bb
A → ε"""
        }
        
        # Determinar el valor del text_area
        if grammar_type != "Seleccionar tipo..." and grammar_type in grammar_examples:
            default_text = grammar_examples[grammar_type]
        else:
            default_text = ""
        
        # Text area con el valor correspondiente
        input_text = st.text_area(
            "Gramática (formato BNF o reglas simples):",
            value=default_text,
            height=200,
            help="Formato: S → aSb | ab (una producción por línea)",
            key=f"grammar_input_{grammar_type}"  # Key único por tipo
        )
        
        analyze_button = st.button("Analizar Gramática", type="primary", use_container_width=True)
        
    elif input_type == "Autómata":
        st.subheader("Ingresar Definición de Autómata")
        
        # Dropdown secundario: Tipo de autómata
        automaton_type = st.selectbox(
            "Tipo de autómata (ejemplo):",
            ["Seleccionar tipo...", "AFD - Autómata Finito Determinista", 
             "AFN - Autómata Finito No Determinista", "AP - Autómata de Pila", 
             "MT - Máquina de Turing"],
            key="automaton_type_selector"
        )
        
        # Ejemplos de autómatas
        automaton_examples = {
            "AFD - Autómata Finito Determinista": """Estados: q0, q1, q2
Alfabeto: a, b
Estado inicial: q0
Estados finales: q2
Transiciones:
q0, a, q1
q0, b, q0
q1, a, q2
q1, b, q1
q2, a, q2
q2, b, q2""",
            "AFN - Autómata Finito No Determinista": """Estados: q0, q1, q2
Alfabeto: a, b
Estado inicial: q0
Estados finales: q2
Transiciones:
q0, a, q0
q0, a, q1
q1, b, q2""",
            "AP - Autómata de Pila": """Estados: q0, q1, q2
Alfabeto: a, b
Alfabeto de pila: Z, A
Estado inicial: q0
Estados finales: q2
Transiciones:
q0, a, Z, q0, AZ
q0, a, A, q0, AA
q0, b, A, q1, ε
q1, b, A, q1, ε
q1, ε, Z, q2, Z""",
            "MT - Máquina de Turing": """Estados: q0, q1, q2, halt
Alfabeto: a, b, #
Alfabeto de cinta: a, b, #, B
Estado inicial: q0
Estados finales: halt
Transiciones:
q0, a, q1, a, R
q0, b, q2, b, R
q1, a, q1, a, R
q1, #, halt, #, S"""
        }
        
        # Determinar el valor del text_area
        if automaton_type != "Seleccionar tipo..." and automaton_type in automaton_examples:
            default_text = automaton_examples[automaton_type]
        else:
            default_text = ""
        
        input_text = st.text_area(
            "Definición de Autómata:",
            value=default_text,
            height=200,
            help="Ingresa la definición del autómata en formato estructurado",
            key=f"automaton_input_{automaton_type}"  # Key único por tipo
        )
        
        analyze_button = st.button("Analizar Autómata", type="primary", use_container_width=True)
        
    else:  # Expresión Regular
        st.subheader("Ingresar Expresión Regular")
        
        # Dropdown secundario: Tipo de regex
        regex_type = st.selectbox(
            "Tipo de expresión regular (ejemplo):",
            ["Seleccionar tipo...", "Regex Simple", "Regex con Kleene", 
             "Regex con Unión", "Regex Compleja"],
            key="regex_type_selector"
        )
        
        # Ejemplos de expresiones regulares
        regex_examples = {
            "Regex Simple": "ab",
            "Regex con Kleene": "a*",
            "Regex con Unión": "a|b",
            "Regex Compleja": "(ab)*|(ba)+"
        }
        
        # Determinar el valor del text_area
        if regex_type != "Seleccionar tipo..." and regex_type in regex_examples:
            default_text = regex_examples[regex_type]
        else:
            default_text = ""
        
        input_text = st.text_area(
            "Expresión Regular:",
            value=default_text,
            height=100,
            help="Ingresa una expresión regular (ej: ab*, (a|b)*, etc.)",
            key=f"regex_input_{regex_type}"  # Key único por tipo
        )
        
        analyze_button = st.button("Analizar y Convertir Regex", type="primary", use_container_width=True)
    
    # Procesar análisis según el tipo de entrada
    if analyze_button:
        if not input_text.strip():
            st.error("Por favor, ingresa una entrada para analizar.")
        else:
            if input_type == "Gramática":
                with st.spinner("Analizando gramática..."):
                    # Parsear gramática
                    parser, errors = parse_grammar_from_text(input_text)
                
                if parser is None:
                    st.error("Error al parsear la gramática:")
                    for error in errors:
                        st.error(f"  - {error}")
                else:
                    # Mostrar información básica
                    st.success("Gramática parseada correctamente")
                    
                    # Clasificar
                    classifier = GrammarClassifier(parser)
                    chomsky_type = classifier.classify()
                    explanation = classifier.get_explanation()
                    violations = classifier.get_violations()
                    problematic = classifier.get_problematic_productions()
                    
                    # SALIDA VISUAL Y TEXTUAL - Tipo de lenguaje detectado
                    st.markdown("---")
                    st.subheader("Resultado del Análisis")
                    
                    if chomsky_type:
                        # Mostrar tipo destacado
                        type_display = {
                            ChomskyType.TYPE_3: "Tipo 3: Gramática Regular",
                            ChomskyType.TYPE_2: "Tipo 2: Gramática Libre de Contexto",
                            ChomskyType.TYPE_1: "Tipo 1: Gramática Sensible al Contexto",
                            ChomskyType.TYPE_0: "Tipo 0: Gramática Recursivamente Enumerable"
                        }
                        st.markdown(f"## {type_display.get(chomsky_type, chomsky_type.value)}")
                        
                        # Información adicional
                        type_info = {
                            ChomskyType.TYPE_3: {
                                "title": "Gramática Regular",
                                "description": "Genera lenguajes regulares. Puede ser reconocida por autómatas finitos.",
                                "power": "Menor poder expresivo"
                            },
                            ChomskyType.TYPE_2: {
                                "title": "Gramática Libre de Contexto",
                                "description": "Genera lenguajes libres de contexto. Puede ser reconocida por autómatas de pila.",
                                "power": "Poder expresivo medio"
                            },
                            ChomskyType.TYPE_1: {
                                "title": "Gramática Sensible al Contexto",
                                "description": "Genera lenguajes sensibles al contexto. Requiere máquinas de Turing lineales acotadas.",
                                "power": "Alto poder expresivo"
                            },
                            ChomskyType.TYPE_0: {
                                "title": "Gramática Recursivamente Enumerable",
                                "description": "Genera lenguajes recursivamente enumerables. Requiere máquinas de Turing completas.",
                                "power": "Máximo poder expresivo"
                            }
                        }
                        
                        info = type_info.get(chomsky_type, {})
                        if info:
                            st.info(f"**{info['title']}**: {info['description']} ({info['power']})")
                    
                    # SALIDA TEXTUAL - Justificación detallada
                    st.markdown("---")
                    st.subheader("Justificación Textual del Resultado")
                    st.markdown("**Explicación paso a paso del proceso de clasificación:**")
                    
                    with st.expander("Ver justificación completa", expanded=True):
                        for line in explanation:
                            if line.startswith("✓"):
                                st.success(line)
                            elif line.startswith("✗"):
                                st.error(line)
                            elif line.startswith("---"):
                                st.markdown(f"**{line}**")
                            elif line.startswith("Justificación") or line.startswith("La gramática"):
                                st.markdown(f"**{line}**")
                            else:
                                st.text(line)
                    
                    # SALIDA VISUAL - Representación visual
                    st.markdown("---")
                    st.subheader("Representación Visual")
                    
                    try:
                        viz_results = visualize_grammar_from_text(input_text, output_dir="output")
                        
                        if 'dependencies' in viz_results or 'structure' in viz_results:
                            col1, col2 = st.columns(2)
                            
                            if 'dependencies' in viz_results:
                                with col1:
                                    st.markdown("**Grafo de Dependencias**")
                                    st.image(viz_results['dependencies'], use_container_width=True)
                            
                            if 'structure' in viz_results:
                                with col2:
                                    st.markdown("**Estructura de Producciones**")
                                    st.image(viz_results['structure'], use_container_width=True)
                    except Exception as e:
                        st.warning(f"No se pudieron generar diagramas: {str(e)}")
                    
                    # Tabs para información adicional
                    tab1, tab2, tab3 = st.tabs(["Producciones", "Análisis Detallado", "Advertencias"])
                    
                    with tab1:
                        st.subheader("Producciones Parseadas")
                        
                        productions = parser.get_productions()
                        terminals = parser.get_terminals()
                        non_terminals = parser.get_non_terminals()
                        start_symbol = parser.get_start_symbol()
                        
                        st.markdown(f"**Símbolo inicial:** `{start_symbol}`")
                        st.markdown(f"**Símbolos terminales:** {', '.join(sorted(terminals)) if terminals else 'Ninguno'}")
                        st.markdown(f"**Símbolos no terminales:** {', '.join(sorted(non_terminals))}")
                        
                        st.markdown("---")
                        st.markdown("**Producciones:**")
                        for left, bodies in productions.items():
                            bodies_str = " | ".join(bodies)
                            st.code(f"{left} → {bodies_str}", language=None)
                    
                    with tab2:
                        st.subheader("Análisis Detallado de Producciones")
                        
                        productions = parser.get_productions()
                        for left, bodies in productions.items():
                            st.markdown(f"**{left} →**")
                            for body in bodies:
                                analysis = parser.analyze_production(left, body)
                                
                                with st.expander(f"`{left} → {body}`"):
                                    st.json(analysis)
                    
                    with tab3:
                        st.subheader("Advertencias y Errores")
                        
                        warnings = parser.get_warnings()
                        if warnings:
                            st.warning("Advertencias encontradas:")
                            for warning in warnings:
                                st.warning(f"  - {warning}")
                        else:
                            st.success("No se encontraron advertencias")
                        
                        if violations:
                            st.error("Violaciones de restricciones:")
                            for violation in violations:
                                st.error(f"  - **{violation['production']}**: {violation['reason']}")
                        
                        if problematic:
                            st.warning("Producciones problemáticas:")
                            for prod in problematic:
                                st.warning(f"  - {prod}")
                        
                        # Generación automática de reporte PDF
                        st.markdown("---")
                        st.subheader("Reporte PDF Automático")
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            auto_generate = st.checkbox("Generar reporte PDF automáticamente", value=True)
                        with col2:
                            include_diagrams = st.checkbox("Incluir diagramas", value=True)
                        
                        # Función auxiliar para generar y descargar PDF
                        def generate_and_download_pdf():
                            try:
                                pdf_path = generate_auto_pdf_report(
                                    input_text,
                                    output_dir="reportes",
                                    include_diagrams=include_diagrams
                                )
                                st.success("Reporte PDF generado exitosamente")
                                with open(pdf_path, "rb") as pdf_file:
                                    st.download_button(
                                        label="Descargar Reporte PDF",
                                        data=pdf_file,
                                        file_name=os.path.basename(pdf_path),
                                        mime="application/pdf",
                                        type="primary"
                                    )
                            except ImportError:
                                st.warning("reportlab no está instalado. Instala con: pip install reportlab")
                            except Exception as e:
                                st.error(f"Error al generar reporte: {str(e)}")
                        
                        # Generar automáticamente o mostrar botón manual
                        if auto_generate:
                            with st.spinner("Generando reporte PDF automático..."):
                                generate_and_download_pdf()
                        else:
                            if st.button("Generar Reporte PDF", type="primary"):
                                with st.spinner("Generando reporte PDF..."):
                                    generate_and_download_pdf()
            
            elif input_type == "Autómata":
                with st.spinner("Analizando autómata..."):
                    # Parsear autómata
                    automata_parser = AutomataParser()
                    if automata_parser.parse(input_text):
                        automaton_def = automata_parser.get_definition()
                        
                        # Analizar autómata
                        automaton_type, analysis, errors, warnings = analyze_automaton(automaton_def)
                        
                        st.success("Autómata parseado correctamente")
                        
                        # SALIDA VISUAL Y TEXTUAL
                        st.markdown("---")
                        st.subheader("Resultado del Análisis")
                        
                        if automaton_type:
                            st.markdown(f"## Tipo de Autómata: {automaton_type.value}")
                            
                            if 'chomsky_type' in analysis:
                                st.markdown(f"### Clasificación Chomsky: {analysis['chomsky_type']}")
                            
                            if 'computational_power' in analysis:
                                st.info(f"**Poder de cómputo:** {analysis['computational_power']}")
                        
                        # SALIDA TEXTUAL - Justificación
                        st.markdown("---")
                        st.subheader("Justificación Textual")
                        
                        st.markdown("**Análisis del autómata:**")
                        st.json(analysis)
                        
                        if errors:
                            st.error("Errores encontrados:")
                            for error in errors:
                                st.error(f"  - {error}")
                        
                        if warnings:
                            st.warning("Advertencias:")
                            for warning in warnings:
                                st.warning(f"  - {warning}")
                        
                        # SALIDA VISUAL - Diagrama
                        st.markdown("---")
                        st.subheader("Representación Visual")
                        
                        try:
                            from visualizer import AutomatonVisualizer
                            # Asegurar que output existe
                            os.makedirs("output", exist_ok=True)
                            viz = AutomatonVisualizer(
                                automaton_def['states'],
                                automaton_def['alphabet'],
                                automaton_def['transitions'],
                                automaton_def['initial_state'],
                                automaton_def['final_states']
                            )
                            diagram_path = viz.visualize(output_file="output/automaton")
                            if diagram_path and os.path.exists(diagram_path):
                                st.image(diagram_path, use_container_width=True)
                            else:
                                st.warning("No se pudo generar el diagrama del autómata")
                        except Exception as e:
                            st.warning(f"No se pudo generar diagrama: {str(e)}")
                    else:
                        st.error("Error al parsear el autómata:")
                        for error in automata_parser.get_errors():
                            st.error(f"  - {error}")
            
            else:  # Expresión Regular
                with st.spinner("Analizando y convirtiendo expresión regular..."):
                    try:
                        # Convertir regex a gramática
                        grammar, explanation = regex_to_grammar(input_text)
                        
                        st.success("Expresión regular procesada correctamente")
                        
                        # SALIDA TEXTUAL
                        st.markdown("---")
                        st.subheader("Resultado de la Conversión")
                        
                        st.markdown("**Gramática Regular equivalente:**")
                        st.code(grammar, language=None)
                        
                        st.markdown("**Proceso de conversión:**")
                        for line in explanation:
                            st.text(line)
                        
                        # Analizar la gramática resultante
                        parser, errors = parse_grammar_from_text(grammar)
                        if parser:
                            classifier = GrammarClassifier(parser)
                            chomsky_type = classifier.classify()
                            
                            st.markdown("---")
                            st.subheader("Clasificación de la Gramática Resultante")
                            st.markdown(f"### {chomsky_type.value if chomsky_type else 'N/A'}")
                            
                            # SALIDA VISUAL
                            st.markdown("---")
                            st.subheader("Representación Visual")
                            
                            try:
                                viz_results = visualize_grammar_from_text(grammar, output_dir="output")
                                if 'dependencies' in viz_results:
                                    st.image(viz_results['dependencies'], use_container_width=True)
                            except:
                                pass
                    except Exception as e:
                        st.error(f"Error al procesar expresión regular: {str(e)}")

# Modo: Visualizador
elif mode == "Visualizador":
    st.header("Visualizador de Gramáticas")
    st.markdown("Genera diagramas visuales de gramáticas y autómatas.")
    
    grammar_input = st.text_area(
        "Gramática para visualizar:",
        value="S → aSb | ab",
        height=150
    )
    
    if st.button("Generar Diagramas", type="primary"):
        if not grammar_input.strip():
            st.error("Por favor, ingresa una gramática.")
        else:
            with st.spinner("Generando diagramas..."):
                results = visualize_grammar_from_text(grammar_input, output_dir="output")
                
                if 'error' in results:
                    st.error(f"{results['error']}")
                else:
                    st.success("Diagramas generados correctamente")
                    
                    col1, col2 = st.columns(2)
                    
                    if 'dependencies' in results:
                        with col1:
                            st.subheader("Grafo de Dependencias")
                            st.image(results['dependencies'], use_container_width=True)
                            with open(results['dependencies'], "rb") as file:
                                st.download_button(
                                    label="Descargar PNG",
                                    data=file,
                                    file_name="dependencies.png",
                                    mime="image/png"
                                )
                    
                    if 'structure' in results:
                        with col2:
                            st.subheader("Estructura de Producciones")
                            st.image(results['structure'], use_container_width=True)
                            with open(results['structure'], "rb") as file:
                                st.download_button(
                                    label="Descargar PNG",
                                    data=file,
                                    file_name="structure.png",
                                    mime="image/png"
                                )

# Modo: Comparador
elif mode == "Comparador":
    st.header("Comparador de Gramáticas")
    st.markdown("Compara dos gramáticas para encontrar similitudes y diferencias.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Gramática 1")
        grammar1_input = st.text_area(
            "Primera gramática:",
            value="S → aSb | ab",
            height=150,
            key="grammar1"
        )
    
    with col2:
        st.subheader("Gramática 2")
        grammar2_input = st.text_area(
            "Segunda gramática:",
            value="S → aSb | ε",
            height=150,
            key="grammar2"
        )
    
    if st.button("Comparar Gramáticas", type="primary"):
        if not grammar1_input.strip() or not grammar2_input.strip():
            st.error("Por favor, ingresa ambas gramáticas para comparar.")
        else:
            with st.spinner("Comparando gramáticas..."):
                try:
                    result = compare_grammars(grammar1_input, grammar2_input, max_depth=5)
                    
                    # Mostrar resultados
                    st.subheader("Resultados de la Comparación")
                    
                    # Tipos
                    col_type1, col_type2 = st.columns(2)
                    with col_type1:
                        st.info(f"**Gramática 1:** {result['grammar1_type'].value if result['grammar1_type'] else 'N/A'}")
                    with col_type2:
                        st.info(f"**Gramática 2:** {result['grammar2_type'].value if result['grammar2_type'] else 'N/A'}")
                    
                    # Mismo tipo
                    if result['same_type']:
                        st.success("Ambas gramáticas son del mismo tipo")
                    else:
                        st.warning("Las gramáticas son de tipos diferentes")
                    
                    # Similitudes
                    if result['similarities']:
                        st.subheader("Similitudes")
                        for similarity in result['similarities']:
                            st.success(f"✓ {similarity}")
                    
                    # Diferencias
                    if result['differences']:
                        st.subheader("Diferencias")
                        for difference in result['differences']:
                            st.warning(f"• {difference}")
                    
                    # Comparación heurística
                    if 'heuristic_comparison' in result and result['heuristic_comparison']:
                        st.subheader("Comparación Heurística de Lenguajes")
                        heur = result['heuristic_comparison']
                        
                        st.markdown(f"**Cadenas generadas por gramática 1:** {heur.get('strings_generated_1', 0)}")
                        st.markdown(f"**Cadenas generadas por gramática 2:** {heur.get('strings_generated_2', 0)}")
                        st.markdown(f"**Cadenas comunes:** {heur.get('common_strings', 0)}")
                        
                        if heur.get('sample_common'):
                            st.markdown("**Muestra de cadenas comunes:**")
                            st.code(', '.join(heur['sample_common'][:10]))
                        
                        if heur.get('sample_only_1'):
                            st.markdown("**Cadenas solo en gramática 1:**")
                            st.code(', '.join(heur['sample_only_1'][:5]))
                        
                        if heur.get('sample_only_2'):
                            st.markdown("**Cadenas solo en gramática 2:**")
                            st.code(', '.join(heur['sample_only_2'][:5]))
                    
                except Exception as e:
                    st.error(f"Error al comparar gramáticas: {str(e)}")

# Modo: Generador de Ejemplos
elif mode == "Generador de Ejemplos":
    st.header("Generador Automático de Ejemplos")
    st.markdown("Genera gramáticas aleatorias de cada tipo de la Jerarquía de Chomsky.")
    
    col_type, col_complexity = st.columns(2)
    
    with col_type:
        example_type = st.selectbox(
            "Tipo de gramática a generar:",
            ["Tipo 3 - Regular", "Tipo 2 - Libre de Contexto", "Tipo 1 - Sensible al Contexto", "Tipo 0 - Recursivamente Enumerable"]
        )
    
    with col_complexity:
        complexity = st.selectbox(
            "Nivel de complejidad:",
            ["simple", "medium", "complex"]
        )
    
    type_map = {
        "Tipo 3 - Regular": ChomskyType.TYPE_3,
        "Tipo 2 - Libre de Contexto": ChomskyType.TYPE_2,
        "Tipo 1 - Sensible al Contexto": ChomskyType.TYPE_1,
        "Tipo 0 - Recursivamente Enumerable": ChomskyType.TYPE_0
    }
    
    if st.button("Generar Ejemplo", type="primary"):
        with st.spinner("Generando gramática..."):
            try:
                chomsky_type = type_map[example_type]
                result = generate_example(chomsky_type, complexity)
                
                st.subheader("Gramática Generada")
                st.code(result['grammar'], language=None)
                
                if result['is_valid']:
                    st.success(f"Gramática válida de tipo {result['requested_type']}")
                else:
                    st.warning("La gramática generada no pasó la validación")
                
                if result['explanation']:
                    with st.expander("Ver explicación de clasificación"):
                        for line in result['explanation']:
                            st.text(line)
                
                # Botón para analizar la gramática generada
                if st.button("Analizar esta gramática"):
                    st.session_state['grammar_to_analyze'] = result['grammar']
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error al generar ejemplo: {str(e)}")

# Modo: Quiz/Tutor
elif mode == "Modo Quiz/Tutor":
    st.header("Modo Quiz/Tutor Interactivo")
    st.markdown("Practica clasificando gramáticas. El sistema generará ejercicios aleatorios y te dará retroalimentación inmediata.")
    
    # Inicializar quiz en session_state
    if 'quiz' not in st.session_state:
        st.session_state.quiz = QuizMode()
    
    if 'quiz_difficulty' not in st.session_state:
        st.session_state.quiz_difficulty = "medium"
    
    # Configuración del quiz
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Configuración")
        difficulty = st.selectbox(
            "Nivel de dificultad:",
            ["easy", "medium", "hard"],
            index=1,
            key="quiz_difficulty_selector"
        )
        
        if difficulty != st.session_state.quiz_difficulty:
            st.session_state.quiz_difficulty = difficulty
            st.session_state.quiz.reset_quiz()
    
    with col2:
        st.subheader("Estadísticas")
        stats = st.session_state.quiz.get_statistics()
        st.metric("Puntuación", f"{stats['score']}/{stats['total']}")
        if stats['total'] > 0:
            st.metric("Porcentaje", f"{stats['percentage']}%")
            st.metric("Correctas", stats['correct'])
            st.metric("Incorrectas", stats['incorrect'])
    
    st.markdown("---")
    
    # Generar nueva pregunta si no hay una activa o si se solicita
    if st.session_state.quiz.get_current_question() is None or st.button("Nueva Pregunta", type="primary"):
        with st.spinner("Generando pregunta..."):
            question = st.session_state.quiz.generate_question(st.session_state.quiz_difficulty)
            st.session_state.current_question = question
    
    current_question = st.session_state.quiz.get_current_question()
    
    if current_question:
        st.subheader("Pregunta")
        st.markdown("**Clasifica la siguiente gramática según la Jerarquía de Chomsky:**")
        
        st.code(current_question['grammar'], language=None)
        
        # Opciones de respuesta
        answer_options = {
            "Tipo 3 - Regular": ChomskyType.TYPE_3,
            "Tipo 2 - Libre de Contexto": ChomskyType.TYPE_2,
            "Tipo 1 - Sensible al Contexto": ChomskyType.TYPE_1,
            "Tipo 0 - Recursivamente Enumerable": ChomskyType.TYPE_0
        }
        
        if not current_question.get('answered', False):
            selected_answer_text = st.radio(
                "Selecciona tu respuesta:",
                options=list(answer_options.keys()),
                key="quiz_answer"
            )
            
            col_submit, col_reset = st.columns([1, 1])
            
            with col_submit:
                if st.button("Enviar Respuesta", type="primary", use_container_width=True):
                    selected_answer = answer_options[selected_answer_text]
                    result = st.session_state.quiz.submit_answer(selected_answer)
                    st.session_state.quiz_result = result
                    st.rerun()
            
            with col_reset:
                if st.button("Reiniciar Quiz", use_container_width=True):
                    st.session_state.quiz.reset_quiz()
                    st.session_state.quiz_result = None
                    st.rerun()
        else:
            # Mostrar resultado
            result = st.session_state.get('quiz_result', {})
            
            if result.get('is_correct'):
                st.success("¡Correcto! Has clasificado la gramática correctamente.")
            else:
                st.error("Incorrecto. Tu respuesta no es correcta.")
            
            st.info(f"**Respuesta correcta:** {current_question['correct_answer'].value}")
            if current_question.get('user_answer'):
                st.info(f"**Tu respuesta:** {current_question['user_answer'].value}")
            
            # Retroalimentación detallada
            st.subheader("Retroalimentación")
            st.markdown(result.get('feedback', ''))
            
            # Explicación completa
            if current_question.get('explanation'):
                with st.expander("Ver explicación completa del análisis"):
                    for line in current_question['explanation']:
                        if line.strip():
                            if line.startswith("✓"):
                                st.success(line)
                            elif line.startswith("✗"):
                                st.error(line)
                            elif line.startswith("---"):
                                st.markdown(f"**{line}**")
                            else:
                                st.text(line)
            
            col_new, col_reset = st.columns([1, 1])
            
            with col_new:
                if st.button("Siguiente Pregunta", type="primary", use_container_width=True):
                    st.session_state.quiz.current_question = None
                    st.session_state.quiz_result = None
                    st.rerun()
            
            with col_reset:
                if st.button("Reiniciar Quiz", use_container_width=True):
                    st.session_state.quiz.reset_quiz()
                    st.session_state.quiz_result = None
                    st.rerun()
    
    # Historial de preguntas
    if st.session_state.quiz.questions_history:
        st.markdown("---")
        with st.expander("Ver historial de preguntas"):
            for i, q in enumerate(st.session_state.quiz.questions_history[-10:], 1):  # Últimas 10
                status = "✓" if q.get('is_correct') else "✗"
                st.markdown(f"**Pregunta {i}:** {status} {q.get('correct_answer').value if q.get('correct_answer') else 'N/A'}")
                st.code(q['grammar'], language=None)

# Modo: Ejemplos
elif mode == "Ejemplos":
    st.header("Ejemplos de Gramáticas")
    st.markdown("Explora ejemplos de gramáticas de cada tipo de la Jerarquía de Chomsky.")
    
    example_type = st.selectbox(
        "Selecciona un tipo de gramática:",
        ["Tipo 3 - Regular", "Tipo 2 - Libre de Contexto", "Tipo 1 - Sensible al Contexto", "Tipo 0 - Recursivamente Enumerable"]
    )
    
    examples = {
        "Tipo 3 - Regular": {
            "grammar": """S → aA
A → bB | b
B → a""",
            "description": "Gramática regular que genera cadenas con el patrón 'ab*a'",
            "language": "L = {ab^n a | n >= 0}"
        },
        "Tipo 2 - Libre de Contexto": {
            "grammar": """S → aSb | ab""",
            "description": "Gramática libre de contexto que genera cadenas con igual número de a's y b's balanceadas",
            "language": "L = {a^n b^n | n >= 1}"
        },
        "Tipo 1 - Sensible al Contexto": {
            "grammar": """S → aSBC | aBC
CB → BC
aB → ab
bB → bb""",
            "description": "Gramática sensible al contexto que genera cadenas con igual número de a's, b's y c's",
            "language": "L = {a^n b^n c^n | n >= 1}"
        },
        "Tipo 0 - Recursivamente Enumerable": {
            "grammar": """S → ACaB
Ca → aaC
CB → DB | E""",
            "description": "Gramática recursivamente enumerable (sin restricciones)",
            "language": "Lenguaje complejo que requiere máquina de Turing completa"
        }
    }
    
    if example_type in examples:
        example = examples[example_type]
        
        st.markdown(f"**Descripción:** {example['description']}")
        st.markdown(f"**Lenguaje generado:** {example['language']}")
        
        st.code(example['grammar'], language=None)
        
        if st.button("Analizar este ejemplo", type="primary"):
            st.session_state['grammar_to_analyze'] = example['grammar']
            st.rerun()

# Modo: Ayuda
elif mode == "Ayuda":
    st.header("Ayuda y Documentación")
    
    st.markdown("""
    ## Guía de Uso
    
    ### Formato de Gramáticas
    
    El sistema acepta gramáticas en formato BNF o reglas simples:
    
    ```
    S → aSb | ab
    A → bA | b
    ```
    
    **Símbolos de producción soportados:**
    - `→` (flecha)
    - `->` (guión y mayor que)
    - `::=` (BNF estándar)
    
    **Separador de alternativas:**
    - `|` (barra vertical)
    
    ### Tipos de Chomsky
    
    1. **Tipo 3 - Regular**: Forma `A → aB | a` o `A → Ba | a`
    2. **Tipo 2 - Libre de Contexto**: Forma `A → α` (un solo no terminal a la izquierda)
    3. **Tipo 1 - Sensible al Contexto**: Forma `αAβ → αγβ` donde `|γ| >= 1`
    4. **Tipo 0 - Recursivamente Enumerable**: Sin restricciones
    
    ### Características
    
    - Análisis automático de gramáticas
    - Clasificación según Jerarquía de Chomsky
    - Explicaciones detalladas paso a paso
    - Visualización de diagramas
    - Detección de errores y advertencias
    - Generación de reportes PDF
    - Comparación de gramáticas
    - Generador automático de ejemplos
    - Modo Quiz/Tutor interactivo con retroalimentación
    - Análisis de autómatas
    - Conversión entre representaciones (Regex, AFN, AFD, Gramática)
    
    ### Ejemplos de Uso
    
    **Gramática Regular:**
    ```
    S → aA
    A → bB | b
    B → a
    ```
    
    **Gramática Libre de Contexto:**
    ```
    S → aSb | ab
    ```
    
    ### Contacto y Soporte
    
    Para más información sobre la Jerarquía de Chomsky, consulta:
    - Teoría de la Computación - Hopcroft, Motwani, Ullman
    - Introduction to Automata Theory - Sipser
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Chomsky Classifier AI - Sistema de Clasificación de Gramáticas Formales<br>"
    "Desarrollado para el curso de Lenguajes y Autómatas"
    "</div>",
    unsafe_allow_html=True
)

