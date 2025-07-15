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

    # Buscar recetas por palabras clave y coincidencias parciales en título o ingredientes
    palabras_usuario = set(re.sub(r'[^\w\s]', '', mensaje_usuario).split())

    recetas_encontradas = []
    for receta in cargar_recetas():
        titulo = receta.get("titulo", "").lower()

        # Si alguna palabra del usuario está en el título o ingredientes
        if any(palabra in titulo or palabra for palabra in palabras_usuario):
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
    
