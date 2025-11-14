#!/bin/bash

echo "========================================"
echo "Chomsky Classifier AI"
echo "Iniciando aplicacion..."
echo "========================================"
echo ""

# Verificar si streamlit está instalado
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "ERROR: Streamlit no está instalado."
    echo "Por favor ejecuta: pip install -r requirements.txt"
    exit 1
fi

# Iniciar Streamlit
streamlit run main.py

