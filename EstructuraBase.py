class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

    def __str__(self):
        return str(self.dato)

class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.cola = None  # Para inserción rápida al final
        self.longitud = 0

    def agregar(self, dato):
        """Agrega un elemento al final de la lista"""
        nuevo_nodo = Nodo(dato)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo
        self.longitud += 1

    def obtener(self, indice):
        """Obtiene el elemento en la posición indicada"""
        if indice < 0 or indice >= self.longitud:
            raise IndexError("Índice fuera de rango")
        actual = self.cabeza
        for i in range(indice):
            actual = actual.siguiente
        return actual.dato

    def esta_vacia(self):
        return self.cabeza is None

    def __len__(self):
        return self.longitud

    def __iter__(self):
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente

    def __str__(self):
        return "[" + ", ".join(str(item) for item in self) + "]"

    def __len__(self):
        return self.longitud
class Cola:
    def __init__(self):
        self.frente = None
        self.final = None
        self.longitud = 0

    def encolar(self, dato):
        nuevo_nodo = Nodo(dato)
        if self.esta_vacia():
            self.frente = nuevo_nodo
            self.final = nuevo_nodo
        else:
            self.final.siguiente = nuevo_nodo
            self.final = nuevo_nodo
        self.longitud += 1

    def desencolar(self):
        if self.esta_vacia():
            return None
        dato = self.frente.dato
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        self.longitud -= 1
        return dato

    def frente_cola(self):
        return self.frente.dato if self.frente else None

    def esta_vacia(self):
        return self.frente is None

    def __len__(self):
        return self.longitud

    def __iter__(self):
        actual = self.frente
        while actual:
            yield actual.dato
            actual = actual.siguiente

class Pila:
    def __init__(self):
        self.tope = None
        self.longitud = 0

    def apilar(self, dato):
        nuevo_nodo = Nodo(dato)
        nuevo_nodo.siguiente = self.tope
        self.tope = nuevo_nodo
        self.longitud += 1

    def desapilar(self):
        if self.esta_vacia():
            return None
        dato = self.tope.dato
        self.tope = self.tope.siguiente
        self.longitud -= 1
        return dato

    def ver_tope(self):
        return self.tope.dato if self.tope else None

    def esta_vacia(self):
        return self.tope is None

    def __len__(self):
        return self.longitud


class DiccionarioSimple:
    def __init__(self):
        self.claves = ListaEnlazada()
        self.valores = ListaEnlazada()

    def agregar(self, clave, valor):
        self.claves.agregar(clave)
        self.valores.agregar(valor)

    def get(self, clave, default=None):

        valor = self.obtener(clave)
        return valor if valor is not None else default

    def obtener(self, clave):
        for i in range(len(self.claves)):
            if self.claves.obtener(i) == clave:
                return self.valores.obtener(i)
        return None

    def items(self):

        items_lista = ListaEnlazada()
        for clave, valor in self:
            items_lista.agregar((clave, valor))
        return items_lista

    def __iter__(self):
        for i in range(len(self.claves)):
            yield (self.claves.obtener(i), self.valores.obtener(i))

class ListaSerializable(ListaEnlazada):
    def to_dict(self):
        """Convierte la lista enlazada a formato serializable sin usar listas nativas"""
        # Creamos una cadena JSON manualmente por lo de las estructuras nativas y poder ver el procesoooo
        json_str = "["
        primero = True

        actual = self.cabeza
        while actual:
            if not primero:
                json_str += ","
            primero = False

            if hasattr(actual.dato, 'to_dict'):
                json_str += actual.dato.to_dict()
            else:
                # Convertir a string escapando comillas
                dato_str = str(actual.dato).replace('"', '\\"')
                json_str += f'"{dato_str}"'

            actual = actual.siguiente

        json_str += "]"
        return json_str


class JsonSerializable:
    def to_dict(self):
        """Convierte el objeto a string JSON a manitax"""
        raise NotImplementedError("Método to_dict debe ser implementado")

    def _serializar_valor(self, valor):
        """Serializa un valor individual"""
        if hasattr(valor, 'to_dict'):
            return valor.to_dict()
        elif isinstance(valor, str):
            return f'"{valor}"'
        else:
            return str(valor)