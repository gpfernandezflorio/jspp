class Archivo(object):
  def __init__(self, nombre, ruta):
    self.nombre = nombre
    self.ruta = ruta
  def Mostrar(self, i):
    tab = ""
    for j in range(i):
      tab += "  "
    print(f"{tab}{self.nombre} ({self.ruta})")

class Carpeta(object):
  def __init__(self, nombre, ruta):
    self.nombre = nombre
    self.ruta = ruta
    self.carpetas = []
    self.archivos = []
  def agregarCarpeta(self, nombreCarpeta, rutaCarpeta):
    nuevaCarpeta = Carpeta(nombreCarpeta, rutaCarpeta)
    self.carpetas.append(nuevaCarpeta)
    return nuevaCarpeta
  def agregarArchivo(self, nombreArchivo, rutaArchivo):
    self.archivos.append(Archivo(nombreArchivo, rutaArchivo))
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
  def agregarCarpeta(self, nombreCarpeta, rutaCarpeta):
    self.raiz = Carpeta(nombreCarpeta, rutaCarpeta)
    return self.raiz
  def MostrarArchivos(self):
    self.raiz.MostrarArchivos(0)