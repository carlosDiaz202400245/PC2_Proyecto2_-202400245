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

                        # Buscar el dron en la lista global y asignarlo
                        for dron in sistema.drones:
                            if dron.id == id_dron:
                                dron.hilera_asignada = hilera_asignada
                                invernadero.drones_asignados.agregar(dron)
                                break

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
    Genera el archivo XML de salida
    """
    try:
        # Crear elemento raíz
        datos_salida = ET.Element('datosSalida')

        # Crear lista de invernaderos
        lista_invernaderos_elem = ET.SubElement(datos_salida, 'ListaInvernaderos')

        for invernadero in sistema.invernaderos:
            invernadero_elem = ET.SubElement(lista_invernaderos_elem, 'invernadero')
            invernadero_elem.set('nombre', invernadero.nombre)

            lista_planes_elem = ET.SubElement(invernadero_elem, 'listaPlanes')

            for plan in invernadero.planes_riego:
                plan_elem = ET.SubElement(lista_planes_elem, 'plan')
                plan_elem.set('nombre', plan.nombre)

                # Agregar estadísticas del plan
                tiempo_optimo_elem = ET.SubElement(plan_elem, 'tiempoOptimoSegundos')
                tiempo_optimo_elem.text = str(plan.tiempo_optimo)

                agua_requerida_elem = ET.SubElement(plan_elem, 'aguaRequeridaLitros')
                agua_requerida_elem.text = str(plan.agua_total)

                fertilizante_elem = ET.SubElement(plan_elem, 'fertilizanteRequeridoGramos')
                fertilizante_elem.text = str(plan.fertilizante_total)

                # Agregar eficiencia de drones
                eficiencia_elem = ET.SubElement(plan_elem, 'eficienciaDronesRegadores')
                for dron in invernadero.drones_asignados:
                    dron_elem = ET.SubElement(eficiencia_elem, 'dron')
                    dron_elem.set('nombre', dron.nombre)
                    dron_elem.set('litrosAgua', str(dron.agua_usada))
                    dron_elem.set('gramosFertilizante', str(dron.fertilizante_usado))

                # Agregar instrucciones (esto se llenaría después de la simulación)
                instrucciones_elem = ET.SubElement(plan_elem, 'instrucciones')
                # Aquí se agregarían las instrucciones por tiempo

        # Crear el árbol XML y guardar
        tree = ET.ElementTree(datos_salida)
        tree.write(archivo_salida, encoding='utf-8', xml_declaration=True)

        return True

    except Exception as e:
        print(f"Error al generar XML de salida: {e}")
        return False


def generar_reporte_html(invernadero, plan, archivo_salida):
    """
    Genera el reporte HTML según los requisitos del enunciado
    """
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reporte de Riego - {invernadero.nombre}</title>
            <style>
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Reporte de Riego Automatizado</h1>
            <h2>Invernadero: {invernadero.nombre}</h2>
            <h2>Plan: {plan.nombre}</h2>

            <h3>Asignación de Drones por Hilera</h3>
            <table>
                <tr><th>Hilera</th><th>Dron</th></tr>
        """

        # Tabla de asignación de drones
        for dron in invernadero.drones_asignados:
            html_content += f"<tr><td>H{dron.hilera_asignada}</td><td>{dron.nombre}</td></tr>"

        html_content += """
            </table>

            <h3>Instrucciones por Tiempo</h3>
            <table>
                <tr><th>Tiempo (s)</th><th>DR01</th><th>DR02</th><th>DR03</th></tr>
        """

        # Tabla de instrucciones (esto se llenaría después de la simulación)
        for instruccion_tiempo in plan.instrucciones_por_tiempo:
            html_content += f"<tr><td>{instruccion_tiempo.segundo}</td>"
            # Aquí se agregarían las instrucciones por dron
            html_content += "<td>...</td><td>...</td><td>...</td></tr>"

        html_content += """
            </table>

            <h3>Estadísticas de Uso</h3>
            <table>
                <tr><th>Dron</th><th>Agua Usada (L)</th><th>Fertilizante Usado (g)</th></tr>
        """

        # Tabla de estadísticas
        for dron in invernadero.drones_asignados:
            html_content += f"<tr><td>{dron.nombre}</td><td>{dron.agua_usada}</td><td>{dron.fertilizante_usado}</td></tr>"

        html_content += f"""
            </table>

            <h3>Totales</h3>
            <p>Tiempo óptimo: {plan.tiempo_optimo} segundos</p>
            <p>Agua total: {plan.agua_total} litros</p>
            <p>Fertilizante total: {plan.fertilizante_total} gramos</p>
        </body>
        </html>
        """

        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return True

    except Exception as e:
        print(f"Error al generar reporte HTML: {e}")
        return False

