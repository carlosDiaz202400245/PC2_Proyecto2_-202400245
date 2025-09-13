from flask import Flask, render_template, request, Response
from ClasesPrincipales import *
from EstructuraBase import *
from xml_parser import cargar_configuracion

app = Flask(__name__)
sistema = Sistema()
simulador = Simulador()


class JsonResponse:
    @staticmethod
    def crear(respuesta_dict):
        """Crea una respuesta JSON manualmente sin usar dict nativos"""
        json_str = "{"
        primero = True
        for clave, valor in respuesta_dict:
            if not primero:
                json_str += ","
            primero = False
            json_str += f'"{clave}":{valor}'
        json_str += "}"
        return Response(json_str, mimetype='application/json')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cargar', methods=['POST'])
def cargar_archivo():
    if 'archivo' not in request.files:
        return "No se envió archivo", 400

    archivo = request.files['archivo']
    if archivo.filename == '':
        return "No se seleccionó archivo", 400

    try:
        global sistema
        sistema = cargar_configuracion(archivo)
        return "Archivo cargado exitosamente", 200
    except Exception as e:
        return f"Error al cargar archivo: {str(e)}", 500


@app.route('/invernaderos')
def obtener_invernaderos():
    """Devuelve la lista de invernaderos disponibles"""
    invernaderos_info = ListaSerializable()
    for invernadero in sistema.invernaderos:
        invernaderos_info.agregar(invernadero)

    respuesta = DiccionarioSimple()
    respuesta.agregar("invernaderos", invernaderos_info.to_dict())

    return JsonResponse.crear(respuesta)


@app.route('/simular/<nombre_invernadero>/<nombre_plan>')
def simular(nombre_invernadero, nombre_plan):
    try:
        # Buscar invernadero y plan
        invernadero = sistema.obtener_invernadero_por_nombre(nombre_invernadero)
        if not invernadero:
            return "Invernadero no encontrado", 404

        plan = None
        for p in invernadero.planes_riego:
            if p.nombre == nombre_plan:
                plan = p
                break

        if not plan:
            return "Plan no encontrado", 404

        # Simular el plan
        plan_simulado = simulador.simular_plan(invernadero, plan)

        # Convertir instrucciones a formato serializable
        instrucciones_serializable = ListaSerializable()
        for instruccion_tiempo in plan_simulado.instrucciones_por_tiempo:
            instrucciones_serializable.agregar(instruccion_tiempo)

        # Preparar resultados con nuestras estructuras
        resultados = DiccionarioSimple()
        resultados.agregar("invernadero", nombre_invernadero)
        resultados.agregar("plan", nombre_plan)
        resultados.agregar("tiempo_optimo", plan_simulado.tiempo_optimo)
        resultados.agregar("agua_total", plan_simulado.agua_total)
        resultados.agregar("fertilizante_total", plan_simulado.fertilizante_total)
        resultados.agregar("instrucciones", instrucciones_serializable.to_dict())

        # Pasar el string JSON directamente al template
        return render_template('resultados.html',
                               resultados_json=resultados.to_dict())

    except Exception as e:
        return f"Error en simulación: {str(e)}", 500


@app.route('/estadisticas_drones/<nombre_invernadero>/<nombre_plan>')
def estadisticas_drones(nombre_invernadero, nombre_plan):
    """Devuelve estadísticas por dron"""
    invernadero = sistema.obtener_invernadero_por_nombre(nombre_invernadero)
    if not invernadero:
        return "Invernadero no encontrado", 404

    estadisticas = ListaSerializable()
    for dron in invernadero.drones_asignados:
        estadisticas.agregar(dron)

    respuesta = DiccionarioSimple()
    respuesta.agregar("estadisticas_drones", estadisticas.to_dict())

    return JsonResponse.crear(respuesta)


if __name__ == '__main__':
    app.run(debug=True)