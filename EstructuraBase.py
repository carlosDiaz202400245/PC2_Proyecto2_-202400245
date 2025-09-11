class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

    def __str__(self):
        return str(self.dato)

class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.longitud = 0

    def agregar(self, dato):
        nuevo_nodo = Nodo(dato)
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente is not None:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo
        self.longitud += 1

    def __iter__(self):
        actual = self.cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente

    def __len__(self):
        return self.longitud