from flask import Flask, render_template, request, Response
from ClasesPrincipales import *
from GraphvizGenerator import GraphvizGenerator
from xml_parser import cargar_configuracion, generar_reporte_html, generar_salida_xml
from EstructuraBase import DiccionarioSimple, ListaEnlazada
from urllib.parse import unquote
app = Flask(__name__)
sistema = Sistema()
simulador = Simulador()


class TemplateData:
    """Estructura simple para pasar datos al template"""

    def __init__(self):
        self._datos = DiccionarioSimple()

    def agregar(self, clave, valor):
        self._datos.agregar(clave, valor)

    def get(self, clave, default=None):
        """Método que Jinja2 usa para acceder a valores"""
        return self._datos.get(clave, default)

    def __getitem__(self, clave):
        valor = self._datos.obtener(clave)
        if valor is None:
            raise KeyError(clave)
        return valor

    def __contains__(self, clave):
        return self._datos.obtener(clave) is not None


class ListaEnlazadaTemplate(ListaEnlazada):
    """lista enlazaza que me conecta con jinnja2"""

    pass  # ListaEnlazada ya es iterable, Jinja la entiende bien

class JsonConverter:
    @staticmethod
    def convertir_a_json(objeto):
        """Convierte cualquier objeto a string JSON usando solo nuestras estructuras"""
        # Para DiccionarioSimple
        if hasattr(objeto, 'claves') and hasattr(objeto, 'valores'):
            return JsonConverter._dict_a_json(objeto)
        # Para ListaEnlazada
        elif hasattr(objeto, 'cabeza') and hasattr(objeto, 'longitud'):
            return JsonConverter._lista_a_json(objeto)
        # Para strings
        elif type(objeto).__name__ == 'str':
            return JsonConverter._escapar_string(objeto)
        # Para números
        else:
            # Intentar convertir a número
            try:
                float(str(objeto))
                return str(objeto)
            except:
                return 'null'

    @staticmethod
    def _escapar_string(s):
        """Escapa caracteres especiales para JSON por que daba clavo en el reporte"""
        resultado = '"'
        i = 0
        while i < len(s):
            car = s[i]

            # Escapar caracteres especiales
            if car == '"':
                resultado += '\\"'
            elif car == '\\':
                resultado += '\\\\'
            elif car == '\b':
                resultado += '\\b'
            elif car == '\f':
                resultado += '\\f'
            elif car == '\n':
                resultado += '\\n'
            elif car == '\r':
                resultado += '\\r'
            elif car == '\t':
                resultado += '\\t'
            else:
                # Verificar si es carácter de control
                codigo = ord(car)
                if codigo < 32:
                    resultado += f'\\u{codigo:04x}'
                else:
                    resultado += car
            i += 1

        resultado += '"'
        return resultado

    @staticmethod
    def _lista_a_json(lista):
        """Convierte ListaEnlazada """
        json_str = "["
        primero = True

        # Usar iterador de ListaEnlazada
        for item in lista:
            if not primero:
                json_str += ","
            primero = False
            json_str += JsonConverter.convertir_a_json(item)

        json_str += "]"
        return json_str

    @staticmethod
    def _dict_a_json(dict_obj):
        """Convierte DiccionarioSimple a JSON object"""
        json_str = "{"
        primero = True

        # Usar iterador de DiccionarioSimple
        for clave, valor in dict_obj:
            if not primero:
                json_str += ","
            primero = False
            json_str += f'{JsonConverter.convertir_a_json(clave)}:{JsonConverter.convertir_a_json(valor)}'

        json_str += "}"
        return json_str
# ==================== RUTAS PRINCIPALES ====================
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
def listar_invernaderos():
    """Devuelve lista de invernaderos usando solo TDAs"""
    invernaderos_lista = ListaEnlazadaTemplate()

    if not sistema.invernaderos.esta_vacia():
        for invernadero in sistema.invernaderos:
            invernadero_info = DiccionarioSimple()
            invernadero_info.agregar("nombre", invernadero.nombre)
            invernadero_info.agregar("num_hileras", invernadero.num_hileras)
            invernadero_info.agregar("plantas_por_hilera", invernadero.plantas_por_hilera)

            planes_lista = ListaEnlazadaTemplate()
            if not invernadero.planes_riego.esta_vacia():
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


@app.route('/simular/<path:nombre_invernadero>/<path:nombre_plan>')
def simular_riego(nombre_invernadero, nombre_plan):
    try:
        from urllib.parse import unquote

        # Decodificar nombres
        nombre_invernadero_decodificado = unquote(nombre_invernadero)
        nombre_plan_decodificado = unquote(nombre_plan)

        print(f" Buscando: '{nombre_invernadero_decodificado}' -> '{nombre_plan_decodificado}'")

        invernadero = sistema.obtener_invernadero_por_nombre(nombre_invernadero_decodificado)
        if not invernadero:
            return f"Invernadero '{nombre_invernadero_decodificado}' no encontrado", 404

        plan = None
        for p in invernadero.planes_riego:
            if p.nombre == nombre_plan_decodificado:
                plan = p
                break

        if not plan:
            return f"Plan '{nombre_plan_decodificado}' no encontrado en invernadero", 404

        # Simular el plan
        plan_simulado = simulador.simular_plan(invernadero, plan)

        #  Crear TemplateData y agregar datos
        datos = TemplateData()
        datos.agregar("invernadero", invernadero.nombre)
        datos.agregar("plan", plan.nombre)
        datos.agregar("tiempo_optimo", plan.tiempo_optimo)
        datos.agregar("agua_total", plan.agua_total)
        datos.agregar("fertilizante_total", plan.fertilizante_total)
        datos.agregar("instrucciones_por_tiempo", plan.instrucciones_por_tiempo)
        datos.agregar("drones", invernadero.drones_asignados)

        # Pasar el objeto datos directamente
        return render_template('simulacion.html', datos=datos)

    except Exception as e:
        import traceback
        print(f" Error: {str(e)}")
        print(traceback.format_exc())  # Para ver el traceback completo
        return f"Error en simulación: {str(e)}", 500


@app.route('/generar_reporte/<path:nombre_invernadero>/<path:nombre_plan>')
def generar_reporte(nombre_invernadero, nombre_plan):
    try:
        #  DECODIFICAR nombres correctamente CON UTF-8 por que si no se mira de la vrg xd
        nombre_invernadero_decodificado = unquote(nombre_invernadero)
        nombre_plan_decodificado = unquote(nombre_plan)

        invernadero = sistema.obtener_invernadero_por_nombre(nombre_invernadero_decodificado)
        if not invernadero:
            return f"Invernadero '{nombre_invernadero_decodificado}' no encontrado", 404

        plan = None
        for p in invernadero.planes_riego:
            if p.nombre == nombre_plan_decodificado:
                plan = p
                break

        if not plan:
            return f"Plan '{nombre_plan_decodificado}' no encontrado en invernadero", 404

        #  NOMBRE DE ARCHIVO SEGURO pa que no jodan los caracteres
        nombre_archivo_seguro = f"reporte_{nombre_invernadero_decodificado.replace(' ', '_')}_{nombre_plan_decodificado.replace(' ', '_')}.html"
        archivo_reporte = f"reportes/{nombre_archivo_seguro}"

        import os
        os.makedirs('reportes', exist_ok=True)

        if generar_reporte_html(invernadero, plan, archivo_reporte):
            return f" Reporte generado exitosamente: {nombre_archivo_seguro}", 200
        else:
            return " Error al generar reporte HTML", 500

    except Exception as e:
        return f" Error al generar reporte: {str(e)}", 500

@app.route('/generar_salida')
def generar_archivo_salida():
    try:

        if sistema.invernaderos.longitud == 0:
            return " No hay datos cargados. Primero cargue un archivo de configuración.", 400

        if generar_salida_xml(sistema, "salida.xml"):
            return " Archivo de salida generado: salida.xml", 200
        else:
            return " Error al generar archivo de salida", 500

    except Exception as e:
        return f" Error al generar salida: {str(e)}", 500


# ==================== RUTAS PARA GRÁFICOS ====================

@app.route('/generar_graficos/<path:nombre_invernadero>/<path:nombre_plan>/<int:tiempo>')
def generar_graficos_ruta(nombre_invernadero, nombre_plan, tiempo):
    try:
        nombre_invernadero_decodificado = unquote(nombre_invernadero)
        nombre_plan_decodificado = unquote(nombre_plan)

        invernadero = sistema.obtener_invernadero_por_nombre(nombre_invernadero_decodificado)
        if not invernadero:
            return "Invernadero no encontrado", 404

        plan = None
        for p in invernadero.planes_riego:
            if p.nombre == nombre_plan_decodificado:
                plan = p
                break

        if not plan:
            return "Plan de riego no encontrado", 404

        # Simular el plan si no está simulado
        if plan.tiempo_optimo == 0:
            plan = simulador.simular_plan(invernadero, plan)

        # MODIFICACIÓN: Usar tiempo 0 si no se especifica (aunque el parámetro ya viene)
        tiempo_grafico = tiempo if tiempo >= 0 else 0

        # Generar gráficos
        generador = GraphvizGenerator()

        # Gráfico del sistema completo
        grafico_sistema = generador.generar_grafo_sistema_completo(sistema, tiempo_grafico, plan)
        archivo_sistema = generador.guardar_grafo(grafico_sistema, f"static/graficos/sistema_{tiempo_grafico}")

        # Gráfico del invernadero
        grafico_invernadero = generador.generar_grafo_invernadero(invernadero, tiempo_grafico)
        archivo_invernadero = generador.guardar_grafo(grafico_invernadero,
                                                      f"static/graficos/invernadero_{nombre_invernadero_decodificado}_{tiempo_grafico}")

        # Gráfico del plan
        grafico_plan = generador.generar_grafo_plan_riego(plan)
        archivo_plan = generador.guardar_grafo(grafico_plan,
                                               f"static/graficos/plan_{nombre_plan_decodificado}_{tiempo_grafico}")

        return "Gráficos generados exitosamente", 200

    except Exception as e:
        return f"Error generando gráficos: {str(e)}", 500


@app.route('/ver_graficos/<path:nombre_invernadero>/<path:nombre_plan>/<int:tiempo>')
def ver_graficos(nombre_invernadero, nombre_plan, tiempo):
    try:
        nombre_invernadero_decodificado = unquote(nombre_invernadero)
        nombre_plan_decodificado = unquote(nombre_plan)

        datos_graficos = TemplateData()
        datos_graficos.agregar("invernadero", nombre_invernadero_decodificado)
        datos_graficos.agregar("plan", nombre_plan_decodificado)
        datos_graficos.agregar("tiempo", tiempo)

        # Rutas de los gráficos generados
        datos_graficos.agregar("grafico_sistema", f"graficos/sistema_{tiempo}.png")
        datos_graficos.agregar("grafico_invernadero",
                               f"graficos/invernadero_{nombre_invernadero_decodificado}_{tiempo}.png")
        datos_graficos.agregar("grafico_plan", f"graficos/plan_{nombre_plan_decodificado}_{tiempo}.png")

        return render_template('graficos.html', graficos=datos_graficos)

    except Exception as e:
        return f"Error mostrando gráficos: {str(e)}", 500


@app.route('/graficos_sistema')
def graficos_sistema():
    """Página simple para mostrar gráficos del sistema"""
    return render_template('graficos_sistema.html')
if __name__ == '__main__':
    import os

    # Crear directorios necesarios
    for dir in ['reportes', 'static/graficos']:
        if not os.path.exists(dir):
            os.makedirs(dir)


    app.run(debug=True, port=5000)