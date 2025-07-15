from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__) #Crea la aplicación flask.

@app.route('/') #Muestra el interfaz de index.html como el principal al abrir la web.
def home():
	return render_template('index.html')

@app.route("/formulario") #Crea la ruta para acceder a la pagina del formulario de nuevas recetas.
def formulario():
	return render_template("formulario.html")

if __name__=='__main__': #Enciende el servidor.
	app.run(debug=True)

import json
import os

RUTA_RECETAS = "recetas.json" #Ruta donde se guardan las recetas.

#Función para cargar las recetas existentes 
def cargar_recetas():
	if os.path.exists(RUTA_RECETAS):
		with open(RUTA_RECETAS, "r", encoding = "utf-8") as f:
			return json.load(f)
	return []

#Función para guardar las recetas.
def guardar_recetas(recetas):
	with open(RUTA_RECETAS, "w", encoding= "utf-8") as f:
		json.dump(recetas, f, indent = 4, ensure_ascii = False)

@app.route("/guardar_receta", methods = ["POST"])
#Obtener los datos del formulario.
def guardar_receta():
	titulo = request.form["titulo"]
	ingredientes = request.form["ingredientes"]
	preparacion = request.form["preparacion"]

	#Cargar recetas existentes
	recetas = cargar_recetas()

	#Añadir la nueva receta.
	nueva_receta = {
		"titulo": titulo,
		"ingredientes": ingredientes,
		"preparacion": preparacion,
	}
	recetas.append(nueva_receta)

	#Guardar de nuevo todas las recetas en el archivo.
	guardar_recetas(recetas)

	#Redirigir al chat después de guardar
	return redirect(url_for("home"))

with open("recetas.json", "r", encoding="utf-8") as f:
	recetas = json.load(f)

@app.route("/enviar_mensaje", methods=["POST"])
def enviar_mensaje():
	#Obtenemos la información del mensaje del usuario.
	data = request.get_json()

	#Extraemos el texto del mensaje.
	mensaje_usuario = data.get("mensaje", "").lower()

	respuesta = ""

	#Comprobamos que el mensaje contenga palabras clave para buscar receta.
	if "receta" in mensaje_usuario or "cómo" in mensaje_usuario or "quiero" in mensaje_usuario:
		encontrada = None

		#Buscamos en la lista de recetas si coincide alguna palabra.
		for receta in recetas:
			if receta["titulo"].lower() in mensaje_usuario:
				encontrada = receta
				break
		#Si coincide una receta.
		if encontrada:
			respuesta = (
				f"¡Aquí tienes la receta de {encontrada['titulo']}!\n\n"
				f"Ingredientes: {encontrada['ingredientes']}\n"
				f"Preparación: {encontrada['preparacion']}"
			)
		else:
			#Si no hay receta que coincida.
			respuesta = "No tengo esa receta, pero puedes añadirla en el formulario."

	else:
		#Si el mensaje no tiene palabras clave
		respuesta = "No entiendo bien, pero puedo buscarte recetas o añadir una nueva."

		#Devolvemos la respuesta al documento.
	return jsonify({"respuesta": respuesta})
