## Proyecto de Procesamiento de Gramáticas y Algoritmo CYK
## Bryan España - 21550

VIDEO COMPLETO:  https://youtu.be/0f8WXOR2zO8

Este proyecto implementa una serie de transformaciones para convertir una gramática a Forma Normal de Chomsky (CNF) y utiliza el Algoritmo CYK para verificar si una cadena pertenece a la gramática. Está diseñado para trabajar con gramáticas libres de contexto, que pueden incluir producciones epsilon (`ε`) y producciones unitarias, y sigue una serie de pasos para limpiar y convertir la gramática antes de realizar el análisis con el Algoritmo CYK.

### Descripción General de Archivos

- **FNC.py**: Archivo principal que contiene la clase `ProcesadorGramatica` con métodos para procesar y transformar la gramática y el Algoritmo CYK para verificar pertenencia de cadenas.

---

## Estructura del Código

### Clase `ProcesadorGramatica`

Esta clase contiene métodos para transformar una gramática dada y prepararla para el análisis con el Algoritmo CYK. A continuación se describen los métodos principales:

#### 1. `leer_gramatica(file_content)`

   - **Descripción**: Lee la gramática desde una cadena (o archivo de texto) y la convierte en un diccionario donde las claves son no terminales y los valores son listas de producciones.
   - **Parámetro**: 
     - `file_content`: Una cadena que representa la gramática en formato de texto.
   - **Retorno**: Un diccionario que representa la gramática.

#### 2. `encontrar_anulables(grammar)`

   - **Descripción**: Encuentra todos los símbolos anulables, es decir, los no terminales que pueden derivar en `ε`.
   - **Parámetro**: 
     - `grammar`: Diccionario de la gramática.
   - **Retorno**: Un conjunto de símbolos anulables.

#### 3. `eliminar_epsilon(grammar)`

   - **Descripción**: Elimina las producciones epsilon (`ε`) de la gramática, manteniendo las equivalencias mediante combinaciones de los símbolos anulables.
   - **Parámetro**: 
     - `grammar`: Diccionario de la gramática.
   - **Retorno**: Diccionario de la gramática sin producciones epsilon.

#### 4. `eliminar_produccion_unitaria(grammar)`

   - **Descripción**: Elimina las producciones unitarias, que son producciones donde un no terminal deriva directamente en otro no terminal.
   - **Parámetro**: 
     - `grammar`: Diccionario de la gramática.
   - **Retorno**: Diccionario de la gramática sin producciones unitarias.

#### 5. `eliminar_no_generados(grammar)`

   - **Descripción**: Elimina símbolos que no son generadores (símbolos que no derivan en terminales) y símbolos no alcanzables desde el símbolo inicial.
   - **Parámetro**: 
     - `grammar`: Diccionario de la gramática.
   - **Retorno**: Diccionario de la gramática sin símbolos inútiles.

#### 6. `convertir_CNF(grammar)`

   - **Descripción**: Convierte la gramática en Forma Normal de Chomsky (CNF). Crea nuevas producciones binarias y reemplaza terminales en producciones mixtas.
   - **Parámetro**: 
     - `grammar`: Diccionario de la gramática.
   - **Retorno**: Diccionario de la gramática en CNF.

#### 7. `algoritmo_CYK(grammar, input_string)`

   - **Descripción**: Implementa el Algoritmo CYK para verificar si una cadena pertenece a la gramática en CNF. Utiliza una tabla triangular para almacenar derivaciones posibles y realiza el análisis de manera ascendente.
   - **Parámetros**: 
     - `grammar`: Diccionario de la gramática en CNF.
     - `input_string`: La cadena de entrada que se va a verificar.
   - **Retorno**: Un valor booleano que indica si la cadena pertenece a la gramática y la tabla CYK generada.

---

## Ejecución del Programa

La función principal para ejecutar el programa se llama `procesar_gramatica_completa(grammar_text)`. Esta función realiza los siguientes pasos:

1. **Leer la Gramática**: Convierte el texto de la gramática en un diccionario estructurado.
2. **Eliminar Producciones Epsilon**: Elimina producciones `ε` si están presentes.
3. **Eliminar Producciones Unitarias**: Elimina producciones donde un no terminal deriva directamente en otro no terminal.
4. **Eliminar Símbolos Inútiles**: Quita los símbolos no generadores y no alcanzables.
5. **Convertir a CNF**: Convierte la gramática en Forma Normal de Chomsky, creando nuevas producciones si es necesario.
6. **Verificación con CYK**: Pide al usuario una cadena y usa el Algoritmo CYK para verificar si la cadena pertenece a la gramática.

### Ejemplo de Uso

Para ejecutar el programa, puedes definir una gramática como texto en `grammar_text` y luego llamar a `procesar_gramatica_completa(grammar_text)` en la sección `__main__`. A continuación, se te pedirá que ingreses cadenas para verificar su pertenencia a la gramática.

```python
if __name__ == "__main__":
    grammar_text = """
        S → NP VP
        VP → VP PP | V NP | cooks | drinks | eats | cuts
        PP → P NP
        NP → Det N | he | she
        V → cooks | drinks | eats | cuts
        P → in | with
        N → cat | dog | beer | cake | juice | meat | soup | fork | knife | oven | spoon
        Det → a | the
    """
    print("=== Procesador de Gramática y Verificador CYK ===")
    procesar_gramatica_completa(grammar_text)
