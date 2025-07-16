from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import re
import unicodedata

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_RECETAS = os.path.join(BASE_DIR, "recetas.json")

def cargar_recetas():
    if os.path.exists(RUTA_RECETAS):
        with open(RUTA_RECETAS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_recetas(recetas):
    with open(RUTA_RECETAS, "w", encoding="utf-8") as f:
        json.dump(recetas, f, indent=4, ensure_ascii=False)

def limpiar_texto(texto):
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return re.sub(r'[^\w\s]', '', texto)

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

    recetas = cargar_recetas()
    recetas.append({
        "titulo": titulo,
        "ingredientes": ingredientes,
        "preparacion": preparacion
    })
    guardar_recetas(recetas)

    return redirect(url_for("home"))

@app.route("/enviar_mensaje", methods=["POST"])
def enviar_mensaje():
    data = request.get_json()
    mensaje_usuario = data.get("mensaje", "")
    mensaje_limpio = limpiar_texto(mensaje_usuario)

    # Respuestas predefinidas
    saludos = ["hola", "buenos dias", "buenas tardes", "buenas noches", "que tal", "hey"]
    despedidas = ["adios", "hasta luego", "nos vemos", "chao", "bye"]
    agradecimientos = ["gracias", "muchas gracias", "gracias amigo", "gracias bot"]
    crear_recetas = ["añadir", "crear", "meter", "agregar"]

    if any(saludo in mensaje_limpio for saludo in saludos):
        return jsonify({"respuesta": "¡Hola! ¿En qué puedo ayudarte? Puedo buscar recetas o añadir una nueva."})

    if any(despedida in mensaje_limpio for despedida in despedidas):
        return jsonify({"respuesta": "¡Hasta luego! ¡Que tengas un buen día!"})

    if any(agradecimiento in mensaje_limpio for agradecimiento in agradecimientos):
        return jsonify({"respuesta": "¡De nada! Siempre aquí para ayudarte 😊"})

    if any(crear in mensaje_limpio for crear in crear_recetas):
        return jsonify({"respuesta": "Perfecto, puedes añadir una nueva receta en el formulario."})

    # BÚSQUEDA SOLO EN TÍTULOS
    recetas = cargar_recetas()
    palabras_usuario = set(mensaje_limpio.split())

    # Palabras que existen en algún título
    palabras_validas = set()
    for receta in recetas:
        palabras_validas.update(limpiar_texto(receta["titulo"]).split())

    # Solo dejamos las que existen en títulos
    palabras_usuario_filtradas = palabras_usuario.intersection(palabras_validas)

    recetas_encontradas = []
    for receta in recetas:
        titulo_limpio = limpiar_texto(receta.get("titulo", ""))
        palabras_titulo = set(titulo_limpio.split())

        # Cambiado: ahora solo necesita compartir al menos 1 palabra
        if palabras_usuario_filtradas and palabras_usuario_filtradas.issubset(palabras_titulo):
            recetas_encontradas.append(receta)

    if recetas_encontradas:
        respuesta = ""
        for rec in recetas_encontradas:
            respuesta += (
                f"Claro, aquí tienes la receta: {rec['titulo']}\n"
                f"Ingredientes: {rec['ingredientes']}\n"
                f"Preparación: {rec['preparacion']}\n\n"
            )
    else:
        respuesta = "No encontré ninguna receta que coincida con tu búsqueda."

    return jsonify({"respuesta": respuesta})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
