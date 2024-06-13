#!/usr/bin/python

import sys
import smbus
import time
import eeml
from Adafruit_I2C import Adafruit_I2C
from array import *
from datetime import datetime
import urllib
import urllib2
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN)
#procesamiento a partir de Xively
API_KEY = '' # The API key
FEED = 98565
API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)
streamName = 2
name = ""

"""
Este código es un programa que recoge datos de un sensor de luz, calcula los promedios de las lecturas y los escribe en un archivo CSV.

"""

class Luxmeter:
    i2c = None

    def __init__(self, address=0x39, debug=0, pause=1):
        # Esta es la función de inicialización de la clase Luxmeter. 
        # Se llama automáticamente cuando se crea un nuevo objeto de esta clase.
        # Los parámetros son:
        # address: la dirección I2C del dispositivo. Por defecto es 0x39.
        self.i2c = Adafruit_I2C(address)
        self.address = address       
        # debug: un indicador para habilitar o deshabilitar el modo de depuración. Por defecto es 0 (desactivado).
        self.debug = debug
        # pause: el tiempo de pausa entre las lecturas del sensor. Por defecto es 1 segundo.
        self.pause = pause


        self.i2c.write8(0x80, 0x03)     # enable the device
        self.i2c.write8(0x81, 0x12)     #  gain = 16X y timing = 101 mSec
        time.sleep(self.pause)          # pause 


    def readfull(self, reg=0x8C):
        """
            Esta función lee los valores de los diodos visibles e IR del dispositivo I2C.
            Parámetros:
            reg: el registro desde el cual leer los datos. Por defecto es 0x8C.
        """       
        try:
            fullval = self.i2c.readU16(reg)
            newval = self.i2c.reverseByteOrder(fullval)
            if (self.debug):
                print("I2C: Dispositivo 0x%02X devolvió 0x%04X desde el registro 0x%02X" % (self.address, fullval & 0xFFFF, reg))
            return newval
        except IOError:
            print("Error al acceder a 0x%02X: Verifica tu dirección I2C" % self.address)
            return -1


    def readIR(self, reg=0x8E):
        """
        Esta función lee solo los valores del diodo IR del dispositivo I2C.
        Parámetros:
        reg: el registro desde el cual leer los datos. Por defecto es 0x8E.
        """
        try:
            # Intenta leer un valor de 16 bits sin signo del registro especificado en el dispositivo I2C.
            IRval = self.i2c.readU16(reg)
            # Cambia el orden de los bytes del valor leído.
            newIR = self.i2c.reverseByteOrder(IRval)
            if (self.debug):
                # Si el modo de depuración está activado, imprime la dirección del dispositivo, el valor leído y el registro.
                print("I2C: Dispositivo 0x%02X devolvió 0x%04X desde el registro 0x%02X" % (self.address, IRval & 0xFFFF, reg))
            # Devuelve el valor leído con el orden de los bytes invertido.
            return newIR
        except IOError:
            # Si se produce un error de entrada/salida, imprime un mensaje de error con la dirección del dispositivo.
            print("Error al acceder a 0x%02X: Verifica tu dirección I2C" % self.address)
            # Devuelve -1 para indicar que se produjo un error.
            return -1
    
    def readfullauto(self, reg=0x8c):
        """
        Esta función lee los valores de los diodos visibles e IR del dispositivo I2C con autoajuste de rango.
        Parámetros:
        reg: el registro desde el cual leer los datos. Por defecto es 0x8C.
        """
        try:
            # Intenta leer un valor de 16 bits sin signo del registro especificado en el dispositivo I2C.
            fullval = self.i2c.readU16(reg)
            # Cambia el orden de los bytes del valor leído.
            newval = self.i2c.reverseByteOrder(fullval)
            if newval >= 37177:
                # Si el valor leído es mayor o igual a 37177, ajusta el rango del sensor.
                self.i2c.write8(0x81, 0x01)
                # Pausa la ejecución durante el tiempo especificado en self.pause.
                time.sleep(self.pause)
                # Lee de nuevo el valor del registro después de ajustar el rango.
                fullval = self.i2c.readU16(reg)
                # Cambia el orden de los bytes del valor leído.
                newval = self.i2c.reverseByteOrder(fullval)
            if (self.debug):
                # Si el modo de depuración está activado, imprime la dirección del dispositivo, el valor leído y el registro.
                print("I2C: Dispositivo 0x%02X devolvió 0x%04X desde el registro 0x%02X" % (self.address, fullval & 0xFFFF, reg))
            # Devuelve el valor leído con el orden de los bytes invertido.
            return newval
        except IOError:
            # Si se produce un error de entrada/salida, imprime un mensaje de error con la dirección del dispositivo.
            print("Error al acceder a 0x%02X: Verifica tu dirección I2C" % self.address)
            # Devuelve -1 para indicar que se produjo un error.
            return -1


    def readIRauto(self, reg=0x8e):
        """
            Esta función lee los valores del diodo IR del dispositivo I2C con autoajuste de rango.
            Parámetros:
            reg: el registro desde el cual leer los datos. Por defecto es 0x8E.
        """
        try:
            # Intenta leer un valor de 16 bits sin signo del registro especificado en el dispositivo I2C.
            IRval = self.i2c.readU16(reg)
            # Cambia el orden de los bytes del valor leído.
            newIR = self.i2c.reverseByteOrder(IRval)
            if newIR >= 37177:
                # Si el valor leído es mayor o igual a 37177, ajusta el rango del sensor.
                self.i2c.write8(0x81, 0x01)     #   elimina la ganancia de 16x
                # Pausa la ejecución durante el tiempo especificado en self.pause.
                time.sleep(self.pause)
                # Lee de nuevo el valor del registro después de ajustar el rango.
                IRval = self.i2c.readU16(reg)
                # Cambia el orden de los bytes del valor leído.
                newIR = self.i2c.reverseByteOrder(IRval)
            if (self.debug):
                # Si el modo de depuración está activado, imprime la dirección del dispositivo, el valor leído y el registro.
                print("I2C: Dispositivo 0x%02X devolvió 0x%04X desde el registro 0x%02X" % (self.address, IRval & 0xFFFF, reg))
            # Devuelve el valor leído con el orden de los bytes invertido.
            return newIR
        except IOError:
            # Si se produce un error de entrada/salida, imprime un mensaje de error con la dirección del dispositivo.
            print("Error al acceder a 0x%02X: Verifica tu dirección I2C" % self.address)
            # Devuelve -1 para indicar que se produjo un error.
            return -1


def luxread(type, address = 0x39, debug = False, autorange = True):
    """
    Esta función obtiene una lectura de lux con o sin autoajuste de rango.
    Parámetros:
    type: no se utiliza en la función actual.
    address: la dirección del sensor de luz. Por defecto es 0x39.
    debug: un booleano que indica si se debe imprimir información de depuración. Por defecto es False.
    autorange: un booleano que indica si se debe utilizar el autoajuste de rango. Por defecto es True.
    """
    # Crea un objeto Luxmeter con la dirección especificada y el modo de depuración.
    LuxSensor = Luxmeter(0x39, False)
    if autorange == True:
        # Si el autoajuste de rango está activado, lee los valores de luz ambiental e IR con autoajuste de rango.
        ambient = LuxSensor.readfullauto()
        IR = LuxSensor.readIRauto()
    else:
         # Si el autoajuste de rango no está activado, lee los valores de luz ambiental e IR sin autoajuste de rango.
        ambient = LuxSensor.readfull()
        IR = LuxSensor.readIR()

    # Si la luz ambiental es 0 (es decir, está oscuro), establece la luz ambiental a un número pequeño para evitar la división por cero.
    if ambient == 0:
        ambient = 0.00001
        
    # Calcula la relación entre la luz IR y la luz ambiental.
    ratio = (float) (IR / ambient)

    # Calcula el valor de lux en función de la relación.
    if ((ratio >= 0) & (ratio <= 0.52)):
        lux = (0.0315 * ambient) - (0.0593 * ambient * (ratio**1.4))
    elif (ratio <= 0.65):
        lux = (0.0229 * ambient) - (0.0291 * IR)
    elif (ratio <= 0.80):
        lux = (0.0157 * ambient) - (0.018 * IR)
    elif (ratio <= 1.3):
        lux = (0.00338 * ambient) - (0.0026 * IR)
    elif (ratio > 1.3):
        lux = 0

    # Devuelve el valor de lux calculado.
    return lux


def writeData(s1, s2, s3):
    """
    Esta función escribe los datos proporcionados en un archivo CSV.
    Parámetros:
    s1, s2, s3: los datos a escribir en el archivo.
    """
    global name
    # Obtiene la hora actual.
    currentTime = datetime.now()
    # Abre el archivo CSV en modo de agregar.
    f = open(str(name)+".csv", "a")
    # Escribe los datos en el archivo, seguidos de una nueva línea.
    # Los datos están en el
    
def getdata():
    """
    Esta función recoge datos de un sensor de luz y los escribe en un archivo CSV.
    """
    global name
    # Crea listas para almacenar múltiples lecturas de luz IR, luz ambiental y lux.
    irbuffer=[]
    ambientbuffer=[]
    luxbuffer=[]

    # Realiza 20 lecturas de cada tipo de luz y las almacena en las listas correspondientes.
    for x in range(1,20):
        irbuffer.append(luxread(1, autorange=False))
        luxbuffer.append(luxread(3, autorange=False))
        ambientbuffer.append(luxread(2, autorange=False))

    # Calcula el valor promedio de cada tipo de luz.
    a = (sum(ambientbuffer) / len(ambientbuffer))
    b = int((sum(luxbuffer) / len(luxbuffer))) # convert to integer
    c = (sum(irbuffer) / len(irbuffer))

    # Escribe los valores promedio en un archivo CSV.
    writeData(a, b, c)

    # Devuelve los valores promedio en formato de cadena.
    return("Lux: %.2f Ambient: %.2f IR: %.2f" % (b, a, c))  


def minuteTimer():
    """
    Esta función realiza una cuenta atrás de 60 segundos.
    Durante la cuenta atrás, si se detecta una entrada en el pin GPIO 23, se cambia el feed de datos y se interrumpe la cuenta atrás.
    """
    # Imprime un mensaje de inicio de la cuenta atrás.
    print("Countdown")
    # Inicializa un contador.
    i = 0
    # Realiza la cuenta atrás durante 60 segundos.
    while i <= 60:
        # Si se detecta una entrada en el pin GPIO 23...
        if ( GPIO.input(23) == False ):
            # Imprime un mensaje de cambio de feed de datos.
            print("Changing feeds!")
            # Cambia el feed de datos.
            changeFeed()
            # Interrumpe la cuenta atrás.
            break
        # Incrementa el contador.
        i += 1
        # Espera un segundo antes de la próxima iteración.
        time.sleep(1)


print("Program started, logging to COSM, ctrl-C to end")  # a startup service message
name = "B-2" #DEBUG
try:
    while 1:
        # Obtiene los datos del sensor de luz y los imprime.
        print(getdata())  
        # Realiza una cuenta atrás de 60 segundos. Si se detecta una entrada en el pin GPIO 23, cambia el feed de datos.
        minuteTimer()   
except KeyboardInterrupt:
    # Si el usuario interrumpe el programa, imprime un mensaje de finalización.
    print("FIN")

