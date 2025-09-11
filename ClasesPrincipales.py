from EstructuraBase import ListaEnlazada
class Dron:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.hilera_asignada = None
        self.posicion_actual = 0
        self.agua_usada = 0
        self.fertilizante_usado = 0

class Planta:
    def __init__(self, hilera, posicion, litros_agua, gramos_fertilizante, nombre_planta):
        self.hilera = hilera
        self.posicion = posicion
        self.litros_agua = litros_agua
        self.gramos_fertilizante = gramos_fertilizante
        self.nombre_planta = nombre_planta

class Invernadero:
    def __init__(self, nombre, num_hileras, plantas_por_hilera):
        self.nombre = nombre
        self.num_hileras = num_hileras
        self.plantas_por_hilera = plantas_por_hilera
        self.plantas = ListaEnlazada()
        self.drones_asignados = ListaEnlazada()  #
        self.planes_riego = ListaEnlazada()

class PlanRiego:
    def __init__(self, nombre, secuencia):
        self.nombre = nombre
        self.secuencia = secuencia  # Ej: "H1-P2, H2-P1, ..."
        self.tiempo_optimo = 0
        self.agua_total = 0
        self.fertilizante_total = 0
        self.instrucciones = ListaEnlazada()  # Para almacenar las instrucciones por tiempo