import xml.etree.ElementTree as ET
from EstructuraBase import *
from ClasesPrincipales import *

def cargar_configuracion(archivo_xml):
    sistema = Sistema()

    try:
        tree = ET.parse(archivo_xml)
        root = tree.getroot()

        # 1. Cargar lista de drones
        lista_drones_element = root.find('listaDrones')
        if lista_drones_element is not None:
            for dron_elem in lista_drones_element.findall('dron'):
                id_dron = int(dron_elem.get('id'))
                nombre_dron = dron_elem.get('nombre')
                dron = Dron(id_dron, nombre_dron)
                sistema.drones.agregar(dron)

        # 2. Cargar lista de invernaderos
        lista_invernaderos_element = root.find('listaInvernaderos')
        if lista_invernaderos_element is not None:
            for invernadero_elem in lista_invernaderos_element.findall('invernadero'):
                # Datos básicos del invernadero
                nombre_invernadero = invernadero_elem.get('nombre')
                num_hileras = int(invernadero_elem.find('numeroHileras').text.strip())
                plantas_x_hilera = int(invernadero_elem.find('plantasXhilera').text.strip())

                invernadero = Invernadero(nombre_invernadero, num_hileras, plantas_x_hilera)

                # 2.1 Cargar plantas del invernadero
                lista_plantas_element = invernadero_elem.find('listaPlantas')
                if lista_plantas_element is not None:
                    for planta_elem in lista_plantas_element.findall('planta'):
                        hilera = int(planta_elem.get('hilera'))
                        posicion = int(planta_elem.get('posicion'))
                        litros_agua = float(planta_elem.get('litrosAgua'))
                        gramos_fertilizante = float(planta_elem.get('gramosFertilizante'))
                        nombre_planta = planta_elem.text.strip() if planta_elem.text else ""

                        planta = Planta(hilera, posicion, litros_agua, gramos_fertilizante, nombre_planta)
                        invernadero.plantas.agregar(planta)

                # 2.2 Cargar asignación de drones a hileras
                asignacion_drones_element = invernadero_elem.find('asignacionDrones')
                if asignacion_drones_element is not None:
                    for asignacion_elem in asignacion_drones_element.findall('dron'):
                        id_dron = int(asignacion_elem.get('id'))
                        hilera_asignada = int(asignacion_elem.get('hilera'))

                        dron_base = None
                        for dron in sistema.drones:
                            if dron.id == id_dron:
                                dron_base = dron
                                break

                        if dron_base:

                            nuevo_dron = Dron(dron_base.id, dron_base.nombre)
                            nuevo_dron.hilera_asignada = hilera_asignada
                            invernadero.drones_asignados.agregar(nuevo_dron)

                # 2.3 Cargar planes de riego
                planes_riego_element = invernadero_elem.find('planesRiego')
                if planes_riego_element is not None:
                    for plan_elem in planes_riego_element.findall('plan'):
                        nombre_plan = plan_elem.get('nombre')
                        secuencia_plan = plan_elem.text.strip()

                        plan_riego = PlanRiego(nombre_plan, secuencia_plan)
                        invernadero.planes_riego.agregar(plan_riego)

                sistema.invernaderos.agregar(invernadero)

        return sistema

    except Exception as e:
        print(f"Error al cargar configuración XML: {e}")
        return sistema


def generar_salida_xml(sistema, archivo_salida):
    """
    GENERACIÓN CORREGIDA del XML de salida según el formato del ejemplo
    """
    try:
        # Crear elemento raíz
        datos_salida = ET.Element('datosSalida')

        # Crear lista de invernaderos (CON NOMBRE CORRECTO)
        lista_invernaderos_elem = ET.SubElement(datos_salida, 'listaInvernaderos')

        for invernadero in sistema.invernaderos:
            invernadero_elem = ET.SubElement(lista_invernaderos_elem, 'invernadero')
            invernadero_elem.set('nombre', invernadero.nombre)

            lista_planes_elem = ET.SubElement(invernadero_elem, 'listaPlanes')

            for plan in invernadero.planes_riego:
                # ✅ SIMULAR el plan si no está simulado
                if plan.tiempo_optimo == 0:
                    from ClasesPrincipales import Simulador
                    simulador = Simulador()
                    plan = simulador.simular_plan(invernadero, plan)

                plan_elem = ET.SubElement(lista_planes_elem, 'plan')
                plan_elem.set('nombre', plan.nombre)

                # ✅ Agregar estadísticas del plan (FORMATO CORRECTO)
                tiempo_optimo_elem = ET.SubElement(plan_elem, 'tiempoOptimoSegundos')
                tiempo_optimo_elem.text = f' {plan.tiempo_optimo} '  # Espacios como en el ejemplo

                agua_requerida_elem = ET.SubElement(plan_elem, 'aguaRequeridaLitros')
                agua_requerida_elem.text = f' {plan.agua_total} '

                fertilizante_elem = ET.SubElement(plan_elem, 'fertilizanteRequeridoGramos')
                fertilizante_elem.text = f' {plan.fertilizante_total} '

                # ✅ Agregar eficiencia de drones (FORMATO CORRECTO)
                eficiencia_elem = ET.SubElement(plan_elem, 'eficienciaDronesRegadores')
                for dron in invernadero.drones_asignados:
                    dron_elem = ET.SubElement(eficiencia_elem, 'dron')
                    dron_elem.set('nombre', dron.nombre)
                    dron_elem.set('litrosAgua', str(dron.agua_usada))
                    dron_elem.set('gramosFertilizante', str(dron.fertilizante_usado))

                # ✅ AGREGAR INSTRUCCIONES POR TIEMPO (PARTE QUE FALTABA)
                instrucciones_elem = ET.SubElement(plan_elem, 'instrucciones')

                if plan.instrucciones_por_tiempo.longitud > 0:
                    for i in range(plan.instrucciones_por_tiempo.longitud):
                        instruccion_tiempo = plan.instrucciones_por_tiempo.obtener(i)
                        tiempo_elem = ET.SubElement(instrucciones_elem, 'tiempo')
                        tiempo_elem.set('segundos', str(instruccion_tiempo.segundo))

                        # Agregar instrucciones de cada dron en este tiempo
                        for j in range(instruccion_tiempo.instrucciones_drones.longitud):
                            instruccion_dron = instruccion_tiempo.instrucciones_drones.obtener(j)
                            dron_inst_elem = ET.SubElement(tiempo_elem, 'dron')
                            dron_inst_elem.set('nombre', instruccion_dron.nombre_dron)

                            # Escapar caracteres XML en la acción
                            accion = instruccion_dron.accion
                            accion = accion.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                            dron_inst_elem.set('accion', accion)

        # ✅ Crear el árbol XML y guardar CON FORMATO
        tree = ET.ElementTree(datos_salida)

        # Mejorar formato del XML
        from xml.dom import minidom
        xml_str = ET.tostring(datos_salida, encoding='utf-8')
        xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="  ", encoding='utf-8')

        # Escribir con declaración XML
        with open(archivo_salida, 'wb') as f:
            f.write(b'<?xml version="1.0"?>\n')
            f.write(xml_pretty)

        return True

    except Exception as e:
        print(f"Error al generar XML de salida: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def generar_reporte_html(invernadero, plan, archivo_salida):
    """
    GENERACIÓN CORREGIDA del reporte HTML
    """
    try:
        # ✅ PRIMERO: Simular el plan si no está simulado
        if plan.tiempo_optimo == 0:
            from ClasesPrincipales import Simulador
            simulador = Simulador()
            plan = simulador.simular_plan(invernadero, plan)

        # ✅ Obtener nombres únicos de todos los drones
        nombres_drones = []
        for i in range(invernadero.drones_asignados.longitud):
            dron = invernadero.drones_asignados.obtener(i)
            nombres_drones.append(dron.nombre)

        # ✅ Crear headers dinámicos para la tabla
        headers_drones = "".join([f"<th>{nombre}</th>" for nombre in nombres_drones])

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reporte de Riego - {invernadero.nombre}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                th, td {{ border: 1px solid black; padding: 10px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                .header {{ background: #4CAF50; color: white; padding: 15px; text-align: center; }}
                .stats {{ margin: 20px 0; padding: 15px; background: #f9f9f9; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌱 Reporte de Riego Automatizado</h1>
                <h2>Invernadero: {invernadero.nombre} | Plan: {plan.nombre}</h2>
            </div>

            <div class="stats">
                <h3>📊 Estadísticas Generales</h3>
                <p><strong>⏱️ Tiempo óptimo:</strong> {plan.tiempo_optimo} segundos</p>
                <p><strong>💧 Agua total:</strong> {plan.agua_total} litros</p>
                <p><strong>🌿 Fertilizante total:</strong> {plan.fertilizante_total} gramos</p>
            </div>

            <h3>📋 Tabla 1: Asignación de Drones por Hilera</h3>
            <table>
                <tr><th>Hilera</th><th>Dron</th><th>Agua Usada (L)</th><th>Fertilizante (g)</th></tr>
        """

        # ✅ Tabla de asignación de drones CORREGIDA
        for i in range(invernadero.drones_asignados.longitud):
            dron = invernadero.drones_asignados.obtener(i)
            html_content += f"""
                <tr>
                    <td>H{dron.hilera_asignada}</td>
                    <td>{dron.nombre}</td>
                    <td>{dron.agua_usada}</td>
                    <td>{dron.fertilizante_usado}</td>
                </tr>"""

        html_content += f"""
            </table>

            <h3>⏱️ Tabla 2: Instrucciones por Tiempo</h3>
            <table>
                <tr><th>Tiempo (s)</th>{headers_drones}</tr>
        """

        # ✅ Tabla de instrucciones CORREGIDA
        if plan.instrucciones_por_tiempo.longitud > 0:
            for i in range(plan.instrucciones_por_tiempo.longitud):
                instruccion_tiempo = plan.instrucciones_por_tiempo.obtener(i)
                html_content += f"<tr><td><strong>{instruccion_tiempo.segundo}</strong></td>"

                # ✅ Para cada dron, buscar su instrucción en este tiempo
                for nombre_dron in nombres_drones:
                    accion_dron = "Esperar"  # Valor por defecto

                    # Buscar la instrucción de este dron en el tiempo actual
                    for j in range(instruccion_tiempo.instrucciones_drones.longitud):
                        instruccion_dron = instruccion_tiempo.instrucciones_drones.obtener(j)
                        if instruccion_dron.nombre_dron == nombre_dron:
                            accion_dron = instruccion_dron.accion
                            break

                    html_content += f"<td>{accion_dron}</td>"

                html_content += "</tr>"
        else:
            html_content += "<tr><td colspan='" + str(
                len(nombres_drones) + 1) + "'>No hay instrucciones simuladas</td></tr>"

        html_content += """
            </table>

            <h3>📈 Estadísticas por Dron</h3>
            <table>
                <tr><th>Dron</th><th>Hilera</th><th>Agua Usada (L)</th><th>Fertilizante Usado (g)</th></tr>
        """

        # ✅ Tabla de estadísticas por dron
        for i in range(invernadero.drones_asignados.longitud):
            dron = invernadero.drones_asignados.obtener(i)
            html_content += f"""
                <tr>
                    <td>{dron.nombre}</td>
                    <td>H{dron.hilera_asignada}</td>
                    <td>{dron.agua_usada}</td>
                    <td>{dron.fertilizante_usado}</td>
                </tr>"""

        html_content += f"""
            </table>

            <div style="margin-top: 30px; text-align: center; color: #666;">
                <p>Reporte generado automáticamente por GuateRiegos 2.0</p>
                <p>© 2025 Universidad de San Carlos de Guatemala</p>
            </div>
        </body>
        </html>
        """

        # ✅ Guardar archivo
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return True

    except Exception as e:
        print(f"Error al generar reporte HTML: {e}")
        import traceback
        print(traceback.format_exc())
        return False
