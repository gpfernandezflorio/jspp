import sys, os
from datos import Datos
from bibpy.archivos import *
sys.path.insert(0, os.path.abspath(os.path.join('.','ts-parser','src')))
from main import parsearArchivo

CARPETA_SALIDA = 'output'
datosConversion = Datos()
generarSalida = False # True

def main():
  ConvertirCarpeta_("../../blockly/core/clipboard")
  exit(0)

  if len(sys.argv) == 1:
    Boom("No me pasaste ningún archivo ni carpeta")
  ruta = sys.argv[1]
  if existeArchivo_(ruta):
    ConvertirArchivo_(ruta)
  elif existeCarpeta_Acá(ruta):
    ConvertirCarpeta_(ruta)
  else:
    Boom("No se encuentra el archivo o carpeta " + ruta)

def ConvertirArchivo_(rutaArchivo):
  ast = parsearArchivo(rutaArchivo, False)
  return ast

def ConvertirCarpeta_(rutaCarpeta):
  if generarSalida:
    ReiniciarSalida()
  ConvertirCarpeta_En_(rutaCarpeta, datosConversion)
  datosConversion.limpiarRutas()
  datosConversion.MostrarArchivos()
  datosConversion.resolverDependencias()
  if generarSalida:
    escribirCarpeta_En_(datosConversion, CARPETA_SALIDA)

def ReiniciarSalida():
  if existeCarpeta_Acá(CARPETA_SALIDA):
    BorrarCarpeta_(CARPETA_SALIDA)
  CrearCarpeta_(CARPETA_SALIDA)

def ConvertirCarpeta_En_(rutaCarpeta, destino):
  nombreCarpeta = nombreDe_(rutaCarpeta)
  nuevoDestino = destino.agregarCarpeta(nombreCarpeta, rutaCarpeta)
  for carpeta in listaDeCarpetasEn_(rutaCarpeta):
    ConvertirCarpeta_En_(nuevaRuta_(rutaCarpeta, carpeta), nuevoDestino)
  for archivo in listaDeArchivosEn_(rutaCarpeta):
    nuevaRuta = nuevaRuta_(rutaCarpeta, archivo)
    ast = ConvertirArchivo_(nuevaRuta)
    nuevoDestino.agregarArchivo(archivo, nuevaRuta, ast)

def escribirCarpeta_En_(carpetaRaiz, rutaDestino):
  for archivo in carpetaRaiz.listaDeArchivos():
    CrearArchivo_En_Con_(archivo.nombre, rutaDestino, archivo.contenido())
  for carpeta in carpetaRaiz.listaDeCarpetas():
    CrearCarpeta_En_(carpeta.nombre, rutaDestino)
    rutaCarpeta = nuevaRuta_(rutaDestino, carpeta.nombre)
    escribirCarpeta_En_(carpeta, rutaCarpeta)

if __name__ == '__main__':
  main()