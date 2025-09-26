from flask import Flask, render_template, request, Response
from ClasesPrincipales import *
from EstructuraBase import *
from xml_parser import cargar_configuracion, generar_reporte_html
from EstructuraBase import *
app = Flask(__name__)
sistema = Sistema()
simulador = Simulador()

class JsonConverter:
    @staticmethod
    def convertir_a_json(objeto):
        """Convertir cualquier objeto a srring Json manualmente"""
        if isinstance(objeto, DiccionarioSimple):
            return JsonConverter._dict_a_json(objeto)
        elif isinstance(objeto, ListaEnlazada):
            return JsonConverter._lista_a_json(objeto)
        elif isinstance(objeto, str):
            return f'"{objeto}"'
        else:
            return str(objeto)

    @staticmethod
    def _lista_a_json(lista):
        json_str = "["
        primero = True
        for item in lista:
            if not primero:
                json_str += ","
                primero = False
                json_str += JsonConverter.convertir_a_json(item)
        json_str += "]"
        return json_str

    @staticmethod
    def _dict_a_json(dict_obj):
        json_str = "{"
        primero = True
        for clave, valor in dict_obj:
            if not primero:
                json_str += ","
            primero = False
            json_str += f'"{clave}": {JsonConverter.convertir_a_json(valor)}'
        json_str += "}"
        return json_str

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

# ==================== RUTAS PRINCIPALES ====================
@app.route('/')
def index():
    """Ruta principal a la pagina index de la app baby"""
    return render_template('index.html')


@app.route('/cargar', methods=['POST'])
def cargar_archivo():
    """Cargar archivos """
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
def listar_invernaderos():
    """Devuelve lista de invernaderos disponibles para la interfaz"""
    invernaderos_lista = ListaEnlazada()
    for invernadero in sistema.invernaderos:
        invernadero_info = DiccionarioSimple()
        invernadero_info.agregar("nombre", invernadero.nombre)
        invernadero_info.agregar("num_hileras", invernadero.num_hileras)
        invernadero_info.agregar("plantas_por_hilera", invernadero.plantas_por_hilera)

        planes_lista = ListaEnlazada()
        for plan in invernadero.planes_riego:
            plan_info = DiccionarioSimple()
            plan_info.agregar("nombre", plan.nombre)
            plan_info.agregar("secuencia", plan.secuencia)
            planes_lista.agregar(plan_info)

        invernadero_info.agregar("planes", planes_lista)
        invernaderos_lista.agregar(invernadero_info)

    respuesta = DiccionarioSimple()
    respuesta.agregar("invernaderos", invernaderos_lista)

    json_str = JsonConverter.convertir_a_json(respuesta)
    return Response(json_str, mimetype='application/json')


@app.route('/simular/<nombre_invernadero>/<nombre_plan>')
def simular_riego(nombre_invernadero, nombre_plan):
    """
    simular el proceso de riego seleccionando el invernadoro y el plan de riego
    """
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
            return "Plan de riego no encontrado", 404

        # Simular el plan (esto llena las instrucciones por tiempo)
        plan_simulado = simulador.simular_plan(invernadero, plan)

        # Preparar datos para el template
        datos_template = DiccionarioSimple()
        datos_template.agregar("invernadero", invernadero.nombre)
        datos_template.agregar("plan", plan.nombre)
        datos_template.agregar("tiempo_optimo", plan.tiempo_optimo)
        datos_template.agregar("agua_total", plan.agua_total)
        datos_template.agregar("fertilizante_total", plan.fertilizante_total)

        # Preparar instrucciones para la tabla
        instrucciones_tabla = ListaEnlazada()
        for instruccion_tiempo in plan.instrucciones_por_tiempo:
            tiempo_info = DiccionarioSimple()
            tiempo_info.agregar("segundo", instruccion_tiempo.segundo)

            acciones_drones = DiccionarioSimple()
            for instruccion in instruccion_tiempo.instrucciones_drones:
                acciones_drones.agregar(instruccion.nombre_dron, instruccion.accion)

            tiempo_info.agregar("acciones", acciones_drones)
            instrucciones_tabla.agregar(tiempo_info)

        datos_template.agregar("instrucciones", instrucciones_tabla)

        # Preparar estadísticas de drones
        drones_estadisticas = ListaEnlazada()
        for dron in invernadero.drones_asignados:
            dron_info = DiccionarioSimple()
            dron_info.agregar("nombre", dron.nombre)
            dron_info.agregar("hilera", dron.hilera_asignada)
            dron_info.agregar("agua_usada", dron.agua_usada)
            dron_info.agregar("fertilizante_usado", dron.fertilizante_usado)
            drones_estadisticas.agregar(dron_info)

        datos_template.agregar("drones", drones_estadisticas)

        return render_template('simulacion.html', datos=datos_template)

    except Exception as e:
        return f"Error en simulación: {str(e)}", 500

@app.route('/generar_reporte/<nombre_invernadero>/<nombre_plan>')
def generar_reporte(nombre_invernadero, nombre_plan):
    """generar reporte html del proceso de riego"""
    try:
        invernadero = sistema.obtener_invernadero_por_nombre()
        if not invernadero:
            return "Invernadero no encontrado", 404

        plan = None
        for p in invernadero.planes_riego:
            if p.nombre == nombre_plan:
                plan = p
                break
        if not plan:
            return "Plan de riego no encontrado", 404
        archivo_reporte = f"reportes/reporte_{nombre_invernadero}_{nombre_plan}.html"
        if generar_reporte_html(invernadero, plan, archivo_reporte):
            return f'Reporte generado correctamente: {archivo_reporte} ', 200
        else:
            return "No se pudo generar el reporte papi", 500

    except Exception as error:
        return f"Error en generar reporte: {str(error)}", 500

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