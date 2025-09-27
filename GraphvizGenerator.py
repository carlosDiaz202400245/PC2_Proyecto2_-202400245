import graphviz
from EstructuraBase import *
from ClasesPrincipales import *

class GraphvizGenerator:
    def __init__(self):
        self.dot = None

    def generar_grafo_lista_enlazada(self, lista, nombre ="ListaEnlazada"):
        """Generar el grafico de la lista babys"""
        dot = graphviz.Digraph(name=nombre)
        dot.attr(rankdir="LR")

        if lista.esta_vacia():
            dot.node('empty', 'Lista Vacía', shape = 'box')
            return dot
        actual = lista.cabeza
        index = 0
        #crearemos los noditos
        while actual:
            node_id = f"node_{index}"
            dot.edge(node_id, str(actual.dato),shape='box')

            if actual.siguiente:
                next_id = f"node{index+1}"
                dot.edge(node_id, next_id,arrowhead='box')

            actual = actual.siguiente
            index += 1
        dot.node('info', f'Longitud: {len(lista)}', shape='note')
        if lista.cabeza:
            dot.edge('info', 'node_0', arrowhead='none')
        return dot
    def generar_grafo_cola(self,cola, nombre="Cola"):
        dot = graphviz.Digraph(name=nombre)
        dot.attr(rankdir="TB")

        dot.node('estructura','COLA', shape='folder')

        if cola.esta_vacia():
            dot.node('Vacia', 'Vacia', shape='box')
            dot.edge('estructura', 'Vacia')
            return dot
        if cola.frente:
            dot.node('Frente', f'Frente: {cola.frente.dato}', shape='box')
            dot.edge('estructura', 'Frente')

        if cola.final:
            dot.node('final',f'Final: {cola.final.dato}', shape='box')
            dot.edge('estructura', 'final')

        dot.node('longitud', f'Longitud:{len(cola)}',shape = "note")
        dot.edge('longitud', 'cola')
        return dot

    def generar_grafo_plan_riego(self,plan,nombre= "PlanRiego"):
        """Generar el grafo del plan (estado del plan de riego papi)"""
        dot = graphviz.Digraph(name=nombre)
        dot.attr(rankdir="TB")

        dot.node('plan_info',f'Plan: {plan.nombre}\nTiempo: {plan.tiempo_optimo}s',shape='component')

        #secuencia en parseatrix

        dot.node('secuencia','Secuencia Parseada', shape='folder')
        dot.edge('plan_info', 'secuencia')

        #elementos de la secuencia
        for i, coordenada in enumerate(plan.secuencia_parseada):
            coord_node = f"coord_{i}"
            dot.node(coord_node, f'H{coordenada.hilera}-P{coordenada.posicion}', shape='box')
            dot.edge('secuencia', coord_node)

            #instrucciones por t
            dot.node ('istrucciones', f'INstrucciones: {len(plan.instrucciones_por_tiempo)} tiempos', shape='folder')
            dot.edge('plan_info', 'istrucciones')

            return dot

    def generar_grafo_invernadero(self,invernadero, tiempo_actual=0):
        """Grafo del grafo invernadero a un tiempo especifico"""
        dot = graphviz.Digraph(name=f'invernadero_{invernadero.nombre}')
        dot.attr(rankdir="TB")

        dot.node('info', f'Inverndero: {invernadero.nombre}\nHileras: {invernadero.num_hileras}\nPlantas por hileras: {invernadero.plantas_por_hilera}', shape='component')

        dot.node('planes_titulo', 'Planes de Riego', shape='folder')
        dot.edge('info', 'planes_titulo')

        for i, plan in enumerate(invernadero.planes_riego):
            plan_node = f"plan_{i}"
            dot.node(plan_node, f'Plan: {plan.nombre}\nSecuencia: {plan.secuencia}', shape='box')
            dot.edge('planes_titulo', plan_node)

        return dot

    def generar_grafo_invernadero(self, invernadero, tiempo_actual=0):
        """Genera gráfico completo del estado del invernadero en un tiempo específico"""
        dot = graphviz.Digraph(name=f"Invernadero_{invernadero.nombre}")
        dot.attr(rankdir='TB')

        # Información del invernadero
        dot.node('info',
                 f'Invernadero: {invernadero.nombre}\nHileras: {invernadero.num_hileras}\nPlantas por hilera: {invernadero.plantas_por_hilera}',
                 shape='component')

        # Drones
        dot.node('drones_title', 'Drones Asignados', shape='folder')
        dot.edge('info', 'drones_title')

        for dron in invernadero.drones_asignados:
            dron_node = f"dron_{dron.nombre}"
            dot.node(dron_node,
                     f'{dron.nombre}\nHilera: {dron.hilera_asignada}\nPosición: {dron.posicion_actual}\nAgua: {dron.agua_usada}L',
                     shape='box')
            dot.edge('drones_title', dron_node)

        # Planes de riego
        dot.node('planes_title', 'Planes de Riego', shape='folder')
        dot.edge('info', 'planes_title')

        for i, plan in enumerate(invernadero.planes_riego):
            plan_node = f"plan_{i}"
            dot.node(plan_node, f'Plan: {plan.nombre}\nSecuencia: {plan.secuencia}', shape='box')
            dot.edge('planes_title', plan_node)

        return dot

    def generar_grafo_sistema_completo(self, sistema, tiempo_actual=0, plan_activo=None):
        """Genera gráfico completo del sistema en un tiempo específico"""
        dot = graphviz.Digraph(name="SistemaCompleto")
        dot.attr(rankdir='TB')

        # Nodo raíz del sistema
        dot.node('sistema', 'Sistema de Riego Automatizado', shape='doublecircle')

        # Invernaderos
        dot.node('invernaderos', f'Invernaderos: {len(sistema.invernaderos)}', shape='folder')
        dot.edge('sistema', 'invernaderos')

        for i, invernadero in enumerate(sistema.invernaderos):
            inv_node = f"invernadero_{i}"
            dot.node(inv_node, f'{invernadero.nombre}\nHileras: {invernadero.num_hileras}', shape='box')
            dot.edge('invernaderos', inv_node)

            # Drones del invernadero
            for dron in invernadero.drones_asignados:
                dron_node = f"dron_{i}_{dron.nombre}"
                estado = "⏹️" if dron.posicion_actual == 0 else "▶️"
                dot.node(dron_node, f'{estado} {dron.nombre}\nPos: {dron.posicion_actual}', shape='ellipse')
                dot.edge(inv_node, dron_node)

        # Tiempo actual
        dot.node('tiempo', f'Tiempo: {tiempo_actual}s', shape='note')
        dot.edge('sistema', 'tiempo')

        if plan_activo:
            dot.node('plan_activo', f'Plan Activo: {plan_activo.nombre}', shape='component')
            dot.edge('sistema', 'plan_activo')

        return dot

    def guardar_grafo(self, dot, nombre_archivo, formato='png'):
        """Guarda el gráfico en un archivo"""
        try:
            dot.render(nombre_archivo, format=formato, cleanup=True)
            return f"{nombre_archivo}.{formato}"
        except Exception as e:
            print(f"Error al guardar gráfico: {e}")
            return None
