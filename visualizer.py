"""
Módulo de visualización para gramáticas y autómatas.

Genera diagramas usando Graphviz y NetworkX:
- Diagramas de transición de autómatas
- Árboles de derivación de gramáticas
- Grafos de dependencias entre símbolos
- Exportación en formatos PNG y SVG
"""

import os
import re
from typing import Dict, List, Set, Tuple, Optional
from graphviz import Digraph
import networkx as nx
import matplotlib.pyplot as plt
from grammar_parser import GrammarParser


class GrammarVisualizer:
    """
    Visualizador de gramáticas formales.
    
    Genera diagramas de:
    - Árboles de derivación
    - Grafos de dependencias entre símbolos
    - Estructura de producciones
    """
    
    def __init__(self, parser: GrammarParser):
        """
        Inicializa el visualizador con un parser de gramática.
        
        Args:
            parser: GrammarParser con la gramática parseada
        """
        self.parser = parser
        self.productions = parser.get_productions()
        self.start_symbol = parser.get_start_symbol()
    
    def visualize_dependency_graph(self, output_file: str = "grammar_dependencies", format: str = "png") -> str:
        """
        Genera un grafo de dependencias entre símbolos no terminales.
        
        Muestra qué símbolos dependen de otros (cuando un símbolo aparece
        en el lado derecho de la producción de otro).
        
        Args:
            output_file: Nombre del archivo de salida (sin extensión)
            format: Formato de salida ('png', 'svg', 'pdf')
            
        Returns:
            Ruta del archivo generado
        """
        dot = Digraph(comment='Grafo de Dependencias de Gramática')
        dot.attr(rankdir='LR')
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
        
        # Agregar nodos (símbolos no terminales)
        for nt in self.productions.keys():
            dot.node(nt, nt)
        
        # Agregar aristas (dependencias)
        for left, bodies in self.productions.items():
            for body in bodies:
                # Buscar símbolos no terminales en el cuerpo
                nts_in_body = re.findall(r'[A-Z][a-zA-Z0-9]*', body)
                for nt in nts_in_body:
                    if nt in self.productions:  # Solo si el símbolo tiene producción
                        dot.edge(left, nt, label=body[:20])  # Limitar longitud de etiqueta
        
        # Renderizar
        output_path = dot.render(output_file, format=format, cleanup=True)
        return output_path
    
    def visualize_production_structure(self, output_file: str = "grammar_structure", format: str = "png") -> str:
        """
        Genera un diagrama que muestra la estructura de las producciones.
        
        Args:
            output_file: Nombre del archivo de salida (sin extensión)
            format: Formato de salida ('png', 'svg', 'pdf')
            
        Returns:
            Ruta del archivo generado
        """
        dot = Digraph(comment='Estructura de Producciones')
        dot.attr(rankdir='TB')
        dot.attr('node', shape='box')
        
        # Agregar nodos y aristas para cada producción
        for left, bodies in self.productions.items():
            # Nodo para el símbolo no terminal
            dot.node(left, left, style='filled', fillcolor='lightgreen')
            
            # Crear nodos para cada cuerpo de producción
            for i, body in enumerate(bodies):
                body_id = f"{left}_{i}"
                dot.node(body_id, body, shape='ellipse', style='filled', fillcolor='lightyellow')
                dot.edge(left, body_id)
        
        output_path = dot.render(output_file, format=format, cleanup=True)
        return output_path
    
    def generate_derivation_tree(self, derivation: List[str], output_file: str = "derivation_tree", format: str = "png") -> str:
        """
        Genera un árbol de derivación para una secuencia de pasos.
        
        Args:
            derivation: Lista de cadenas representando los pasos de derivación
            output_file: Nombre del archivo de salida (sin extensión)
            format: Formato de salida ('png', 'svg', 'pdf')
            
        Returns:
            Ruta del archivo generado
        """
        dot = Digraph(comment='Árbol de Derivación')
        dot.attr(rankdir='TB')
        dot.attr('node', shape='box')
        
        # Crear nodos para cada paso
        for i, step in enumerate(derivation):
            node_id = f"step_{i}"
            dot.node(node_id, step)
            
            # Conectar con el paso anterior
            if i > 0:
                dot.edge(f"step_{i-1}", node_id)
        
        output_path = dot.render(output_file, format=format, cleanup=True)
        return output_path


class AutomatonVisualizer:
    """
    Visualizador de autómatas (AFD, AFN, AP, MT).
    
    Genera diagramas de transición de estados.
    """
    
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: List[Tuple],
                 initial_state: str, final_states: Set[str]):
        """
        Inicializa el visualizador de autómata.
        
        Args:
            states: Conjunto de estados
            alphabet: Alfabeto de entrada
            transitions: Lista de transiciones (estado_origen, símbolo, estado_destino)
            initial_state: Estado inicial
            final_states: Conjunto de estados finales
        """
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
    
    def visualize(self, output_file: str = "automaton", format: str = "png") -> str:
        """
        Genera un diagrama del autómata.
        
        Args:
            output_file: Nombre del archivo de salida (sin extensión)
            format: Formato de salida ('png', 'svg', 'pdf')
            
        Returns:
            Ruta del archivo generado
        """
        dot = Digraph(comment='Autómata')
        dot.attr(rankdir='LR')
        dot.attr('node', shape='circle')
        
        # Agregar nodo inicial invisible
        dot.node('start', '', shape='point')
        dot.edge('start', self.initial_state)
        
        # Agregar estados
        for state in self.states:
            if state in self.final_states:
                # Estado final: doble círculo
                dot.node(state, state, shape='doublecircle', style='filled', fillcolor='lightgreen')
            else:
                dot.node(state, state)
        
        # Agregar transiciones
        transition_dict = {}
        for trans in self.transitions:
            if len(trans) >= 3:
                from_state, symbol, to_state = trans[0], trans[1], trans[2]
                edge_key = (from_state, to_state)
                
                if edge_key not in transition_dict:
                    transition_dict[edge_key] = []
                transition_dict[edge_key].append(str(symbol))
        
        # Crear aristas con etiquetas combinadas
        for (from_state, to_state), symbols in transition_dict.items():
            label = ', '.join(symbols)
            dot.edge(from_state, to_state, label=label)
        
        output_path = dot.render(output_file, format=format, cleanup=True)
        return output_path
    
    def visualize_with_networkx(self, output_file: str = "automaton_nx", format: str = "png") -> str:
        """
        Genera un diagrama usando NetworkX y Matplotlib.
        
        Args:
            output_file: Nombre del archivo de salida (sin extensión)
            format: Formato de salida ('png', 'svg', 'pdf')
            
        Returns:
            Ruta del archivo generado
        """
        G = nx.DiGraph()
        
        # Agregar nodos
        G.add_nodes_from(self.states)
        
        # Agregar aristas
        for trans in self.transitions:
            if len(trans) >= 3:
                from_state, symbol, to_state = trans[0], trans[1], trans[2]
                if G.has_edge(from_state, to_state):
                    # Si ya existe la arista, agregar el símbolo a la etiqueta
                    G[from_state][to_state]['label'] += f', {symbol}'
                else:
                    G.add_edge(from_state, to_state, label=str(symbol))
        
        # Crear layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Dibujar
        plt.figure(figsize=(12, 8))
        
        # Dibujar aristas
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)
        
        # Dibujar nodos
        node_colors = ['lightgreen' if state in self.final_states else 'lightblue' 
                      for state in self.states]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000)
        
        # Etiquetas de nodos
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        # Etiquetas de aristas
        edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)
        
        # Marcar estado inicial
        if self.initial_state in pos:
            x, y = pos[self.initial_state]
            plt.annotate('', xy=(x-0.15, y), xytext=(x-0.3, y),
                        arrowprops=dict(arrowstyle='->', lw=2, color='red'))
        
        plt.title('Diagrama de Autómata', fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # Guardar
        output_path = f"{output_file}.{format}"
        plt.savefig(output_path, format=format, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path


def visualize_grammar_from_text(grammar_text: str, output_dir: str = "output") -> Dict[str, str]:
    """
    Función de conveniencia para visualizar una gramática desde texto.
    
    Args:
        grammar_text: Texto con la gramática
        output_dir: Directorio de salida
        
    Returns:
        Diccionario con las rutas de los archivos generados
    """
    # Crear directorio si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Parsear gramática
    parser = GrammarParser()
    if not parser.parse(grammar_text):
        return {'error': 'No se pudo parsear la gramática'}
    
    # Crear visualizador
    visualizer = GrammarVisualizer(parser)
    
    # Generar diagramas
    results = {}
    
    try:
        dep_path = visualizer.visualize_dependency_graph(
            output_file=os.path.join(output_dir, "dependencies")
        )
        results['dependencies'] = dep_path
    except Exception as e:
        results['dependencies_error'] = str(e)
    
    try:
        struct_path = visualizer.visualize_production_structure(
            output_file=os.path.join(output_dir, "structure")
        )
        results['structure'] = struct_path
    except Exception as e:
        results['structure_error'] = str(e)
    
    return results


# Ejemplos de uso
if __name__ == "__main__":
    # Ejemplo 1: Visualizar gramática
    print("Generando diagramas de gramática...")
    grammar = """
    S → aSb | ab
    """
    
    results = visualize_grammar_from_text(grammar, output_dir="examples")
    print("Resultados:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    # Ejemplo 2: Visualizar autómata
    print("\nGenerando diagrama de autómata...")
    states = {'q0', 'q1', 'q2'}
    alphabet = {'a', 'b'}
    transitions = [
        ('q0', 'a', 'q1'),
        ('q1', 'b', 'q2'),
        ('q2', 'a', 'q0')
    ]
    initial = 'q0'
    final = {'q2'}
    
    automaton_viz = AutomatonVisualizer(states, alphabet, transitions, initial, final)
    try:
        path = automaton_viz.visualize(output_file="examples/automaton")
        print(f"Diagrama generado: {path}")
    except Exception as e:
        print(f"Error: {e}")

