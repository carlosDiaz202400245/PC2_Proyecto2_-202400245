from EstructuraBase import ListaEnlazada, DiccionarioSimple
import time


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


class Sistema:
    def __init__(self):
        self.drones = ListaEnlazada()
        self.invernaderos = ListaEnlazada()
        self.simulador = Simulador()

    def agregar_dron(self, dron):
        """Agrega un dron al sistema"""
        self.drones.agregar(dron)

    def agregar_invernadero(self, invernadero):
        """Agrega un invernadero al sistema"""
        self.invernaderos.agregar(invernadero)

    def obtener_invernadero_por_nombre(self, nombre):
        """Busca un invernadero por nombre"""
        for i in range(self.invernaderos.longitud):
            invernadero = self.invernaderos.obtener(i)
            if invernadero.nombre == nombre:
                return invernadero
        return None

    def obtener_dron_por_nombre(self, nombre):
        """Busca un dron por nombre"""
        for i in range(self.drones.longitud):
            dron = self.drones.obtener(i)
            if dron.nombre == nombre:
                return dron
        return None

    def asignar_dron_a_invernadero(self, nombre_dron, nombre_invernadero, hilera):
        """Asigna un dron a un invernadero específico"""
        dron = self.obtener_dron_por_nombre(nombre_dron)
        invernadero = self.obtener_invernadero_por_nombre(nombre_invernadero)

        if dron and invernadero:
            dron.hilera_asignada = hilera
            invernadero.drones_asignados.agregar(dron)
            return True
        return False

    def crear_plan_riego(self, nombre_invernadero, nombre_plan, secuencia):
        """Crea un plan de riego para un invernadero"""
        invernadero = self.obtener_invernadero_por_nombre(nombre_invernadero)
        if invernadero:
            plan = PlanRiego(nombre_plan, secuencia)
            invernadero.planes_riego.agregar(plan)
            return plan
        return None

    def simular_plan(self, nombre_invernadero, nombre_plan):
        """Simula un plan de riego"""
        invernadero = self.obtener_invernadero_por_nombre(nombre_invernadero)
        if invernadero:
            for i in range(invernadero.planes_riego.longitud):
                plan = invernadero.planes_riego.obtener(i)
                if plan.nombre == nombre_plan:
                    return self.simulador.simular_plan(invernadero, plan)
        return None

    def limpiar_sistema(self):
        """Limpia todas las configuraciones previas"""
        self.drones = ListaEnlazada()
        self.invernaderos = ListaEnlazada()
        self.simulador = Simulador()

    def mostrar_estado(self):
        """Muestra el estado actual del sistema"""

        for i in range(self.invernaderos.longitud):
            invernadero = self.invernaderos.obtener(i)


class Dron:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.hilera_asignada = None
        self.posicion_actual = 0
        self.agua_usada = 0
        self.fertilizante_usado = 0
        self.instrucciones = ListaEnlazada()
        self.ha_regado = False
        self.completado = False
        self.planta_objetivo = None
        self.plantas_pendientes = ListaEnlazada()

    def asignar_hilera_y_planta(self, hilera, planta_objetivo):
        self.hilera_asignada = hilera
        self.planta_objetivo = planta_objetivo

    def agregar_planta_pendiente(self, posicion_planta):
        """Agrega una planta a la lista de pendientes"""
        self.plantas_pendientes.agregar(posicion_planta)
        if self.planta_objetivo is None and self.plantas_pendientes.longitud > 0:
            self.planta_objetivo = self.plantas_pendientes.obtener(0)

    def obtener_siguiente_planta(self):
        """Obtiene la siguiente planta pendiente"""
        if self.plantas_pendientes.longitud > 0:
            self.planta_objetivo = self.plantas_pendientes.obtener(0)
            return self.planta_objetivo
        return None

    def completar_planta_actual(self):
        """Marca la planta actual como completada - CORREGIDO"""
        if self.plantas_pendientes.longitud > 0:

            nuevas_plantas = ListaEnlazada()
            for i in range(1, self.plantas_pendientes.longitud):
                nuevas_plantas.agregar(self.plantas_pendientes.obtener(i))
            self.plantas_pendientes = nuevas_plantas

            self.ha_regado = False

            # Establecer siguiente planta si es q hay más va
            if self.plantas_pendientes.longitud > 0:
                self.planta_objetivo = self.plantas_pendientes.obtener(0)
            else:
                self.planta_objetivo = None
            return True
        return False

    def mover_adelante(self):
        if (not self.completado and
                self.planta_objetivo is not None and
                self.posicion_actual < self.planta_objetivo):
            self.posicion_actual += 1
            return f"Adelante (H{self.hilera_asignada}P{self.posicion_actual})"
        return "Esperar"

    def mover_atras(self):
        if self.posicion_actual > 0:
            self.posicion_actual -= 1
            if self.posicion_actual == 0:
                self.completado = True
                return "FIN"
            return f"Atrás (H{self.hilera_asignada}P{self.posicion_actual})"
        elif self.posicion_actual == 0:
            self.completado = True
            return "FIN"
        return "Esperar"

    def puede_regar(self):
        return (not self.ha_regado and
                self.planta_objetivo is not None and
                self.posicion_actual == self.planta_objetivo and
                not self.completado)

    def regar(self, planta):
        if self.puede_regar():
            self.agua_usada += planta.litros_agua
            self.fertilizante_usado += planta.gramos_fertilizante
            self.ha_regado = True
            return f"Regar (H{self.hilera_asignada}P{self.posicion_actual})"
        return "Esperar"

    def esperar(self):
        return "Esperar"

    def tiene_plantas_pendientes(self):
        return self.plantas_pendientes.longitud > 0

    def __str__(self):
        return f"{self.nombre} (Hilera {self.hilera_asignada}, Posición {self.posicion_actual}, Objetivo: {self.planta_objetivo})"

class InstruccionTiempo:
    def __init__(self, segundo):
        self.segundo = segundo
        self.instrucciones_drones = ListaEnlazada()

    def agregar_instruccion(self, nombre_dron, accion):
        instruccion = InstruccionDron(nombre_dron, accion)
        self.instrucciones_drones.agregar(instruccion)

    def __str__(self):
        return f"Tiempo {self.segundo}s: {self.instrucciones_drones.longitud} instrucciones"


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
        self.plantas = ListaEnlazada()
        self.drones_asignados = ListaEnlazada()
        self.planes_riego = ListaEnlazada()

    def obtener_planta(self, hilera, posicion):
        for i in range(self.plantas.longitud):
            planta = self.plantas.obtener(i)
            if planta.hilera == hilera and planta.posicion == posicion:
                return planta
        return None

    def obtener_dron_por_hilera(self, hilera):
        for i in range(self.drones_asignados.longitud):
            dron = self.drones_asignados.obtener(i)
            if dron.hilera_asignada == hilera:
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
        resultado = ListaEnlazada()
        parte_actual = ""

        for i in range(len(cadena)):
            caracter = cadena[i]
            if caracter == delimitador:
                if parte_actual:
                    resultado.agregar(parte_actual)
                    parte_actual = ""
            else:
                parte_actual += caracter

        if parte_actual:
            resultado.agregar(parte_actual)

        return resultado

    @staticmethod
    def extraer_numero_despues_de_prefijo(cadena, prefijo):
        numero_str = ""
        encontrado_prefijo = False
        indice_prefijo = 0

        for i in range(len(cadena)):
            caracter = cadena[i]

            if not encontrado_prefijo:
                if indice_prefijo < len(prefijo) and caracter == prefijo[indice_prefijo]:
                    indice_prefijo += 1
                    if indice_prefijo == len(prefijo):
                        encontrado_prefijo = True
                else:
                    indice_prefijo = 0
            else:
                if caracter.isdigit():
                    numero_str += caracter
                else:
                    break

        return int(numero_str) if numero_str else 0

    @staticmethod
    def strip(cadena):
        if not cadena:
            return ""

        inicio = 0
        fin = len(cadena) - 1

        while inicio <= fin and cadena[inicio].isspace():
            inicio += 1

        while fin >= inicio and cadena[fin].isspace():
            fin -= 1

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
        self.secuencia_parseada = ListaEnlazada()
        elementos = UtilString.split(self.secuencia, ',')

        for i in range(elementos.longitud):
            elemento = elementos.obtener(i)
            elemento_limpio = UtilString.strip(elemento)

            if elemento_limpio:
                partes = UtilString.split(elemento_limpio, '-')

                if partes.longitud == 2:
                    parte_hilera = partes.obtener(0)
                    parte_posicion = partes.obtener(1)

                    hilera = UtilString.extraer_numero_despues_de_prefijo(parte_hilera, 'H')
                    posicion = UtilString.extraer_numero_despues_de_prefijo(parte_posicion, 'P')

                    coordenada = CoordenadaPlanta(hilera, posicion)
                    self.secuencia_parseada.agregar(coordenada)

    def __str__(self):
        return f"Plan {self.nombre}: {self.secuencia}"


class Simulador:
    def __init__(self):
        self.tiempo_actual = 0

    def simular_plan(self, invernadero, plan):
        self.tiempo_actual = 0
        self.reiniciar_drones(invernadero)
        plan.instrucciones_por_tiempo = ListaEnlazada()

        if plan.secuencia_parseada.longitud == 0:
            plan.parsear_secuencia()

        plantas_por_dron = self.asignar_plantas_corregido(invernadero, plan.secuencia_parseada)
        return self.simulacion_corregida(invernadero, plan, plantas_por_dron)

    def asignar_plantas_corregido(self, invernadero, secuencia_plantas):
        """Usar solo estructuras personalizadas"""
        plantas_por_dron = DiccionarioSimple()

        for i in range(invernadero.drones_asignados.longitud):
            dron = invernadero.drones_asignados.obtener(i)
            plantas_por_dron.agregar(dron.nombre, ListaEnlazada())

        for i in range(secuencia_plantas.longitud):
            coord = secuencia_plantas.obtener(i)
            dron = invernadero.obtener_dron_por_hilera(coord.hilera)
            if dron:
                plantas_lista = plantas_por_dron.obtener(dron.nombre)
                plantas_lista.agregar(coord.posicion)

        for i in range(invernadero.drones_asignados.longitud):
            dron = invernadero.drones_asignados.obtener(i)
            plantas_lista = plantas_por_dron.obtener(dron.nombre)

            dron.plantas_pendientes = ListaEnlazada()
            for j in range(plantas_lista.longitud):
                dron.plantas_pendientes.agregar(plantas_lista.obtener(j))

            if dron.plantas_pendientes.longitud > 0:
                dron.planta_objetivo = dron.plantas_pendientes.obtener(0)
            else:
                dron.planta_objetivo = None

        return plantas_por_dron

    def simulacion_corregida(self, invernadero, plan, plantas_por_dron):
        """CORRECCIÓN DEFINITIVA del tiempo óptimo"""
        max_tiempo = 50
        tiempo_real_final = 0  # Nuevo contador para el tiempo real

        # Fase 1: Simulación principal
        for tiempo in range(1, max_tiempo + 1):
            self.tiempo_actual = tiempo
            instruccion_tiempo = InstruccionTiempo(tiempo)
            riego_permitido = True
            tiempo_tiene_acciones = False
            todos_completados = True

            for i in range(invernadero.drones_asignados.longitud):
                dron = invernadero.drones_asignados.obtener(i)

                if not dron.completado:
                    todos_completados = False
                    accion = self.obtener_accion_corregida(dron, riego_permitido, invernadero)
                    instruccion_tiempo.agregar_instruccion(dron.nombre, accion)

                    if "Regar" in accion:
                        riego_permitido = False
                        self.aplicar_riego_real(dron, invernadero)

                    if "FIN" not in accion and "Esperar" not in accion:
                        tiempo_tiene_acciones = True
                else:
                    instruccion_tiempo.agregar_instruccion(dron.nombre, "FIN")


            if tiempo_tiene_acciones:
                plan.instrucciones_por_tiempo.agregar(instruccion_tiempo)
                tiempo_real_final = tiempo  # Actualizar tiempo real
            elif not todos_completados:
                # Si no hay acciones pero aún no todos completaronagregar igual
                plan.instrucciones_por_tiempo.agregar(instruccion_tiempo)
                tiempo_real_final = tiempo
            else:

                tiempo_real_final = tiempo - 1  # El último tiempo con acciones fue el anterior
                break


            if todos_completados:

                if tiempo_tiene_acciones:
                    tiempo_real_final = tiempo
                else:

                    tiempo_real_final = tiempo - 1
                break


        if not self.todos_drones_completados(invernadero):
            self.asegurar_regreso_al_inicio(invernadero, plan, tiempo_real_final)


        if plan.instrucciones_por_tiempo.longitud > 0:
            ultimo_tiempo = plan.instrucciones_por_tiempo.obtener(plan.instrucciones_por_tiempo.longitud - 1)
            plan.tiempo_optimo = ultimo_tiempo.segundo
        else:
            plan.tiempo_optimo = tiempo_real_final

        self.calcular_estadisticas(invernadero, plan)
        return plan

    def todos_drones_completados(self, invernadero):
        """Verificar si todos los drones están completados"""
        for i in range(invernadero.drones_asignados.longitud):
            dron = invernadero.drones_asignados.obtener(i)
            if not dron.completado:
                return False
        return True

    def asegurar_regreso_al_inicio(self, invernadero, plan, tiempo_inicio):
        """Asegurar regreso completo empezando desde tiempo_inicio"""
        tiempo_actual = tiempo_inicio

        while not self.todos_drones_completados(invernadero) and tiempo_actual < 60:
            tiempo_actual += 1
            instruccion_tiempo = InstruccionTiempo(tiempo_actual)
            movimiento_ocurrio = False

            for i in range(invernadero.drones_asignados.longitud):
                dron = invernadero.drones_asignados.obtener(i)

                if not dron.completado and dron.posicion_actual > 0:
                    dron.posicion_actual -= 1
                    if dron.posicion_actual == 0:
                        dron.completado = True
                        instruccion_tiempo.agregar_instruccion(dron.nombre, "FIN")
                    else:
                        instruccion_tiempo.agregar_instruccion(dron.nombre,
                                                               f"Atrás (H{dron.hilera_asignada}P{dron.posicion_actual})")
                    movimiento_ocurrio = True
                else:
                    dron.completado = True
                    instruccion_tiempo.agregar_instruccion(dron.nombre, "FIN")

            if movimiento_ocurrio:
                plan.instrucciones_por_tiempo.agregar(instruccion_tiempo)
            else:
                break

    def obtener_accion_corregida(self, dron, riego_permitido, invernadero):
        if dron.completado:
            return "FIN"

        if dron.plantas_pendientes.longitud == 0:
            return self.mover_al_inicio(dron)

        if dron.planta_objetivo is None and dron.plantas_pendientes.longitud > 0:
            dron.planta_objetivo = dron.plantas_pendientes.obtener(0)

        objetivo = dron.planta_objetivo

        if objetivo is None:
            return self.mover_al_inicio(dron)

        if dron.posicion_actual == objetivo:
            if not dron.ha_regado:
                if riego_permitido:
                    dron.ha_regado = True
                    dron.planta_actual = objetivo
                    return f"Regar (H{dron.hilera_asignada}P{objetivo})"
                else:
                    return "Esperar (riego ocupado)"
            else:
                return self.manejar_planta_completada(dron)
        elif dron.posicion_actual < objetivo:
            dron.posicion_actual += 1
            return f"Adelante (H{dron.hilera_asignada}P{dron.posicion_actual})"
        else:
            return self.mover_al_inicio(dron)

    def aplicar_riego_real(self, dron, invernadero):
        if hasattr(dron, 'planta_actual'):
            planta_real = invernadero.obtener_planta(dron.hilera_asignada, dron.planta_actual)
            if planta_real:
                dron.agua_usada += planta_real.litros_agua
                dron.fertilizante_usado += planta_real.gramos_fertilizante
                self.marcar_planta_completada(dron)

    def marcar_planta_completada(self, dron):
        if dron.plantas_pendientes.longitud > 0:
            nuevas_plantas = ListaEnlazada()
            for i in range(1, dron.plantas_pendientes.longitud):
                nuevas_plantas.agregar(dron.plantas_pendientes.obtener(i))
            dron.plantas_pendientes = nuevas_plantas

            dron.ha_regado = False
            dron.planta_actual = None

            if dron.plantas_pendientes.longitud > 0:
                dron.planta_objetivo = dron.plantas_pendientes.obtener(0)
            else:
                dron.planta_objetivo = None

    def manejar_planta_completada(self, dron):
        self.marcar_planta_completada(dron)

        if dron.planta_objetivo is not None:
            if dron.posicion_actual < dron.planta_objetivo:
                dron.posicion_actual += 1
                return f"Adelante (H{dron.hilera_asignada}P{dron.posicion_actual})"
            else:
                return self.mover_al_inicio(dron)
        else:
            return self.mover_al_inicio(dron)

    def mover_al_inicio(self, dron):
        if dron.posicion_actual > 0:
            dron.posicion_actual -= 1
            if dron.posicion_actual == 0:
                dron.completado = True
                return "FIN"
            return f"Atrás (H{dron.hilera_asignada}P{dron.posicion_actual})"
        else:
            dron.completado = True
            return "FIN"

    def reiniciar_drones(self, invernadero):
        for i in range(invernadero.drones_asignados.longitud):
            dron = invernadero.drones_asignados.obtener(i)
            dron.posicion_actual = 0
            dron.agua_usada = 0
            dron.fertilizante_usado = 0
            dron.ha_regado = False
            dron.completado = False
            dron.planta_objetivo = None
            dron.planta_actual = None
            dron.plantas_pendientes = ListaEnlazada()

    def calcular_estadisticas(self, invernadero, plan):
        plan.agua_total = 0
        plan.fertilizante_total = 0
        for i in range(invernadero.drones_asignados.longitud):
            dron = invernadero.drones_asignados.obtener(i)
            plan.agua_total += dron.agua_usada
            plan.fertilizante_total += dron.fertilizante_usado

