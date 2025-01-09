class Archivo(object):
  def __init__(self, nombre, ruta, ast):
    self.nombre = nombre
    self.ruta = ruta
    self.ast = ast
  def limpiarRuta(self, pre):
    self.ruta = self.ruta[pre:]
  def contenido(self):
    return self.ast.toJs()
  def Mostrar(self, i, mostrarAST=False):
    tab = ""
    for j in range(i):
      tab += "  "
    print(f"{tab}{self.nombre} ({self.ruta})")
    if mostrarAST:
      print(self.ast)
      print("\n\n")

class Carpeta(object):
  def __init__(self, nombre, ruta):
    self.nombre = nombre
    self.ruta = ruta
    self.carpetas = []
    self.archivos = []
  def listaDeCarpetas(self):
    return self.carpetas
  def listaDeArchivos(self):
    return self.archivos
  def agregarCarpeta(self, nombreCarpeta, rutaCarpeta):
    nuevaCarpeta = Carpeta(nombreCarpeta, rutaCarpeta)
    self.carpetas.append(nuevaCarpeta)
    return nuevaCarpeta
  def agregarArchivo(self, nombreArchivo, rutaArchivo, astArchivo):
    archivo = Archivo(nombreArchivo, rutaArchivo, astArchivo)
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
  def listaDeCarpetas(self):
    return [self.raiz]
  def listaDeArchivos(self):
    return []
  def agregarCarpeta(self, nombreCarpeta, rutaCarpeta):
    self.raiz = Carpeta(nombreCarpeta, rutaCarpeta)
    return self.raiz
  def MostrarArchivos(self):
    self.raiz.MostrarArchivos(0)
  def limpiarRutas(self):
    self.raiz.limpiarRuta()
  def resolverDependencias(self):
    print("TODO")