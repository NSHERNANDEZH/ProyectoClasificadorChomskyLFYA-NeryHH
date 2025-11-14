"""
Script de ejecución alternativa para Chomsky Classifier AI.

Este script permite ejecutar la aplicación de diferentes maneras:
- Como script Python directo
- Con opciones de configuración
"""

import sys
import subprocess
import os


def check_dependencies():
    """Verifica que las dependencias estén instaladas."""
    required_modules = ['streamlit', 'grammar_parser', 'classifier']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print("ERROR: Faltan las siguientes dependencias:")
        for mod in missing:
            print(f"  - {mod}")
        print("\nPor favor ejecuta: pip install -r requirements.txt")
        return False
    
    return True


def run_streamlit(port=8501, host="localhost"):
    """
    Ejecuta la aplicación Streamlit.
    
    Args:
        port: Puerto en el que se ejecutará la aplicación
        host: Host en el que se ejecutará la aplicación
    """
    if not check_dependencies():
        sys.exit(1)
    
    print("=" * 50)
    print("Chomsky Classifier AI")
    print("Iniciando aplicación...")
    print("=" * 50)
    print()
    print(f"La aplicación se abrirá en: http://{host}:{port}")
    print("Presiona Ctrl+C para detener la aplicación")
    print()
    
    # Ejecutar streamlit
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", "main.py",
            "--server.port", str(port),
            "--server.address", host
        ]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nAplicación detenida por el usuario.")
    except Exception as e:
        print(f"\nERROR al ejecutar la aplicación: {e}")
        sys.exit(1)


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Chomsky Classifier AI - Sistema de Clasificación de Gramáticas Formales"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8501,
        help="Puerto en el que se ejecutará la aplicación (default: 8501)"
    )
    parser.add_argument(
        "--host", "-H",
        type=str,
        default="localhost",
        help="Host en el que se ejecutará la aplicación (default: localhost)"
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Abrir automáticamente el navegador"
    )
    
    args = parser.parse_args()
    
    # Construir comando
    cmd = [
        sys.executable, "-m", "streamlit", "run", "main.py",
        "--server.port", str(args.port),
        "--server.address", args.host
    ]
    
    if args.browser:
        cmd.append("--server.headless")
        cmd.append("false")
    
    print("=" * 50)
    print("Chomsky Classifier AI")
    print("Iniciando aplicación...")
    print("=" * 50)
    print()
    print(f"La aplicación se abrirá en: http://{args.host}:{args.port}")
    print("Presiona Ctrl+C para detener la aplicación")
    print()
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nAplicación detenida por el usuario.")
    except Exception as e:
        print(f"\nERROR al ejecutar la aplicación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Si se ejecuta sin argumentos, usar valores por defecto
    if len(sys.argv) == 1:
        run_streamlit()
    else:
        main()

