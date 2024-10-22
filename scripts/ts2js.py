import sys, os
from datos import Datos
from bibpy.archivos import nombreDe_, listaDeCarpetasEn_, listaDeArchivosEn_, existeCarpeta_Acá, nuevaRuta_
sys.path.insert(0, os.path.abspath(os.path.join('.','ts-parser','src')))
from main import parsearArchivo

CARPETA_SALIDA = 'output'
datosConversion = Datos()

def main():
  ConvertirCarpeta_("../../blockly/core/")
  ConvertirArchivo_("../../blockly/core/blockly.ts")
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
  parsearArchivo(rutaArchivo)

def ConvertirCarpeta_(rutaCarpeta):
  # ReiniciarSalida()
  ConvertirCarpeta_En_(rutaCarpeta, datosConversion)
  # datosConversion.MostrarArchivos()

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
    nuevoDestino.agregarArchivo(archivo, nuevaRuta_(rutaCarpeta, archivo))
    parsearArchivo(nuevaRuta_(rutaCarpeta, archivo))

if __name__ == '__main__':
  main()