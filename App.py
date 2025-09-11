from flask import Flask, render_template, request
from ClasesPrincipales import *
from xml_parser import cargar_configuracion

app = Flask(__name__)
sistema = None  # Aquí guardarás la configuración cargada

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cargar', methods=['POST'])
def cargar_archivo():
    archivo = request.files['archivo']
    global sistema
    sistema = cargar_configuracion(archivo)
    return "Archivo cargado"

@app.route('/simular/<invernadero_id>/<plan_id>')
def simular(invernadero_id, plan_id):
    # Lógica de simulación aquí
    return render_template('resultados.html', resultados=...)