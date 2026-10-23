# Guía de clase: Scripting y conexión de programas mediante pipes

*Material de apoyo para la clase de Scripting*

## 1. ¿Qué es un lenguaje de scripting?

Un **lenguaje de scripting** es un lenguaje pensado para escribir *scripts*: programas relativamente cortos que automatizan tareas, coordinan otras herramientas o personalizan el comportamiento de un software existente. Suelen compartir algunas características:

- **Se ejecutan mediante un intérprete**, sin necesidad de un ciclo explícito de compilación. Se escribe, se ejecuta y se prueba de inmediato.
- **Son de alto nivel**: ofrecen cadenas, listas, diccionarios, expresiones regulares y acceso al sistema operativo con muy poco código.
- **Priorizan la productividad del programador** por encima del rendimiento de ejecución.
- **Tienen buen soporte para interactuar con el entorno**: archivos, procesos, variables de entorno, red.

La frontera con los lenguajes "de programación general" es difusa. Python, por ejemplo, se usa tanto para scripts de veinte líneas como para aplicaciones grandes. Por eso conviene pensar el *scripting* más como **una forma de uso** que como una categoría estricta de lenguajes.

Ejemplos conocidos: **Bash** y otros shells, **Python**, **Perl**, **Ruby**, **Lua**, **PowerShell**, **Tcl**, **AWK**, **JavaScript**, **VBA** (macros de Office) y **AppleScript**.

## 2. ¿Para qué se usan?

Hay tres grandes familias de aplicación.

### 2.1 Propósitos específicos

Tareas puntuales que sería excesivo resolver con un programa "formal":

- Renombrar o reorganizar miles de archivos.
- Procesar y transformar archivos de texto, logs o CSV.
- Generar reportes periódicos.
- Hacer backups, limpiar directorios temporales, rotar logs.
- Despliegues e instalaciones automatizadas.

Es el terreno clásico de Bash, Perl y Python: unas pocas líneas reemplazan horas de trabajo manual.

### 2.2 Automatización o extensión de un software particular

Muchas aplicaciones incluyen un lenguaje de scripting embebido para que el usuario las automatice o extienda:

- **VBA** en Excel y Word, para automatizar planillas y documentos.
- **JavaScript** en el navegador, para dar comportamiento a las páginas web.
- **Lua** en videojuegos y herramientas como Nginx o Neovim.
- **Python** en Blender, GIMP, FreeCAD o QGIS.
- **Lenguajes de macros** en editores de texto y suites ofimáticas.

Aquí el script no es un programa independiente: vive *dentro* de otra aplicación y accede a sus objetos y funciones.

### 2.3 Conexión entre diferentes programas ("glue language")

Uno de los usos más importantes: **pegar** programas que no fueron diseñados para trabajar juntos. Cada programa hace bien una cosa, y el script los coordina: lanza procesos, les pasa datos, recoge los resultados y decide qué hacer a continuación.

Esta es la idea central de la filosofía Unix: *programas pequeños, que hacen una sola cosa y se comunican mediante texto*. El mecanismo de comunicación por excelencia son los **pipes** (tuberías), y es lo que practicaremos en el ejercicio de la siguiente sección.

## 3. Concepto clave: entrada estándar, salida estándar y pipes

Todo proceso en un sistema Unix/Linux arranca con tres canales de comunicación abiertos:

| Canal | Nombre | Descriptor | Por defecto |
| --- | --- | --- | --- |
| `stdin` | entrada estándar | 0 | teclado |
| `stdout` | salida estándar | 1 | pantalla |
| `stderr` | salida de errores | 2 | pantalla |

Un **pipe** conecta la `stdout` de un proceso con la `stdin` de otro, de modo que lo que el primero escribe es lo que el segundo lee. En el shell se expresa con el símbolo `|`:

```bash
programa1 | programa2 | programa3
```

Ningún programa necesita saber con quién está conectado. Cada uno simplemente lee de `stdin` y escribe en `stdout`. Esa es la razón por la que programas escritos en lenguajes distintos pueden combinarse libremente.

## 4. Ejercicio: conectar dos programas mediante un pipe

Vamos a construir un pequeño sistema de tres piezas:

- **`griton.py`**: lee líneas y las devuelve en mayúsculas con un signo de exclamación.
- **`timido.py`**: lee líneas y las devuelve en minúsculas, entre puntos suspensivos.
- **`main.py`**: un script "coordinador" que lanza a los dos anteriores, los conecta entre sí y les envía un mensaje.

El flujo de datos es el siguiente:

```
  main.py ──mensaje──▶ griton.py ──pipe──▶ timido.py ──resultado──▶ main.py
            (stdin)    (stdout)    (stdin)    (stdout)    (lee la línea)
```

> En este ejercicio usamos Python por comodidad, pero `griton` y `timido` podrían estar escritos en Bash, Perl, Ruby o cualquier otro lenguaje, e incluso cada uno en uno distinto. Mientras lean de `stdin` y escriban en `stdout`, el resto funciona igual.

### 4.1 El programa `griton.py`

```python
#!/usr/bin/python
import sys

for line in sys.stdin:
  sys.stdout.write(line.upper().strip()+'!\n')
  sys.stdout.flush()
```

Qué hace, línea por línea:

1. `#!/usr/bin/python` es el *shebang*: le indica al sistema qué intérprete usar cuando el archivo se ejecuta directamente (`./griton.py`).
2. `for line in sys.stdin` recorre la entrada estándar línea por línea, y se bloquea esperando datos hasta que llegue una línea nueva o se cierre la entrada.
3. `line.upper().strip()` pasa el texto a mayúsculas y elimina el salto de línea y los espacios sobrantes de los extremos.
4. Se escribe el resultado seguido de `'!\n'`.
5. `sys.stdout.flush()` fuerza el envío inmediato de lo escrito (ver la nota sobre *buffering* más abajo).

### 4.2 El programa `timido.py`

```python
#!/usr/bin/python
import sys

for line in sys.stdin:
  sys.stdout.write('...'+line.lower().strip()+'...\n')
  sys.stdout.flush()
```

Es el espejo de `griton.py`: pasa el texto a minúsculas y lo rodea con puntos suspensivos.

### 4.3 Primera prueba: usando el shell

Antes de escribir código para conectarlos, probemos cada programa solo y luego con el pipe del shell. Primero hay que darles permiso de ejecución:

```bash
chmod +x griton.py timido.py main.py
```

Cada uno por separado:

```bash
echo "hola mundo" | ./griton.py
# HOLA MUNDO!

echo "HOLA MUNDO" | ./timido.py
# ...hola mundo...
```

Y ahora los dos encadenados:

```bash
echo "hola mundo" | ./griton.py | ./timido.py
# ...hola mundo!...
```

Observemos qué pasó: `griton` convirtió el texto a `H``OL``A`` ``M``U``N``DO``!` y `timido` lo recibió, lo pasó a minúsculas y le agregó los puntos suspensivos. El signo de exclamación sobrevivió: lo único que cambió fue el "volumen".

**Esto es exactamente lo que va a hacer `main.py`**, pero desde un programa en lugar de desde la línea de comandos.

### 4.4 El programa `main.py`

```python
#!/usr/bin/python
import io
import subprocess as sp

def main():
  griton = sp.Popen(
    ['./griton.py'],
    stdin=sp.PIPE,
    stdout=sp.PIPE
    )
  timido = sp.Popen(
    ['./timido.py'],
    stdin=griton.stdout,
    stdout=sp.PIPE
    )

  gritonin = io.TextIOWrapper(
    griton.stdin,
    encoding='utf-8'
  )
  timidoout = io.TextIOWrapper(
    timido.stdout,
    encoding='utf-8'
  )

  msg = 'Hola Mundo'

  print('Le digo a griton: ' + msg)
  gritonin.write(msg+'\n')
  gritonin.close()        # cierra la entrada de griton (también cierra griton.stdin)
  
  rs = timidoout.readline()
  print('Timido dice: ' + rs.strip())
  timidoout.close()       # cierra la salida de timido (también cierra timido.stdout)

  griton.wait()           # espera a que termine griton
  timido.wait()           # espera a que termine timido

if __name__ == "__main__":
  main()
```

> **Si no funciona****:**
>
> En los pipes reemplazar, puede ser `python` o `python3`
>
> ```python
> ['./griton.py'] --> ['python','griton.py']
> ['./timido.py'] --> ['python','timido.py']
> ```

#### Paso 1: lanzar a `griton`

```python
griton = sp.Popen(['./griton.py'], stdin=sp.PIPE, stdout=sp.PIPE)
```

`subprocess.Popen` crea un **nuevo proceso** que ejecuta `./griton.py`. Los parámetros `stdin=sp.PIPE` y `stdout=sp.PIPE` le piden a Python que cree un pipe para cada canal, de modo que `main.py` pueda escribir en la entrada de `griton` (`griton.stdin`) y que su salida quede disponible en `griton.stdout`.

#### Paso 2: lanzar a `timido` y conectarlo

```python
timido = sp.Popen(['./timido.py'], stdin=griton.stdout, stdout=sp.PIPE)
```

Acá está el corazón del ejercicio: en lugar de crear un pipe nuevo para la entrada de `timido`, le pasamos **`griton.stdout`**. Es el equivalente exacto del símbolo `|` en el shell. A partir de este momento, todo lo que `griton` escriba lo lee `timido` directamente, sin pasar por `main.py`.

#### Paso 3: envolver los extremos en objetos de texto

`Popen` entrega los canales como flujos de **bytes**. Para poder escribir y leer *strings* se los envuelve con `io.TextIOWrapper`:

- `gritonin` es el extremo por el que `main.py` **escribe** hacia `griton`.
- `timidoout` es el extremo por el que `main.py` **lee** lo que sale de `timido`.

#### Paso 4: enviar el mensaje y leer la respuesta

```python
gritonin.write(msg+'\n')
rs = timidoout.readline()
```

Se escribe el mensaje terminado en `\n` (el fin de línea es lo que hace que `for line in sys.stdin` entregue la línea) y luego se lee una línea del otro extremo de la cadena. `readline()` **se bloquea** hasta que `timido` produce su respuesta.

### 4.5 Ejecución y resultado esperado

```bash
./main.py
```

```
Le digo a griton: Hola mundo
Timido dice: ...hola mundo!...
```

#### Variante: usar `with` en lugar de cerrar a mano

`Popen` es un administrador de contexto: al salir del bloque `with`, Python cierra los pipes del proceso y llama a `wait()` por nosotros, incluso si ocurre una excepción. La forma básica es:

```python
with sp.Popen(['./griton.py'], stdin=sp.PIPE, stdout=sp.PIPE) as griton:
    ...
```

Aplicado al ejercicio, anidamos los dos procesos. Con `text=True` los pipes ya entregan *strings*, así que no hace falta `io.TextIOWrapper`:

```python
with sp.Popen(['./griton.py'], stdin=sp.PIPE,
              stdout=sp.PIPE, text=True) as griton:
    with sp.Popen(['./timido.py'], stdin=griton.stdout,
                  stdout=sp.PIPE, text=True) as timido:
        griton.stdin.write('Hola Mundo\n')
        griton.stdin.close()  # EOF: sin esto, se congela
        respuesta = timido.stdout.readline()
        print('Timido dice: ' + respuesta.strip())
```

Ojo: el `close()` de la entrada de `griton` sigue siendo manual. El `with` de `timido` espera a que ese proceso termine, y `timido` no termina hasta que `griton` cierre su salida, lo que no ocurre hasta que `griton` reciba EOF.

### 4.6 Notas importantes para discutir en clase

**Los procesos corren en paralelo.** `griton`, `timido` y `main` son tres procesos distintos del sistema operativo que se ejecutan a la vez. Pueden verse con `ps` mientras corre el ejercicio. La sincronización ocurre de forma natural: cada lectura se bloquea hasta que hay datos disponibles.

**Lenguajes intercambiables.** Podría reemplazarse `griton.py` por un script de Bash y el sistema seguiría funcionando:

```bash
#!/bin/bash
while read line; do
  echo "${line^^}!"
done
```

El contrato entre los programas no es el lenguaje: es el *protocolo de texto por líneas*.

**Ejecutabilidad y rutas.** El script usa rutas como `./griton.py`, así que debe ejecutarse desde el directorio donde están los archivos, y estos necesitan permiso de ejecución. Si hay problemas, una alternativa es lanzar `['python', 'griton.py']`, que no depende del shebang ni de los permisos.

### 4.7 Preguntas para reflexionar

1. ¿Qué ocurre si se elimina `sys.stdout.flush()` de `griton.py`? ¿Por qué?
2. ¿Qué pasa si se invierte el orden de la cadena, es decir, si `timido` va primero y `griton` después? ¿Cuál es el resultado final?
3. ¿Qué diferencia hay entre esta cadena y ejecutar `griton` y `timido` uno después del otro, guardando el resultado intermedio en un archivo?
4. ¿Qué ventajas tiene conectar los procesos mediante pipes frente a escribir todo en un único programa?

### 4.8 Ejercicios propuestos

1. **Enviar varios mensajes.** Modificar `main.py` para enviar tres mensajes distintos y mostrar las tres respuestas (hay que repetir `write` + `readline`).
2. **Agregar un tercer programa.** Crear `eco.py`, que repita cada línea dos veces, e insertarlo en la cadena entre `griton` y `timido`.
3. **Cambiar de lenguaje.** Reescribir `timido` en Bash o en Perl, sin tocar `main.py`, y verificar que el resultado es el mismo.
4. **Usar herramientas del sistema.** Reemplazar `griton.py` por un comando existente, por ejemplo `tr 'a-z' 'A-Z'`, y comprobar que `main.py` funciona con un programa que no fue escrito para este ejercicio.
5. **Manejar el cierre.** Cerrar `gritonin` después de enviar el mensaje y observar cómo termina la cadena de procesos.

## 5. Resumen

- Los lenguajes de scripting priorizan la rapidez de desarrollo y la facilidad para interactuar con el entorno.
- Se aplican a **tareas específicas**, a la **automatización o extensión de software particular** y a la **conexión entre programas**.
- Los **pipes** conectan la salida de un proceso con la entrada de otro, permitiendo combinar programas pequeños, incluso escritos en lenguajes distintos.
- Python (a través de `subprocess`) puede hacer desde un programa lo mismo que el shell hace con `|`.
