# autoreadme — AI-powered PR Companion & README Generator

**autoreadme** has evolved. While it still generates professional READMEs, its primary mission is now to be your **AI-powered PR Companion**. It analyzes your Pull Requests, summarizes changes, detects breaking changes via AST, and suggests missing tests.

## 🚀 Key Features

- **🤖 PR Companion**: Generate executive summaries of your Pull Requests.
- **⚠️ Breaking Change Detection**: AST-based analysis to detect signature changes and removed functions.
- **🧪 Test Suggestions**: AI-driven suggestions for test cases based on your code changes.
- **📁 README Generation**: Automatically generate a professional README.md from your codebase.
- **🌐 Multi-language**: Supports Python, JavaScript, TypeScript, Go, Java, Rust, and Ruby.
- **🤖 Provider Agnostic**: Works with Ollama (local), OpenAI, Anthropic, and Gemini.

## 📦 Installation

```bash
pip install autoreadme
```

## 🛠️ Usage

### Analyze Pull Request
```bash
autoreadme pr --base main
```

### Generate README
```bash
autoreadme . --provider openai
```

---

## 📋 Overview

### Resumen Técnico del Proyecto 'autoreadme'

#### Arquitectura del Proyecto

El proyecto 'autoreadme' es un conjunto de scripts y bibliotecas diseñadas para generar automáticamente los archivos README de proyectos basados en la información y funciones disponibles en su códigobase. La estructura principal del proyecto se divide en varios módulos y paquetes, cada uno responsable de una parte específica del proceso.

#### Módulos Principales

1. **autoreadme/analyzer.py**: Este archivo contiene las funciones principales para analizar proyectos utilizando LLMs. Al cargar el repositorio Git, recoge archivos específicos, lee el contenido de los archivos, y utiliza un modelo de generación de texto para generar descripciones detalladas de los archivos y estructuras del proyecto.

2. **autoreadme/cli.py**: Implementa una interfaz de comando simple para ejecutar la herramienta `autoreadme`. El archivo proporciona opciones para cargar configuraciones, generar READMEs basados en datos, y mostrar información sobre el estado actual del proceso.

3. **autoreadme/generator.py**: Este script usa Jinja2 y una LLM RAG para generar un README.md completo para un proyecto basado en un conjunto de datos detallados. Es capaz de construir diagramas de arquitectura, identificar rutas de API, extraer información sobre bases de datos y servicios externos.

4. **autoreadme/llm/__init__.py**: Define una biblioteca para implementar diferentes proveedores de lenguaje de inteligencia artificial (LLMs). Algunas de las funciones principales incluyen:

   - `LLMProvider`: Una clase que representa a un provider.
   
   - `get_provider`: Un método para obtener los proveedores disponibles.

5. **autoreadme/llm/factory.py**: Define una función `get_provider` para obtener instancias de proveedores específicos.

6. **autoreadme/llm/openai_provider.py**, **autoreadme/llm/ollama_provider.py**, **autoreadme/llm/anthropic_provider.py**, y **autoreadme/llm/gemini_provider.py**: Definen los proveedores de lenguaje para diferentes modelos, como OpenAI, Anthropic, GPT-3, Ollama, y Gemini, respectivamente.

7. **autoreadme/languages/base.py**: Define una clase abstracta `FileInfo` que se utiliza para almacenar información detallada sobre un archivo de código fuente. También incluye una clase abstracta `LanguageParser` que define el patrón abstractor para analizar archivos específicos.

8. **autoreadme/languages/java.py**, **autoreadme/languages/registry.py**, **autoreadme/languages/ruby.py**, **autoreadme/languages/python.py**, **autoreadme/languages/go.py**, y **autoreadme/languages/javascript.py**: Implementan la clase `LanguageParser` para cada lenguaje, proporcionando funciones específicas para extraer información del código fuente correspondiente.

9. **autoreadme/languages/__init__.py**: Define una estructura básica para el módulo de análisis de lenguajes.

10. **autoreadme/languages/rust.py**: Implementa la clase `RustParser` para analizar archivos en Rust.

#### Dependencias Runtime

La herramienta 'autoreadme' requiere las siguientes dependencias:

- click: Para implementar la interfaz de comando simple.
- jinja2: Para generar el README.md utilizando un template.
- rich: Para mejorar la presentación de los resultados.
- pyyaml: Para parsear y manipular archivos YAML.
- pytest: Para testear el código.
- pytest-cov: Para medir覆盖率 del código durante los tests.
- pathspec: Para manejar expresiones regulares para identificar archivos.

#### Lenguajes Detectados

El proyecto 'autoreadme' soporta el análisis de varios lenguajes de programación, incluyendo Python, Java, JavaScript/TypeScript, Go, Rust, Ruby y C. Estos lenguajes son detectados automáticamente basándose en las extensiones del archivo.

#### Generación del README.md

El proceso principal para generar un README.md se divide en varias etapas:

1. **Carga del Repositorio Git**: El script recoge el contenido del repositorio Git, incluyendo archivos específicos y directorios.
2. **Analisis de Archivos**: Utiliza el analizador `analyzer.py` para extraer información sobre los archivos y estructuras del proyecto.
3. **Generación del Diagrama de Arquitectura**: El script utiliza el generador `generator.py` para construir un diagrama de arquitectura basado en los datos obtenidos.
4. **Extraer Información sobre Bases de Datos y Servicios**: El script analiza las rutas de API y bases de datos del código fuente para extraer información relevante.
5. **Generar el README.md**: Finalmente, el script utiliza la biblioteca `jinja2` para generar un archivo README.md basado en un template proporcionado.

#### Ejecución del Proyecto

Para ejecutar el proyecto, se requiere instalar las dependencias de Python utilizando pip:

```bash
pip install -r requirements.txt
```

Una vez instaladas las dependencias, se puede correr el script principal usando la siguiente命令:

```bash
python autoreadme/cli.py generate
```

Este comando generará un README.md basado en los datos disponibles en el repositorio Git.

#### Desarrollo y Mantenimiento

El proyecto 'autoreadme' se desarrolla utilizando Python, con una estructura modular y orientada a objetos. Se utiliza la biblioteca `click` para crear interfaces de comando simples y la biblioteca `jinja2` para generar archivos Markdown. El código está escrito en un estilo fácil de entender y mantenible, con comentarios claros para explicar el propósito de cada parte del proyecto.

El proyecto se mantiene actualizado añadiendo nuevas funcionalidades, mejorando la eficiencia y la calidad del resultado, así como actualizando las dependencias para adaptarse a los cambios en los lenguajes de programación más recientes.


## 🏗️ System Architecture

```
### Diagrama ASCII Profesional del Proyecto 'autoreadme'

```
+---------------------+
| Autoreadme           |
+---------------------+
     |
     v
+---------------------+
| CLI                 |
+---------------------+
     |
     v
+---------------------+
| Generator            |
+---------------------+
     |
     v
+---------------------+
| LLMProvider          |
+---------------------+
```

#### Capas del Proyecto:

1. **CLI** (Command Line Interface):
   - Funciones: `load_config`, `save_config`
   - Clases: `cli`

2. **Generator**:
   - Funciones: `generate_readme`
   - Clases: `generator`

3. **LLMProvider**:
   - Funciones: `get_provider`
   - Clases: `llm`

#### Módulos del Proyecto:

- **autoreadme/cli.py**
  - Functions: `load_config`, `save_config`, `cli`, `config`, `config_show`, `config_set_key`, `config_set_provider`, `config_set_model`, `progress_callback`
  
- **autoreadme/generator.py**
  - Functions: `_build_context_texts`, `_generate_architecture_diagram`, `_enrich_routes`, generate_readme, _safe_basename

- **autoreadme/llm/__init__.py**
  - Functions: 
  - Classes: 

- **autoreadme/llm/factory.py**
  - Functions: `get_provider`
  - Classes: 

- **autoreadme/llm/openai_provider.py**
  - Functions: __init__, chat
  
- **autoreadme/llm/ollama_provider.py**
  - Functions: __init__, chat
  
- **autoreadme/llm/anthropic_provider.py**
  - Functions: __init__, chat
  
- **autoreadme/llm/gemini_provider.py**
  - Functions: __init__, chat
  
- **autoreadme/llm/base.py**
  - Functions: to_dict, parse, _extract, build_llm_prompt

- **autoreadme/languages/java.py**
  - Functions: `_extract`
  
- **autoreadme/languages/registry.py**
  - Functions: get_parser_for_file
  
- **autoreadme/languages/ruby.py**
  - Functions: _extract
  
- **autoreadme/languages/python.py**
  - Functions: _extract
  
- **autoreadme/languages/go.py**
  - Functions: _extract
 
- **autoreadme/languages/javascript.py**
  - Functions: _extract

- **autoreadme/languages/base.py**
  - Functions: to_dict, parse, _extract, build_llm_prompt
```
```



## 📁 Project Structure


### `autoreadme/`


#### `analyzer.py`  *(Python)*

**Functions:** _load_gitignore, _collect_files, _read_content, _analyze_file, analyze_project, _load_package_json, _load_pyproject_toml, _load_go_mod, ...
  **Classes:** ProjectData



El archivo `analyzer.py` es un programa diseñado para analizar proyectos de desarrollo en múltiples lenguajes utilizando LLMs para generar descripciones detalladas de los archivos y estructuras del proyecto. Aquí está una versión resumida del código fuente:

### Propósito del Archivo
El archivo `analyzer.py` es un programa que permite realizar un análisis exhaustivo de un proyecto, identificando v...


#### `__init__.py`  *(Python)*



  **Exports:** analyze_project, generate_readme, get_provider, ProjectData, __version__


### Resumen Técnico del Archivo Python

El archivo `autoreadme` es un script diseñado para generar automáticamente los archivos README de proyectos basados en la información y funciones disponibles en su códigobase. Es una herramienta potente que utiliza AI para analizar el contenido del proyecto, identificar las características, descripciones y dependencias principales, y luego genera un archivo ...


#### `cli.py`  *(Python)*

**Functions:** load_config, save_config, cli, config, config_show, config_set_key, config_set_provider, config_set_model, ...




El código proporcionado se refiere a un script de línea de comandos llamado `autoreadme`, diseñado para generar READMEs profesionales basados en los archivos y estructura del proyecto actual. El archivo está escrito en Python utilizando la biblioteca `click` para crear una interfaz de comando simple.

### ¿Qué hace el script?

1. **Configuración**:
   - El script permite cargar y modificar una con...


#### `generator.py`  *(Python)*

**Functions:** _build_context_texts, _generate_architecture_diagram, _enrich_routes, generate_readme, _safe_basename




### Resumen Técnico del Archivo `generator.py`

#### Propósito General
El archivo `generator.py` es un script que utiliza Jinja2 y una LLM RAG para generar un README.md completo para un proyecto basado en un conjunto de datos detallados. El objetivo principal es proporcionar una visión detallada del proyecto, incluyendo su arquitectura, propósito técnico, módulos principales y dependencias clave.
...



### `autoreadme/llm/`


#### `__init__.py`  *(Python)*



  **Exports:** LLMProvider, get_provider


Resumen técnico en castellano:

Este archivo Python se designa como una biblioteca que proporciona un sistema para implementar diferentes proveedores de lenguaje de inteligencia artificial (LLMs). Algunas de las funciones principales incluyen:

- `LLMProvider`: Una clase que representa a un provider específico de LLMs. Este objeto tiene métodos para realizar solicitudes a la API del LLM y devolver...


#### `factory.py`  *(Python)*

**Functions:** get_provider




### Resumen Técnico del Código Python proporcionado

#### Introducción
El código proporcionado es un módulo en Python que define una clase `LLMProvider` y una función `get_provider`. Esta clase y la función son diseñadas para encapsular el manejo de diferentes proveedores de lenguaje automático (LLMs), permitiendo la creación de instancias específicas de estos provedores según las necesidades del ...


#### `openai_provider.py`  *(Python)*

**Functions:** __init__, chat
  **Classes:** OpenAIProvider



### Resumen Técnico

El archivo proporcionado define una clase llamada `OpenAIProvider` que extiende la clase base `LLMProvider`. Este provider se utiliza para comunicarse con las APIs de OpenAI, específicamente con sus modelos de generación de texto (GPT). 

**Características Principales del Archivo:**

1. **Imports e Inicialización:**
   - Se importan las bibliotecas `os` y `openai`.
   - La cla...


#### `ollama_provider.py`  *(Python)*

**Functions:** __init__, chat
  **Classes:** OllamaProvider



### Resumen Técnico

Este código es una implementación de una clase `OllamaProvider` que se utiliza para proporcionar servicios de lenguaje basados en el modelo Ollama. El archivo está diseñado para ser ejecutado localmente y no requiere una API key.

#### Propósito del Archivo
- **Provee una implementación de un proveedor de servicio de lenguaje** utilizando el modelo `qwen2.5-coder:14b`.
- **No ...


#### `anthropic_provider.py`  *(Python)*

**Functions:** __init__, chat
  **Classes:** AnthropicProvider



Resumen técnico en castellano:

Este archivo Python es un proveedor de lenguajes de programación llamado AnthropicProvider para la biblioteca `autoreadme`. La clase principal de este provider se llama AnthropicProvider y implementa varios métodos para interactuar con el servicio de Anthropic.

El método __init__ inicializa el cliente de Anthropic, utilizando la clave API proporcionada o la que est...


#### `gemini_provider.py`  *(Python)*

**Functions:** __init__, chat
  **Classes:** GeminiProvider



El archivo proporcionado es una implementación de una clase llamada `GeminiProvider` que extiende la clase base `LLMProvider`. El propósito principal de este archivo es proporcionar un acceso a una lenguaje modelo llamado Gemini, que se utiliza para generar respuestas basadas en las preguntas o comandos ingresados por el usuario.

### Componentes principales

1. **Importaciones**:
   - `os`: Para ...


#### `base.py`  *(Python)*

**Functions:** __init__, chat, rag_chat
  **Classes:** LLMProvider



Resumen técnico en castellano:

Este archivo es un ejemplo de una clase abstracta en Python llamada `LLMProvider`. Esta clase se diseñó para proporcionar un protocolo básico para implementaciones específicas de los LLM (Lenguajes de Proceso Natural). El propósito principal de esta clase es garantizar que todas las implementaciones cumplan con ciertos requisitos, como enviar prompts y recibir respu...



### `autoreadme/languages/`


#### `java.py`  *(Python)*

**Functions:** _extract
  **Classes:** JavaParser



Resumen Técnico en Castellano:

Este código Python define una clase llamada `JavaParser` que hereda de la clase `LanguageParser`. La clase es diseñada para analizar y extracción información específica del lenguaje Java, incluyendo clases, métodos, imports, Spring/JAX-RS routes, bases de datos o servicios externos.

1. **Funciones Principales**:
   - `_extract` method: Este método se encarga de ext...


#### `registry.py`  *(Python)*

**Functions:** get_parser_for_file




### Resumen Técnico

Este código proporciona una implementación de una biblioteca para análisis de lenguajes de programación basado en diferentes formatos como JavaScript, Python, Go, Java, Rust y Ruby. El archivo contiene la definición de clases de analizador específico para cada lenguaje, así como un mapa de extensión a la clase correspondiente.

#### Clases Principales:

1. **LanguageParser**:
...


#### `__init__.py`  *(Python)*



  **Exports:** LanguageParser, FileInfo, get_parser_for_file, SUPPORTED_EXTENSIONS


### Resumen Técnico del Archivo Python

#### Proyecto:
El archivo `__init__.py` se encuentra dentro del directorio `parsers/`, especificamente en la subcarpeta `base`. El objetivo principal de este archivo es servir como un punto de entrada para el módulo `parsers.base`.

#### Funciones y Clases Principales:

1. **LanguageParser**:
   - Este es un clase que define los métodos necesarios para anali...


#### `ruby.py`  *(Python)*

**Functions:** _extract
  **Classes:** RubyParser



Resumen técnico en castellano:

Este script Python define una clase `RubyParser` que extiende la clase base `LanguageParser`. Este parser es diseñado para analizar y extraer información relevante sobre archivos Ruby, como métodos, clases, requerimientos, rutas de API, bases de datos y servicios externos.

### Funciones Principales:

1. **_extract**: Este método se encarga de buscar patrones en el ...


#### `python.py`  *(Python)*

**Functions:** _extract
  **Classes:** PythonParser



Este script es una clase de análisis basada en ASTs (Abstract Syntax Trees) para el lenguaje Python. Su principal función es extraer información detallada del código fuente, incluyendo funciones, clases, rutas API, conexiones a bases de datos y servicios externos. Aquí está un resumen técnico del archivo:

### Propósito del Archivo

El script se ha diseñado para proporcionar una visión detallada d...


#### `go.py`  *(Python)*

**Functions:** _extract
  **Classes:** GoParser



Este archivo Python define una clase `GoParser` que extiende la clase `LanguageParser`. La clase se encarga de analizar y extraer información sobre un código Go desde un archivo de texto proporcionado. A continuación, te proporciono el resumen técnico en castellano:

### Propósito del Archivo

El objetivo principal de este archivo es parsear y analizar un archivo Go (.go) para extraer información ...


#### `javascript.py`  *(Python)*

**Functions:** _extract
  **Classes:** JavaScriptParser



El archivo Python proporcionado es una implementación específica para analizar y extraer información sobre el lenguaje JavaScript/TypeScript. Aquí está un resumen técnico en castellano:

### Propósito del Archivo

El objetivo principal del archivo es proporcionar una clase de análisis personalizada llamada `JavaScriptParser` que extiende la clase base `LanguageParser`. Esta clase se utiliza para a...


#### `base.py`  *(Python)*

**Functions:** to_dict, parse, _extract, build_llm_prompt
  **Classes:** FileInfo, LanguageParser



Este es un código fuente que proporciona la estructura básica para una clase `FileInfo` que se utiliza para almacenar información detallada sobre un archivo de código fuente. También incluye una clase abstracta `LanguageParser` que define el patrón abstractor para analizar archivos específicos.

### Clase `FileInfo`

La clase `FileInfo` es un dataclass que encapsula la información extraída del arc...


#### `rust.py`  *(Python)*

**Functions:** _extract
  **Classes:** RustParser



Este archivo Python es una clase llamada `RustParser` que hereda de una clase base llamada `LanguageParser`. La tarea principal de esta clase es extraer información sobre el lenguaje Rust del código fuente proporcionado.

El archivo define varios atributos, incluyendo:

- `EXTENSIONS`: Una tupla que contiene las extensiones de archivo soportadas por este analizador.
- `LANGUAGE_NAME`: Un string qu...










## 🛠️ Dependencies

**Runtime:** click, jinja2, rich, pyyaml, pytest, pytest-cov, pathspec










---

*README generated by [autoreadme](https://github.com/autoreadme/autoreadme) 🤖*