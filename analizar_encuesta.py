"""
Analiza la encuesta social del curso de Infra y genera:

  - Gráficos de barras (con matplotlib) para las preguntas de opción múltiple.
  - Una página web (output/index.html) con esos gráficos y las respuestas
    de las preguntas de texto libre.

Para correrlo:
    python3 analizar_encuesta.py

El resultado queda en la carpeta output/ (se puede abrir output/index.html
directamente en el navegador, sin necesidad de servidor).
"""

import csv
import html
import textwrap
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Rutas de archivos
# ---------------------------------------------------------------------------

CARPETA_BASE = Path(__file__).parent
ARCHIVO_CSV = CARPETA_BASE / "data" / "encuesta.csv"
CARPETA_SALIDA = CARPETA_BASE / "output"
CARPETA_GRAFICOS = CARPETA_SALIDA / "graficos"

# ---------------------------------------------------------------------------
# Preguntas de opción (única o múltiple) que vamos a graficar.
# Cada una es: (columna en el csv, título del gráfico, archivo .png, tipo)
# tipo = "unica"    -> el alumno eligió una sola opción
# tipo = "multiple" -> el alumno pudo elegir varias, separadas por comas
# ---------------------------------------------------------------------------

PREGUNTAS_GRAFICO = [
    (
        "¿Cuál consideras que es tu nivel previo en programación?",
        "Nivel previo en programación",
        "nivel_previo.png",
        "unica",
    ),
    (
        "¿Has tenido contacto previo con algún lenguaje de programación? (Puedes marcar varios)",
        "Lenguajes de programación conocidos",
        "lenguajes.png",
        "multiple",
    ),
    (
        "¿Cuál crees que será tu mayor desafío a la hora de aprender a programar?",
        "Mayor desafío percibido",
        "desafio.png",
        "unica",
    ),
    (
        "¿Trabajas en el campo de la tecnología (IT)?",
        "¿Trabaja actualmente en el campo de IT?",
        "trabaja_it.png",
        "unica",
    ),
    (
        "Edad:",
        "Edad",
        "edad.png",
        "unica",
    ),
    (
        "Ocupación:",
        "Ocupación",
        "ocupacion.png",
        "multiple",
    ),
    (
        "Gustos e Intereses (pueden ser múltiples):",
        "Gustos e intereses",
        "gustos.png",
        "multiple",
    ),
    (
        "Provincia",
        "Provincia",
        "provincia.png",
        "unica",
    ),
]

# La provincia se escribió con mayúsculas/minúsculas distintas y sin tildes
# (ej: "Buenos Aires", "BUENOS AIRES", "Cordoba ", "Neuquen"). Acá la
# normalizamos para que no queden separadas en el gráfico como si fueran
# lugares distintos, y unificamos "Capital Federal" con "CABA".
NORMALIZACION_PROVINCIA = {
    "buenos aires": "Buenos Aires",
    "capital federal": "CABA",
    "caba": "CABA",
    "cordoba": "Córdoba",
    "córdoba": "Córdoba",
    "tucuman": "Tucumán",
    "tucumán": "Tucumán",
    "neuquen": "Neuquén",
    "neuquén": "Neuquén",
    "la rioja": "La Rioja",
    "santa cruz": "Santa Cruz",
}

# Preguntas de texto libre: se muestran como listado de respuestas, no se grafican.
PREGUNTAS_TEXTO_LIBRE = [
    (
        "¿Qué tipo de contenido te gustaría ver en futuras clases o actividades?"
        "Que temas te interesan para ver en la materia Programación 1. "
        "Que Programas te gustaría realizar ?",
        "Contenido que les gustaría ver en clase",
    ),
    (
        "¿Tienes alguna sugerencia para mejorar el ambiente en clase?",
        "Sugerencias para mejorar el ambiente en clase",
    ),
    (
        "¿Que te parece que se puede hacer para incentivar uso de las camaras en las clases?",
        "Ideas para incentivar el uso de cámaras",
    ),
    (
        "Algún libro / video / documento sobre IT que te gustó para recomendar ?",
        "Recomendaciones de IT (libros, videos, documentos)",
    ),
    (
        "Libros o películas en general para recomendar?",
        "Recomendaciones de libros o películas",
    ),
    (
        "Pregunta abierta, considera poner lo que quieras..",
        "Pregunta abierta",
    ),
]


# ---------------------------------------------------------------------------
# Lectura de datos
# ---------------------------------------------------------------------------

def leer_respuestas():
    """Lee el CSV de la encuesta y devuelve una lista de diccionarios (uno por alumno)."""
    with open(ARCHIVO_CSV, encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        return list(lector)


# ---------------------------------------------------------------------------
# Conteo de respuestas
# ---------------------------------------------------------------------------

def contar_opcion_unica(respuestas, columna):
    """Cuenta cuántas veces aparece cada valor en una columna de opción única."""
    valores = (fila[columna].strip() for fila in respuestas)
    valores = (v for v in valores if v)

    if columna == "Provincia":
        valores = (NORMALIZACION_PROVINCIA.get(v.lower(), v) for v in valores)

    return Counter(valores)


def contar_opcion_multiple(respuestas, columna):
    """Cuenta cada opción por separado en columnas donde se eligió más de una,
    separadas por comas (ej: "Python, JavaScript, HTML / CSS (Desarrollo Web)")."""
    contador = Counter()
    for fila in respuestas:
        valor = fila[columna].strip()
        if not valor:
            continue
        opciones = [o.strip() for o in valor.split(",")]
        contador.update(o for o in opciones if o)
    return contador


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------

def generar_grafico_barras(contador, titulo, nombre_archivo):
    """Genera un gráfico de barras horizontales a partir de un Counter y lo guarda como PNG.
    Devuelve la ruta del archivo generado (relativa a output/), para usar en el HTML."""
    items = contador.most_common()
    # Algunas respuestas son textos largos en vez de una opción corta
    # (ej: alguien que escribió su propia respuesta con sus palabras).
    # Se acortan con "…" para que no rompan el gráfico.
    etiquetas = [textwrap.shorten(etiqueta, width=55, placeholder="…") for etiqueta, _ in items]
    cantidades = [cantidad for _, cantidad in items]

    alto = max(3, len(etiquetas) * 0.6)
    plt.figure(figsize=(9, alto))
    plt.barh(etiquetas, cantidades, color="#4C72B0")
    plt.gca().invert_yaxis()  # la opción más elegida queda arriba
    plt.title(titulo)
    plt.xlabel("Cantidad de alumnos")

    ruta_completa = CARPETA_GRAFICOS / nombre_archivo
    plt.savefig(ruta_completa, bbox_inches="tight")
    plt.close()

    return ruta_completa.relative_to(CARPETA_SALIDA)


def generar_todos_los_graficos(respuestas):
    """Genera un gráfico por cada pregunta en PREGUNTAS_GRAFICO.
    Devuelve una lista de (titulo, ruta_imagen) para usar en el HTML."""
    CARPETA_GRAFICOS.mkdir(parents=True, exist_ok=True)

    graficos = []
    for columna, titulo, nombre_archivo, tipo in PREGUNTAS_GRAFICO:
        if tipo == "unica":
            contador = contar_opcion_unica(respuestas, columna)
        else:
            contador = contar_opcion_multiple(respuestas, columna)

        ruta_imagen = generar_grafico_barras(contador, titulo, nombre_archivo)
        graficos.append((titulo, ruta_imagen))

    return graficos


# ---------------------------------------------------------------------------
# Generación de la página web
# ---------------------------------------------------------------------------

def generar_html(respuestas, graficos):
    """Arma el archivo output/index.html con los gráficos y las respuestas de texto libre."""
    partes = [
        "<!DOCTYPE html>",
        '<html lang="es">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>Encuesta social - Infra (Jueves)</title>",
        "<style>",
        "body { font-family: sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }",
        "h1 { text-align: center; }",
        "h2 { border-bottom: 2px solid #4C72B0; padding-bottom: 0.3rem; margin-top: 2.5rem; }",
        "img { max-width: 100%; display: block; margin: 1rem auto; }",
        "ul { line-height: 1.5; }",
        "li { margin-bottom: 0.6rem; }",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>Encuesta social - Infra (Jueves)</h1>",
        f"<p style='text-align:center'>Total de respuestas: {len(respuestas)}</p>",
    ]

    partes.append("<h2>Gráficos</h2>")
    for titulo, ruta_imagen in graficos:
        titulo_seguro = html.escape(titulo)
        partes.append(f"<h3>{titulo_seguro}</h3>")
        partes.append(f'<img src="{ruta_imagen.as_posix()}" alt="{titulo_seguro}">')

    partes.append("<h2>Respuestas de texto libre</h2>")
    for columna, titulo in PREGUNTAS_TEXTO_LIBRE:
        respuestas_columna = [fila[columna].strip() for fila in respuestas]
        respuestas_columna = [r for r in respuestas_columna if r]

        partes.append(f"<h3>{html.escape(titulo)}</h3>")
        if respuestas_columna:
            partes.append("<ul>")
            for respuesta in respuestas_columna:
                partes.append(f"<li>{html.escape(respuesta)}</li>")
            partes.append("</ul>")
        else:
            partes.append("<p><em>Sin respuestas.</em></p>")

    partes.append("</body>")
    partes.append("</html>")

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta_html = CARPETA_SALIDA / "index.html"
    ruta_html.write_text("\n".join(partes), encoding="utf-8")
    return ruta_html


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def main():
    respuestas = leer_respuestas()
    graficos = generar_todos_los_graficos(respuestas)
    ruta_html = generar_html(respuestas, graficos)
    print(f"Listo. Abrí {ruta_html} en el navegador para ver el resultado.")


if __name__ == "__main__":
    main()
