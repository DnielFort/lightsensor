import auxiliares
from data_functions import *

# Función que devuelve True si el valor de la luz es mayor que 1000, y False en caso contrario.
def light_on():
    return auxiliares.read_light() > 1000

"""
Continuar aquí, manejo del modulo relé
"""