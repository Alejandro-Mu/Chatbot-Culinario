from flask import Flask, render_template

app = Flask(__name__) #Crea la aplicación flask.

@app.route('/') #Muestra el interfaz de index.html como el principal al abrir la web.
def home():
	return render_template('index.html')

@app.route("/formulario") #Crea la ruta para acceder a la pagina del formulario de nuevas recetas.
def formulario():
	return render_template("formulario.html")

if __name__=='__main__': #Enciende el servidor.
	app.run(debug=True)

