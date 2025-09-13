from EstructuraBase import ListaEnlazada, DiccionarioSimple


class Dron:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.hilera_asignada = None
        self.posicion_actual = 0  # Empieza en posición 0 (inicio de hilera)
        self.agua_usada = 0
        self.fertilizante_usado = 0
        self.instrucciones = ListaEnlazada()  # Instrucciones específicas para este dron

    def mover_adelante(self):
        self.posicion_actual += 1
        return f"Adelante (H{self.hilera_asignada}P{self.posicion_actual})"

    def mover_atras(self):
        self.posicion_actual -= 1
        return f"Atrás (H{self.hilera_asignada}P{self.posicion_actual})"

    def regar(self, planta):
        self.agua_usada += planta.litros_agua
        self.fertilizante_usado += planta.gramos_fertilizante
        return f"Regar (H{self.hilera_asignada}P{self.posicion_actual})"

    def esperar(self):
        return "Esperar"

    def finalizar(self):
        # Regresar al inicio si es necesario
        instrucciones_regreso = ListaEnlazada()
        while self.posicion_actual > 0:
            instrucciones_regreso.agregar(self.mover_atras())
        return instrucciones_regreso

    def to_dict(self):
        dict_obj = DiccionarioSimple()
        dict_obj.agregar("id", self.id)
        dict_obj.agregar("nombre", self.nombre)
        dict_obj.agregar("hilera_asignada", self.hilera_asignada)
        dict_obj.agregar("agua_usada", self.agua_usada)
        dict_obj.agregar("fertilizante_usado", self.fertilizante_usado)
        return dict_obj
    def __str__(self):
        return f"{self.nombre} (Hilera {self.hilera_asignada})"


class InstruccionDron:
    def __init__(self, nombre_dron, accion):
        self.nombre_dron = nombre_dron
        self.accion = accion

    def __str__(self):
        return f"{self.nombre_dron}: {self.accion}"

    def to_dict(self):
        dict_obj = DiccionarioSimple()
        dict_obj.agregar("dron", self.nombre_dron)
        dict_obj.agregar("accion", self.accion)
        return dict_obj


class InstruccionTiempo:
    def __init__(self, segundo):
        self.segundo = segundo
        self.instrucciones_drones = ListaEnlazada()

    def agregar_instruccion(self, nombre_dron, accion):
        instruccion = InstruccionDron(nombre_dron, accion)
        self.instrucciones_drones.agregar(instruccion)

    def __str__(self):
        return f"Tiempo {self.segundo}s: {len(self.instrucciones_drones)} instrucciones"

class Planta:
    def __init__(self, hilera, posicion, litros_agua, gramos_fertilizante, nombre_planta):
        self.hilera = hilera
        self.posicion = posicion
        self.litros_agua = litros_agua
        self.gramos_fertilizante = gramos_fertilizante
        self.nombre_planta = nombre_planta

    def __str__(self):
        return f"H{self.hilera}-P{self.posicion} ({self.nombre_planta})"


class Invernadero:
    def __init__(self, nombre, num_hileras, plantas_por_hilera):
        self.nombre = nombre
        self.num_hileras = num_hileras
        self.plantas_por_hilera = plantas_por_hilera
        self.plantas = ListaEnlazada()  # Todas las plantas
        self.drones_asignados = ListaEnlazada()  # Drones asignados a este invernadero
        self.planes_riego = ListaEnlazada()  # Planes de riego para este invernadero

    def obtener_planta(self, hilera, posicion):
        """Busca una planta específica en la lista"""
        for planta in self.plantas:
            if planta.hilera == hilera and planta.posicion == posicion:
                return planta
        return None

    def obtener_dron_por_hilera(self, hilera):
        """Obtiene el dron asignado a una hilera específica"""
        for dron in self.drones_asignados:
            if dron.hilera_asignada == hilera:
                return dron
        return None

    def obtener_dron_por_id(self, id_dron):
        """Obtiene un dron por su ID"""
        for dron in self.drones_asignados:
            if dron.id == id_dron:
                return dron
        return None

    def to_dict(self):
        dict_obj = DiccionarioSimple()
        dict_obj.agregar("nombre", self.nombre)
        dict_obj.agregar("num_hileras", self.num_hileras)
        dict_obj.agregar("plantas_por_hilera", self.plantas_por_hilera)
        return dict_obj


class CoordenadaPlanta:
    def __init__(self, hilera, posicion):
        self.hilera = hilera
        self.posicion = posicion

    def __str__(self):
        return f"H{self.hilera}-P{self.posicion}"


class UtilString:
    @staticmethod
    def split(cadena, delimitador):
        """Implementación propia de split usando ListaEnlazada"""
        resultado = ListaEnlazada()
        parte_actual = ""

        # Necesitamos iterar caracter por caracter
        for i in range(len(cadena)):
            caracter = cadena[i]
            if caracter == delimitador:
                if parte_actual:
                    resultado.agregar(parte_actual)
                    parte_actual = ""
            else:
                parte_actual += caracter

        # Agregar la última parte
        if parte_actual:
            resultado.agregar(parte_actual)

        return resultado

    @staticmethod
    def extraer_numero_despues_de_prefijo(cadena, prefijo):
        """Extrae el número después de un prefijo sin usar slicing"""
        numero_str = ""
        encontrado_prefijo = False
        indice_prefijo = 0
        longitud_prefijo = len(prefijo)

        # Iterar por cada caracter
        for i in range(len(cadena)):
            caracter = cadena[i]

            if not encontrado_prefijo:
                # Buscar el prefijo
                if indice_prefijo < longitud_prefijo and caracter == prefijo[indice_prefijo]:
                    indice_prefijo += 1
                    if indice_prefijo == longitud_prefijo:
                        encontrado_prefijo = True
                else:
                    indice_prefijo = 0
            else:
                # Ya encontramos el prefijo, extraer números
                if caracter.isdigit():
                    numero_str += caracter
                else:
                    break

        return int(numero_str) if numero_str else 0

    @staticmethod
    def strip(cadena):
        """Implementación propia de strip"""
        if not cadena:
            return ""

        inicio = 0
        fin = len(cadena) - 1

        # Encontrar inicio no espaciado
        while inicio <= fin and cadena[inicio].isspace():
            inicio += 1

        # Encontrar fin no espaciado
        while fin >= inicio and cadena[fin].isspace():
            fin -= 1

        # Reconstruir string sin espacios
        resultado = ""
        for i in range(inicio, fin + 1):
            resultado += cadena[i]

        return resultado


class PlanRiego:
    def __init__(self, nombre, secuencia):
        self.nombre = nombre
        self.secuencia = secuencia
        self.secuencia_parseada = ListaEnlazada()
        self.tiempo_optimo = 0
        self.agua_total = 0
        self.fertilizante_total = 0
        self.instrucciones_por_tiempo = ListaEnlazada()

    def parsear_secuencia(self):
        """Convierte la cadena de secuencia en una lista de CoordenadaPlanta"""
        self.secuencia_parseada = ListaEnlazada()
        elementos = UtilString.split(self.secuencia, ',')

        for i in range(len(elementos)):
            elemento = elementos.obtener(i)
            elemento_limpio = UtilString.strip(elemento)

            if elemento_limpio:
                partes = UtilString.split(elemento_limpio, '-')

                if len(partes) == 2:
                    parte_hilera = partes.obtener(0)
                    parte_posicion = partes.obtener(1)

                    hilera = UtilString.extraer_numero_despues_de_prefijo(parte_hilera, 'H')
                    posicion = UtilString.extraer_numero_despues_de_prefijo(parte_posicion, 'P')

                    coordenada = CoordenadaPlanta(hilera, posicion)
                    self.secuencia_parseada.agregar(coordenada)

    def __str__(self):
        return f"Plan {self.nombre}: {self.secuencia}"
class Sistema:
    def __init__(self):
        self.drones = ListaEnlazada()  # Todos los drones disponibles
        self.invernaderos = ListaEnlazada()  # Todos los invernaderos

    def obtener_invernadero_por_nombre(self, nombre):
        """Busca un invernadero por nombre"""
        for invernadero in self.invernaderos:
            if invernadero.nombre == nombre:
                return invernadero
        return None

    def limpiar_sistema(self):
        """Limpia todas las configuraciones previas"""
        self.drones = ListaEnlazada()
        self.invernaderos = ListaEnlazada()


class Simulador:
    def __init__(self):
        self.tiempo_actual = 0
        self.instrucciones_totales = ListaEnlazada()

    def simular_plan(self, invernadero, plan):
        """Simula to-do el plan de riego para un invernadero"""
        # Reiniciar estado de drones
        self.reiniciar_drones(invernadero)

        # Parsear la secuencia si no está parseada
        if len(plan.secuencia_parseada) == 0:
            plan.parsear_secuencia()

        # Simular cada planta en la secuencia
        for coordenada in plan.secuencia_parseada:
            self.simular_planta(invernadero, plan, coordenada)

        # Hacer que todos los drones regresen al inicio
        self.regresar_drones_al_inicio(invernadero, plan)

        # Calcular estadísticas finales
        self.calcular_estadisticas(invernadero, plan)

        return plan

    def reiniciar_drones(self, invernadero):
        """Reinicia la posición y estadísticas de todos los drones"""
        for dron in invernadero.drones_asignados:
            dron.posicion_actual = 0
            dron.agua_usada = 0
            dron.fertilizante_usado = 0
            dron.instrucciones = ListaEnlazada()

    def simular_planta(self, invernadero, plan, coordenada):
        """Simula el riego de una planta específica"""
        hilera = coordenada.hilera
        posicion_deseada = coordenada.posicion

        # Obtener el dron de esta hilera
        dron = invernadero.obtener_dron_por_hilera(hilera)
        if not dron:
            return

        # Obtener la planta objetivo
        planta = invernadero.obtener_planta(hilera, posicion_deseada)
        if not planta:
            return

        # Mover el dron a la posición deseada
        self.mover_dron_a_posicion(invernadero, dron, posicion_deseada, plan)

        # Regar la planta
        self.regar_planta(invernadero, dron, planta, plan)

    def mover_dron_a_posicion(self, invernadero, dron, posicion_deseada, plan):
        """Mueve el dron a la posición objetivo"""
        while dron.posicion_actual != posicion_deseada:
            self.tiempo_actual += 1
            instruccion_tiempo = InstruccionTiempo(self.tiempo_actual)

            if dron.posicion_actual < posicion_deseada:
                # Mover adelante
                accion = dron.mover_adelante()
                instruccion_tiempo.agregar_instruccion(dron.nombre, accion)
            else:
                # Mover atrás
                accion = dron.mover_atras()
                instruccion_tiempo.agregar_instruccion(dron.nombre, accion)

            # Los otros drones esperan
            self.agregar_instrucciones_espera(invernadero, dron, instruccion_tiempo)

            plan.instrucciones_por_tiempo.agregar(instruccion_tiempo)

    def regar_planta(self, invernadero, dron, planta, plan):
        """Realiza el riego de la planta"""
        self.tiempo_actual += 1
        instruccion_tiempo = InstruccionTiempo(self.tiempo_actual)

        # Dron objetivo riega
        accion = dron.regar(planta)
        instruccion_tiempo.agregar_instruccion(dron.nombre, accion)

        # Los otros drones esperan
        self.agregar_instrucciones_espera(invernadero, dron, instruccion_tiempo)

        plan.instrucciones_por_tiempo.agregar(instruccion_tiempo)

    def agregar_instrucciones_espera(self, invernadero, dron_activo, instruccion_tiempo):
        """Agrega instrucciones de espera para los drones inactivos"""
        for dron in invernadero.drones_asignados:
            if dron != dron_activo:
                # Verificar si el dron ya terminó
                if dron.posicion_actual > 0:
                    # Si no ha terminado, espera
                    instruccion_tiempo.agregar_instruccion(dron.nombre, dron.esperar())
                else:
                    # Si ya terminó, puede mostrar FIN
                    instruccion_tiempo.agregar_instruccion(dron.nombre, "FIN")

    def regresar_drones_al_inicio(self, invernadero, plan):
        """Hace que todos los drones regresen al inicio"""
        for dron in invernadero.drones_asignados:
            while dron.posicion_actual > 0:
                self.tiempo_actual += 1
                instruccion_tiempo = InstruccionTiempo(self.tiempo_actual)

                # Dron activo retrocede
                accion = dron.mover_atras()
                instruccion_tiempo.agregar_instruccion(dron.nombre, accion)

                # Los otros drones esperan o muestran FIN
                self.agregar_instrucciones_espera(invernadero, dron, instruccion_tiempo)

                plan.instrucciones_por_tiempo.agregar(instruccion_tiempo)

    def calcular_estadisticas(self, invernadero, plan):
        """Calcula las estadísticas finales del plan"""
        plan.tiempo_optimo = self.tiempo_actual

        # Calcular totales de agua y fertilizante
        for dron in invernadero.drones_asignados:
            plan.agua_total += dron.agua_usada
            plan.fertilizante_total += dron.fertilizante_usado