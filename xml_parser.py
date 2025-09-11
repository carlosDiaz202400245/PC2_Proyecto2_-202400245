import xml.etree.ElementTree as ET
from EstructuraBase import *
from ClasesPrincipales import *

def cargar_configuracion(archivo_xml):
    tree = ET.parse(archivo_xml)
    root = tree.getroot()
    lista_drones = ListaEnlazada()
    for dron_elem in root.findall('.//dron'):
        id = dron_elem.get('id')
        nombre = dron_elem.get('nombre')
        lista_drones.agregar(Dron(id, nombre))
