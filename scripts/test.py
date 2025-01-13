import sys, os
from ts2js import ConvertirCarpeta_
from bibpy.archivos import *
sys.path.insert(0, os.path.abspath(os.path.join('.','ts-parser','src')))
from parser import mostrarDiff, eq_string

tests = ['cero']

class Datos:
  def __init__(self, ruta):
    self.ruta = ruta
    self.r = len(ruta)
    self.archivos = {}
  def agregarArchivo(self, ruta):
    rutaCompleta = ruta
    rutaArchivo = rutaCompleta[self.r:]
    self.archivos[rutaArchivo] = Archivo(rutaCompleta)
  def MostrarArchivos(self):
    for ruta in self.archivos:
      print(ruta + " : " + self.archivos[ruta].ruta)
  def archivosGenerados(self):
    return self.archivos.keys()
  def generado(self, ruta):
    return ruta in self.archivos
  def abrir(self, ruta):
    return self.archivos[ruta].abrir()

class Archivo:
  def __init__(self, ruta):
    self.ruta = ruta
  def abrir(self):
    return contenidoDe_(self.ruta)

for test in tests:
  ConvertirCarpeta_(nuevaRuta_('test',test))
  esperado = nuevaRuta_('test',f"output-{test}")
  obtenido = nuevaRuta_('output',test)
  archivosEsperados = Datos(esperado)
  archivosObtenidos = Datos(obtenido)
  for ruta in todosLosArchivosEn_(esperado):
    archivosEsperados.agregarArchivo(ruta)
  for ruta in todosLosArchivosEn_(obtenido):
    archivosObtenidos.agregarArchivo(ruta)
  archivosObtenidos.MostrarArchivos()
  archivosEsperados.MostrarArchivos()
  for ruta in archivosEsperados.archivosGenerados():
    if not archivosObtenidos.generado(ruta):
      print(f"Faltó generar el archivo {ruta}")
      exit()
  for ruta in archivosObtenidos.archivosGenerados():
    if not archivosEsperados.generado(ruta):
      print(f"Se generó el archivo {ruta} adicional")
      exit()
  for ruta in archivosEsperados.archivosGenerados():
    esperado = archivosEsperados.abrir(ruta)
    obtenido = archivosObtenidos.abrir(ruta)
    print(ruta)
    if eq_string(esperado, obtenido):
      print("OK")
    else:
      mostrarDiff(esperado, obtenido)
      exit()