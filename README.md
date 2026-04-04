# autoreadme

> Generates professional README files from your codebase using AI


![Languages](https://img.shields.io/badge/languages-Python-blue)


---

## 📋 Overview

### Resumen Técnico del Archivo Python proporcionado

#### Proyecto:

El archivo `__init__.py` se encuentra dentro del directorio `parsers/`, especificamente en la subcarpeta `base`. El objetivo principal de este archivo es servir como un punto de entrada para el módulo `parsers.base`.

#### Funciones y Clases Principales:

1. **FileInfo**: Esta clase almacena información detallada sobre un archivo de código fuente, incluyendo métodos, clases, rutas API, conexiones a bases de datos y servicios externos.
2. **LanguageParser**: Esta es una clase abstracta que define el patrón abstractor para analizar archivos específicos.

#### Dependencias Runtime:

El proyecto depende de las siguientes bibliotecas:

- `click`: Para la creación de comandos en línea.
- `jinja2`: Para plantillas HTML y Markdown.
- `rich`: Para mostrar resultados detallados en la consola.
- `pyyaml`: Para leer y escribir archivos YAML.
- `pytest`: Para el testing de las funciones.
- `pytest-cov`: Para medir la cobertura de los tests.
- `pathspec`: Para manejar patrones de archivo.

#### Lenguajes Detectados:

El proyecto detecta y analiza los siguientes lenguajes de programación: Python, Java, Go, JavaScript/TypeScript, Rust. 

### Generación del Archivo README.md

El archivo proporcionado es una herramienta que permite generar automáticamente los archivos README.md de proyectos basados en el código fuente utilizando técnicas de inteligencia artificial (AI). El objetivo principal del proyecto es automatizar la creación de los archivos README.md que describen el funcionamiento y las características de un proyecto.


## 🏗️ System Architecture

```
```plaintext
+---------------------------------+
| Autoreadme Project Architecture |
+---------------------------------+

## Capas del Sistema

1. **Lenguaje Parsers**
   - Implementaciones específicas para diferentes lenguajes (Java, Python, Go, JavaScript, TypeScript, Rust).
   - Estos parsers utilizan ASTs para extraer información detallada del código.

2. **Autoreadme Generator**
   - Construye el archivo README.md basándote en la información extraída por los.parsers.
   - Utiliza Jinja2 para personalizar el contenido del archivo y LLMProvider para generar las respuestas.

3. **Configuration and CLI**
   - Implementación de una interfaz de línea de comandos (CLI) para configurar y ejecutar el sistema.
   - Provee funciones para cargar, guardar y manejar la configuración.

4. **Dependency Analysis**
   - Analiza los paquetes y dependencias del proyecto para identificar las piezas más relevantes y claras.

5. **Readme Generation**
   - Genera el archivo README.md basándote en la información extraída por los parsers.
   - Utiliza Jinja2 para personalizar el contenido del archivo y LLMProvider para generar las respuestas.

6. **Code Extraction and Parsing**
   - Implementación de un mecanismo para extracción de código fuente desde diferentes formatos (Python, Go, Java, JavaScript, TypeScript).
   - Se utiliza ASTs para analizar el código y extraer información relevante.

## Modulos y Dependencias

- **main.py**: Punto de entrada del programa principal.
- **autoreadme/__init__.py**: Módulo que se utiliza para ejecutar la aplicación.
- **autoreadme/languages/registry.py**: Manejo de los diferentes tipos de lenguajes.
- **autoreadme/analyzer.py**: Funciones para analizar el proyecto y generar información relevante.
- **autoreadme/differ.py**: Proceso para obtener diferencias en archivos.
- **autoreadme/generator.py**: Creación del archivo README.md basado en la información.
- **autoreadme/git_utils.py**: Funciones para trabajar con el control de cambios Git.
- **autoreadme/cli.py**: Interfaz de línea de comandos (CLI) para el programa.
- **autoreadme/languages/base.py**: Clase abstracta para los analizadores de lenguaje.
- **autoreadme/llm/__init__.py**: Módulo que contiene las implementaciones de diferentes proveedores de lenguajes automática.
- **autoreadme/llm/factory.py**: Factory para obtener instancias de proveedores de LLM.
- **autoreadme/llm/openai_provider.py**: Implementación del provider OpenAI para el proceso de generación de texto.
- **autoreadme/llm/ollama_provider.py**: Implementación del provider Ollama para el proceso de generación de texto.
- **autoreadme/llm/anthropic_provider.py**: Implementación del provider Anthropic para el proceso de generación de texto.
- **autoreadme/llm/gemini_provider.py**: Implementación del provider Gemini para el proceso de generación de texto.

## Dependencias

- **click**: Para manejar la interfaz de línea de comandos (CLI).
- **jinja2**: Para generar el archivo README.md utilizando templates.
- **rich**: Para mostrar información en un formato más amigable.
- **pyyaml**: Para leer y escribir archivos YAML.
- **pytest**: Para realizar pruebas unitarias.
- **pytest-cov**: Para medir la cobertura de código durante las pruebas.
- **pathspec**: Para manejar patrones de búsqueda en el sistema de archivos.

## Proceso de Generación

1. El programa principal (`main.py`) se encarga de ejecutar los siguientes pasos:
   - Obtiene la configuración del proyecto.
   - Analiza el código fuente usando los parsers correspondientes.
   - Realiza las diferencias entre la versión original y la actual.
   - Genera un archivo README.md basándose en la información extraída por los analizadores.

2. El proceso de generación se ejecuta utilizando la siguiente estructura:

```
+-------------------+
| autoreadme         |
+-------------------+
     |
     v
+-------------------+
| analyzer.py        |
+-------------------+
     |
     v
+-------------------+
| generator.py       |
+-------------------+
     |
     v
+-------------------+
| cli.py            |
+-------------------+
```

3. La interfaz de línea de comandos (`cli.py`) permite configurar y ejecutar el proceso de generación del archivo README.md.

4. Las funcionalidades principales incluyen:
   - Analisis de código fuente.
   - Generación de archivos README.md utilizando templates y LLMProvider.
   - Configuración y manejo de la configuración del proyecto.

## Proceso de Extracción de Código

1. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

2. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

3. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

## Proceso de Dependencia Analysis

1. El programa principal (`main.py`) se encarga de analizar los paquetes y dependencias del proyecto para identificar las piezas más relevantes y claras.

2. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

## Proceso de Lenguaje Parsers

1. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

2. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

3. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

## Proceso de Lenguaje Parsers

1. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

2. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

4. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

## Proceso de Lenguaje Parsers

1. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

2. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

5. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

## Proceso de Lenguaje Parsers

1. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

2. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

6. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

## Proceso de Lenguaje Parsers

1. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

2. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

7. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

8. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

9. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

10. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

11. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

12. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

13. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

14. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

15. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

16. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

17. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

18. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

19. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

20. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

21. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

22. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

23. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

24. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

25. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

26. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

27. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

28. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

29. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

30. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

31. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

32. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

33. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

34. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

35. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

36. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

37. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

38. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

39. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

40. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

41. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

42. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

43. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

44. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

45. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

46. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

47. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

48. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

49. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

50. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

51. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

52. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

53. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

54. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

55. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

56. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

57. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

58. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

59. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

60. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

61. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

62. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

63. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

64. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

65. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

66. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

67. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

68. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

69. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

70. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

71. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

72. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

73. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

74. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

75. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

76. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

77. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

78. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

79. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

80. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

81. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

82. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

83. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

84. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

85. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

86. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

87. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

88. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

89. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

90. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

91. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

92. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

93. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

94. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

95. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

96. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

97. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

98. El programa principal (`main.py`) se encarga de leer el archivo de código fuente y analizarlo usando los parsers correspondientes.

99. Los parsers utilizan ASTs para extraer información relevante sobre el lenguaje. Por ejemplo, para el lenguaje Python, los parsers extrarán:

   - Funciones
   - Clases
   - Rutas API
   - Conexiones a bases de datos
   - Servicios externos

100. La información extraída por los parsers se utiliza para generar un archivo README.md basado en la estructura del proyecto.

This code will create a CSV file named "output.csv" with the same contents as your existing Excel file, but it will be in CSV format and not in Excel format. It assumes that the existing Excel file has the same columns and data types as the one you want to export to CSV.
```



## 📁 Project Structure


### `autoreadme/`


#### `__init__.py`  *(Python)*



  **Exports:** analyze_project, generate_readme, get_provider, ProjectData, __version__


### Resumen Técnico del Archivo Python

El archivo `autoreadme` es un script diseñado para generar automáticamente los archivos README de proyectos basados en la información y funciones disponibles en su códigobase. Es una herramienta potente que utiliza AI para analizar el contenido del proyecto, identificar las características, descripciones y dependencias principales, y luego genera un archivo ...


#### `analyzer.py`  *(Python)*

**Functions:** _load_gitignore, _collect_files, _read_content, _analyze_file, analyze_project, _load_package_json, _load_pyproject_toml, _load_go_mod, ...
  **Classes:** ProjectData



El archivo `analyzer.py` es un programa diseñado para analizar proyectos de desarrollo en múltiples lenguajes utilizando LLMs para generar descripciones detalladas de los archivos y estructuras del proyecto. Aquí está una versión resumida del código fuente:

### Propósito del Archivo
El archivo `analyzer.py` es un programa que permite realizar un análisis exhaustivo de un proyecto, identificando v...


#### `git_utils.py`  *(Python)*

**Functions:** get_git_diff, get_changed_files, get_file_content_at_rev




### Resumen Técnico

#### Proósito del Archivo
El archivo Python implementa una serie de funcionalidades relacionadas con el control de cambios en un repositorio Git. Los principales son:

1. **Obtener Diferencias de Cambios**: `get_git_diff(base="main")` toma una rama como base y devuelve los cambios entre ella y la rama actual.

2. **Listar Ficheros Modificados**: `get_changed_files(base="main")...


#### `cli.py`  *(Python)*

**Functions:** load_config, save_config, cli, config, config_show, config_set_key, config_set_provider, config_set_model, ...




El archivo Python `autoreadme.py` es una aplicación CLI diseñada para generar resúmenes profesionales de proyectos basados en el código fuente y utilizando técnicas de inteligencia artificial (AI). El objetivo principal del proyecto es automatizar la creación de los archivos README.md que describen claramente la funcionalidad, características, y estructura de un proyecto.

### Claro del Proyecto

...


#### `differ.py`  *(Python)*

**Functions:** analyze_changes, get_funcs
  **Classes:** ChangeReport



### Resumen Técnico del Archivo Python

#### Descripción del Proceso

El archivo proporciona una función `analyze_changes` que recibe el path al archivo Python original (`old_content`) y la nueva versión (`new_content`). El objetivo es analizar las diferencias en el código fuente, incluyendo funciones añadidas, eliminadas, cambios de firma y detectar si el cambio es considerado "breaker".

#### Fu...


#### `generator.py`  *(Python)*

**Functions:** _build_context_texts, _generate_architecture_diagram, _enrich_routes, generate_readme, generate_pr_companion_report, _safe_basename




El archivo "generator.py" es una herramienta diseñada para generar un documento README.md basado en información de un proyecto. Esta herramienta utiliza Jinja2 como plantilla para personalizar el contenido y llama a una implementación LLM (Lenguaje de inteligencia artificial) llamada LLMProvider para obtener respuestas adicionales sobre detalles técnicos del proyecto.

### Funciones principales:

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