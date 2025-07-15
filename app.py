from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import re

app = Flask(__name__)  # Crea la aplicación Flask.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_RECETAS = os.path.join(BASE_DIR, "recetas.json")  # Ruta donde se guardan las recetas.

# Función para cargar las recetas existentes
def cargar_recetas():
    if os.path.exists(RUTA_RECETAS):
        with open(RUTA_RECETAS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Función para guardar las recetas
def guardar_recetas(recetas):
    with open(RUTA_RECETAS, "w", encoding="utf-8") as f:
        json.dump(recetas, f, indent=4, ensure_ascii=False)

# Cargar recetas al iniciar la app (se puede recargar si quieres, pero con esta está bien)
recetas = cargar_recetas()

# Función para buscar palabras en texto ignorando mayúsculas y signos de puntuación
def contiene_palabra(mensaje, lista_palabras):
    mensaje = mensaje.lower()
    mensaje = re.sub(r'[^\w\s]', '', mensaje)  # Quita signos de puntuación
    palabras = mensaje.split()
    for palabra in lista_palabras:
        palabra = palabra.lower()
        if palabra in palabras:
            return True
    return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/formulario")
def formulario():
    return render_template("formulario.html")

@app.route("/guardar_receta", methods=["POST"])
def guardar_receta():
    titulo = request.form["titulo"]
    ingredientes = request.form["ingredientes"]
    preparacion = request.form["preparacion"]

    recetas = cargar_recetas()  # Recarga recetas para no perder datos

    nueva_receta = {
        "titulo": titulo,
        "ingredientes": ingredientes,
        "preparacion": preparacion,
    }
    recetas.append(nueva_receta)
    guardar_recetas(recetas)

    return redirect(url_for("home"))

@app.route("/enviar_mensaje", methods=["POST"])
def enviar_mensaje():
    data = request.get_json()
    mensaje_usuario = data.get("mensaje", "").lower()

    saludos = ["hola", "buenos días", "buenas tardes", "buenas noches", "qué tal", "hey"]
    despedidas = ["adiós","Adios", "hasta luego", "nos vemos", "chao", "bye"]
    agradecimientos = ["gracias", "muchas gracias", "gracias amigo", "gracias bot"]
    crear_recetas = ["añadir", "crear", "meter", "agregar"]

    # Responder saludos y despedidas
    if contiene_palabra(mensaje_usuario, saludos):
        respuesta = "¡Hola! ¿En qué puedo ayudarte? Puedo buscar recetas o añadir una nueva."
        return jsonify({"respuesta": respuesta})

    if contiene_palabra(mensaje_usuario, despedidas):
        respuesta = "¡Hasta luego! ¡Que tengas un buen día!"
        return jsonify({"respuesta": respuesta})

    if any(agradecimiento in mensaje_usuario for agradecimiento in agradecimientos):
        respuesta = "¡De nada! Siempre aquí para ayudarte 😊"
        return jsonify({"respuesta": respuesta})

    # Añadir receta
    if contiene_palabra(mensaje_usuario, crear_recetas):
       respuesta = "Perfecto, puedes añadir una nueva receta en el formulario"
       return jsonify({"respuesta": respuesta})

    stopwords = {
    # Artículos definidos e indefinidos
    "el", "la", "los", "las", "un", "una", "unos", "unas",

    # Preposiciones comunes
    "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde", "en", "entre",
    "hacia", "hasta", "para", "por", "según", "sin", "so", "sobre", "tras",

    # Pronombres personales y posesivos
    "yo", "tú", "él", "ella", "ello", "nosotros", "vosotros", "ellos", "ellas",
    "me", "te", "se", "nos", "os", "mi", "mis", "tu", "tus", "su", "sus",
    "nuestro", "nuestra", "nuestros", "nuestras", "vos", "vosotras", "vosotros",

    # Adverbios y otros términos comunes
    "ahí", "aquí", "allí", "allá", "así", "bien", "casi", "cómo", "cuándo", "dónde",
    "más", "menos", "muy", "nada", "nunca", "otra", "otras", "otro", "otros", "porqué",
    "qué", "quién", "quienes", "sí", "también", "tan", "tanto", "ya",

    # Verbos comunes auxiliares y funcionales
    "ser", "estar", "haber", "tener", "hacer", "poder", "deber", "querer", "saber",

    # Palabras funcionales varias y modismos que no aportan en búsqueda
    "quiero", "conmigo", "contiene", "contener", "lleve", "llevar", "lleva",
    "desde", "durante", "mediante", "excepto", "incluso", "salvo", "versus", "vía",

    # Conjunciones y palabras de enlace
    "y", "e", "o", "u", "pero", "sino", "aunque", "porque", "pues", "que",

    # Otros comunes
    "todo", "todos", "todas", "cada", "cual", "cuales", "cualquier", "cuanto",
    "cuanta", "cuantas", "uno", "una", "unos", "unas", "algo", "algunos", "algunas",
      "a", "acá", "ahí", "al", "algo", "algunas", "algunos", "allá", "allí", "ambos", "ante",
    "antes", "aquel", "aquella", "aquellas", "aquello", "aquellos", "aqui", "aquí", "arriba",
    "así", "atrás", "aun", "aunque", "bajo", "bastante", "bien", "cabe", "cada", "casi", "como",
    "con", "conmigo", "conocer", "consideró", "contiene", "contener", "contra", "cual", "cuales",
    "cualquier", "cuando", "cuanto", "cuanta", "cuantas", "de", "del", "demasiada", "demasiado",
    "dentro", "desde", "donde", "dos", "durante", "el", "ella", "ellas", "ellos", "emplear",
    "en", "encima", "entonces", "entre", "era", "erais", "eran", "eras", "eres", "es", "esa",
    "esas", "ese", "eso", "esos", "esta", "estaba", "estado", "estáis", "estamos", "estan", "estar",
    "estará", "estas", "este", "esto", "estos", "estoy", "estuve", "ex", "existe", "existen",
    "explicó", "fue", "fueron", "fuese", "fui", "fuimos", "gran", "grande", "grandes", "ha",
    "haber", "había", "habían", "habrá", "habrán", "hacer", "hace", "hacen", "hacerlo", "hasta",
    "hay", "haya", "he", "hemos", "hice", "hicieron", "hizo", "hubo", "igual", "incluso",
    "intentó", "ir", "jamás", "junto", "la", "lado", "las", "le", "les", "lo", "los", "luego",
    "mal", "más", "me", "menos", "mi", "mía", "mías", "mientras", "mio", "míos", "mis", "misma",
    "mismo", "mismos", "modo", "mucho", "muchos", "muy", "nada", "ni", "ninguna", "ninguno",
    "no", "nos", "nosotras", "nosotros", "nuestra", "nuestras", "nuestro", "nuestros", "nunca",
    "o", "os", "otra", "otras", "otro", "otros", "para", "pero", "poco", "por", "porque", "qué",
    "que", "quien", "quienes", "sabe", "saber", "se", "sea", "sean", "según", "ser", "si", "sí",
    "siempre", "sin", "sino", "sobre", "sois", "solamente", "somos", "son", "soy", "su", "sus",
    "tal", "también", "tampoco", "tan", "tanto", "te", "tendré", "tendrá", "tenemos", "tener",
    "tenido", "tercero", "ti", "tiene", "tienen", "todo", "todos", "tras", "tu", "tú", "tus",
    "tuve", "tuvimos", "tuvo", "un", "una", "uno", "unos", "vosotras", "vosotros", "vuestra",
    "vuestras", "vuestro", "vuestros", "y", "ya", "yo", "quiero", "lleve", "llevar", "lleva"
}


    # Limpiar mensaje y eliminar signos de puntuación
    palabras_usuario = set(re.sub(r'[^\w\s]', '', mensaje_usuario).split())
    palabras_usuario = {p for p in palabras_usuario if p not in stopwords}

    recetas_encontradas = []
    for receta in cargar_recetas():
        titulo = receta.get("titulo", "").lower()

        # Buscar que todas las palabras importantes estén en el título
        if all(palabra in titulo for palabra in palabras_usuario):
            recetas_encontradas.append(receta) 

    if recetas_encontradas:
        respuesta = ""
        for rec in recetas_encontradas:
            respuesta += (f"Claro, aquí tienes la receta: {rec['titulo']}\n"
                          f"Ingredientes: {rec['ingredientes']}\n"
                          f"Preparación: {rec['preparacion']}\n\n")
    else:
        respuesta = "No encontré ninguna receta que coincida con tu búsqueda."

    return jsonify({"respuesta": respuesta})

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port)
    
