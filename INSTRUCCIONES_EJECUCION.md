# Instrucciones de Ejecución - Chomsky Classifier AI

## Métodos de Ejecución

El proyecto puede ejecutarse de varias maneras:

### Método 1: Script Batch (Windows) - RECOMENDADO

Simplemente haz doble clic en el archivo `run.bat` o ejecuta en la consola:

```bash
run.bat
```

### Método 2: Script Shell (Linux/Mac)

Ejecuta en la terminal:

```bash
chmod +x run.sh
./run.sh
```

### Método 3: Script Python

Ejecuta directamente:

```bash
python run.py
```

O con opciones:

```bash
# Especificar puerto
python run.py --port 8502

# Especificar host
python run.py --host 0.0.0.0

# Abrir navegador automáticamente
python run.py --browser
```

### Método 4: Comando Streamlit Directo

El método tradicional:

```bash
streamlit run main.py
```

Con opciones:

```bash
# Puerto personalizado
streamlit run main.py --server.port 8502

# Host personalizado (accesible desde red local)
streamlit run main.py --server.address 0.0.0.0

# Sin abrir navegador automáticamente
streamlit run main.py --server.headless true
```

## Requisitos Previos

Antes de ejecutar, asegúrate de tener instaladas las dependencias:

```bash
pip install -r requirements.txt
```

## Acceso a la Aplicación

Una vez iniciada, la aplicación estará disponible en:

- **URL local:** http://localhost:8501
- **URL de red:** http://[tu-ip]:8501 (si usas --server.address 0.0.0.0)

## Detener la Aplicación

Presiona `Ctrl+C` en la terminal donde se está ejecutando.

## Solución de Problemas

### Error: "Streamlit no está instalado"

```bash
pip install streamlit
```

### Error: "Módulo no encontrado"

```bash
pip install -r requirements.txt
```

### Puerto ya en uso

Usa un puerto diferente:

```bash
streamlit run main.py --server.port 8502
```

### No se abre el navegador automáticamente

Abre manualmente tu navegador y ve a: http://localhost:8501

## Notas

- La primera vez que ejecutes, Streamlit puede tardar unos segundos en iniciar
- Si cambias el código, Streamlit se recargará automáticamente
- Los archivos generados (PDFs, diagramas) se guardan en la carpeta `output/`

