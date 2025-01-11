import sys, os
from bibpy.listas import fold
sys.path.insert(0, os.path.abspath(os.path.join('.','ts-parser','src')))
from parser import *

class Archivo(object):
  def __init__(self, nombre, ruta, ast, carpetaContenedora):
    if nombre[-3:] == '.ts':
      self.nombre = nombre[:-3]
    else:
      falla()
    self.ruta = ruta
    self.ast = ast
    self.carpetaContenedora = carpetaContenedora
    self.importados = []
    self.exportados = []
  def limpiarRuta(self, pre):
    self.ruta = self.ruta[pre:]
  def contenido(self):
    return self.ast.toJs()
  def Mostrar(self, i=0, mostrarAST=False):
    tab = ""
    for j in range(i):
      tab += "  "
    print(f"{tab}{self.nombre} ({self.ruta})")
    print(f"{tab}  {list(map(lambda x : x.ls(), self.importados))}")
    for exportado in self.exportados:
      print(f"{tab}  {exportado}")
    if mostrarAST:
      print(self.ast)
      print("\n\n")
  def exponerExportados(self):
    for declaracion in self.ast.declaraciones:
      if isinstance(declaracion, AST_export):
        self.exportados.append(show(declaracion.exportable))
  def buscarDependencias(self):
    for declaracion in self.ast.declaraciones:
      if isinstance(declaracion, AST_import):
        self.importados.append(Referencia(declaracion, self))

class Referencia(object):
  def __init__(self, ast_import, archivoFuente):
    self.ast_import = ast_import
    carpetaActual = archivoFuente.carpetaContenedora
    rutaLocal = contenidoString(ast_import.archivo.literal)
    while rutaLocal.startswith('../'):
      carpetaActual = carpetaActual.carpetaContenedora
      rutaLocal = rutaLocal[3:]
    if rutaLocal.startswith('./'):
      rutaLocal = rutaLocal[2:]
    self.archivoDestino = carpetaActual.cd(rutaLocal)
  def ls(self):
    return self.archivoDestino.ruta

class Carpeta(object):
  def __init__(self, nombre, ruta, carpetaContenedora):
    self.nombre = nombre
    self.ruta = ruta
    self.carpetas = []
    self.archivos = []
    self.carpetaContenedora = carpetaContenedora
  def listaDeCarpetas(self):
    return self.carpetas
  def listaDeArchivos(self):
    return self.archivos
  def agregarCarpeta(self, nombreCarpeta, rutaCarpeta):
    nuevaCarpeta = Carpeta(nombreCarpeta, rutaCarpeta, self)
    self.carpetas.append(nuevaCarpeta)
    return nuevaCarpeta
  def agregarArchivo(self, nombreArchivo, rutaArchivo, astArchivo):
    archivo = Archivo(nombreArchivo, rutaArchivo, astArchivo, self)
    self.archivos.append(archivo)
    return archivo
  def limpiarRuta(self, pre=None):
    if pre is None:
      pre = 0
      while self.ruta.startswith("../"):
        self.ruta = self.ruta[3:]
        pre = pre + 3
    else:
      self.ruta = self.ruta[pre:]
    if pre > 0:
      for carpeta in self.carpetas:
        carpeta.limpiarRuta(pre)
      for archivo in self.archivos:
        archivo.limpiarRuta(pre)
  def todosLosArchivos(self):
    return fold(lambda rec, x : x.todosLosArchivos() + rec, self.archivos, self.carpetas)
  def cd(self, ruta):
    if len(ruta) == 0:
      return self
    proximaDiagonal = ruta.find('/')
    if proximaDiagonal < 0:
      return self.archivoDeNombre(ruta)
    else:
      return self.carpetaDeNombre(ruta[0:proximaDiagonal]).cd(ruta[proximaDiagonal+1:])
  def archivoDeNombre(self, nombre):
    for archivo in self.archivos:
      if archivo.nombre == nombre:
        return archivo
    falla()
  def carpetaDeNombre(self, nombre):
    for carpeta in self.carpetas:
      if carpeta.nombre == nombre:
        return carpeta
    falla()
  def MostrarArchivos(self, i):
    tab = ""
    for j in range(i):
      tab += "  "
    i += 1
    print(f"{tab}{self.nombre} ({self.ruta})")
    for carpeta in self.carpetas:
      carpeta.MostrarArchivos(i)
    for archivo in self.archivos:
      archivo.Mostrar(i)

class Datos(object):
  def __init__(self):
    self.raiz = None
    self.ruta = ""
  def listaDeCarpetas(self):
    return [self.raiz]
  def listaDeArchivos(self):
    return []
  def agregarCarpeta(self, nombreCarpeta, rutaCarpeta):
    self.raiz = Carpeta(nombreCarpeta, rutaCarpeta, self)
    return self.raiz
  def MostrarArchivos(self):
    self.raiz.MostrarArchivos(0)
  def limpiarRutas(self):
    self.raiz.limpiarRuta()
  def todosLosArchivos(self):
    return self.raiz.todosLosArchivos()
  def cd(self, ruta):
    self.raiz.cd(ruta)
  def resolverDependencias(self):
    todosLosArchivos = self.todosLosArchivos()
    for archivo in todosLosArchivos:
      archivo.exponerExportados()
    for archivo in todosLosArchivos:
      archivo.buscarDependencias()

def contenidoString(string):
  resultado = string
  if (resultado[0]=="'" and resultado[-1]=="'") or (resultado[0]=='"' and resultado[-1]=='"'):
    resultado = resultado[1:-1]
  else:
    falla()
  if resultado[-3:] == '.js':
    resultado = resultado[:-3]
  else:
    falla()
  return resultado

def falla():
  breakpoint()