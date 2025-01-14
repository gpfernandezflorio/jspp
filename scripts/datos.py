import sys, os
from bibpy.listas import fold, mapear, filtrar
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
    self.modulo = nombreModulo(self)
    self.definiciones = DefinicionesModulo(self)
    self.importados = []
    # self.exportados = []
    self.milaAst = None
  def limpiarRuta(self, pre):
    self.ruta = self.ruta[pre:]
  def contenido(self):
    return self.milaAst.restore()
  def Mostrar(self, i=0, mostrarAST=False):
    tab = ""
    for j in range(i):
      tab += "  "
    print(f"{tab}{self.nombre} ({self.nombreModulo()})")
    print(f"{tab}  {list(map(lambda x : x.ls(), self.importados))}")
    # for exportado in self.exportados:
    #   print(f"{tab}  {exportado}")
    if mostrarAST:
      print(self.ast)
      print("\n\n")
  def nombreModulo(self):
    return self.carpetaContenedora.nombreModulo() + self.modulo
  def nombresLocales(self):
    return self.definiciones.todosLosNombres()
  def exponerExportados(self):
    # for declaracion in self.ast.declaraciones:
    #   if type(declaracion) is AST_export:
    #     self.exportados.append(declaracion.exportable)
    for definicion in BuscarDefiniciones(self.ast.declaraciones):
      self.definiciones.definir(definicion)
  def buscarDependencias(self):
    for declaracion in self.ast.declaraciones:
      if type(declaracion) is AST_import:
        self.importados.append(Referencia(declaracion, self))
  def esNombreLocal(self, nombre):
    return self.definiciones.contiene(nombre)

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

class DefinicionesModulo(object):
  def __init__(self, archivoFuente):
    self.modulo = archivoFuente.nombreModulo()
    self.nombres = {}
  def definir(self, declaracion):
    if type(declaracion) is AST_declaracion_variable:
      nombre = nombreNodo(declaracion)
      self.nombres[nombre] = self.modulo + '.' + nombre
    elif type(declaracion) is AST_declaracion_funcion:
      nombre = nombreNodo(declaracion)
      self.nombres[nombre] = self.modulo + '.' + nombre
    elif type(declaracion) is AST_declaracion_clase:
      nombre = nombreNodo(declaracion)
      self.nombres[nombre] = self.modulo + '.' + nombre
  def todosLosNombres(self):
    return list(self.nombres.keys())
  def contiene(self, nombre):
    return nombre in self.nombres

class Carpeta(object):
  def __init__(self, nombre, ruta, carpetaContenedora):
    self.nombre = nombre
    self.ruta = ruta
    self.carpetas = []
    self.archivos = []
    self.modulo = nombreModulo(self)
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
  def nombreModulo(self):
    return self.carpetaContenedora.nombreModulo() + self.modulo + '.'
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
    self.procesando = None
  def listaDeCarpetas(self):
    return [self.raiz]
  def listaDeArchivos(self):
    return []
  def agregarCarpeta(self, nombreCarpeta, rutaCarpeta):
    self.raiz = Carpeta(nombreCarpeta, rutaCarpeta, self)
    return self.raiz
  def nombreModulo(self):
    return ''
  def MostrarArchivos(self):
    self.raiz.MostrarArchivos(0)
  def limpiarRutas(self):
    self.raiz.limpiarRuta()
  def todosLosArchivos(self):
    return self.raiz.todosLosArchivos()
  def cd(self, ruta):
    self.raiz.cd(ruta)
  def ts2js(self):
    todosLosArchivos = self.todosLosArchivos()
    for archivo in todosLosArchivos:
      archivo.exponerExportados()
    for archivo in todosLosArchivos:
      archivo.buscarDependencias()
    for archivo in todosLosArchivos:
      self.procesando = Procesamiento(archivo)
      archivo.milaAst = limpiarAst(archivo.ast, self)
  def limpiarNombre(self, nombreOriginal):
    entorno = self.procesando.entornoPara(nombreOriginal)
    if entorno is None:
      return nombreOriginal
    if entorno.esArchivo():
      if self.procesando.archivoActual.esNombreLocal(nombreOriginal):
        return self.procesando.archivoActual.nombreModulo() + '.' + nombreOriginal
      else:
        falla()
    else:
      return nombreOriginal
  def enEntornoArchivo(self):
    return self.procesando.entornoActual().id == "ARCHIVO"
  def entrar(self, nodo):
    self.procesando.entrar(nodo)
  def salir(self):
    self.procesando.salir()

class Procesamiento(object):
  def __init__(self, archivo):
    self.archivoActual = archivo
    self.entornos = [EntornoArchivo(archivo)]
  def entornoActual(self):
    return self.entornos[0]
  def entrar(self, nodo):
    entorno = None
    if type(nodo) is AST_declaracion_funcion:
      entorno = EntornoFuncion(nodo)
    elif type(nodo) is AST_expresion_funcion:
      entorno = EntornoFuncion(nodo)
    elif type(nodo) is AST_declaracion_clase:
      entorno = EntornoClase(nodo)
    else:
      falla()
    self.entornos.insert(0, entorno)
  def salir(self):
    del self.entornos[0]
  def entornoPara(self, nombre):
    for entorno in self.entornos:
      if entorno.estaDefinido(nombre):
        return entorno
    return None

class Entorno(object):
  def __init__(self):
    self.definiciones = []
  def esArchivo(self):
    return False
  def esClase(self):
    return False
  def esFuncion(self):
    return False
  def esFuncion(self):
    return False
  def estaDefinido(self, nombre):
    return nombre in self.definiciones

class EntornoArchivo(Entorno):
  def __init__(self, archivo):
    self.id = "ARCHIVO"
    self.definiciones = archivo.nombresLocales()
  def esArchivo(self):
    return True

class EntornoClase(Entorno):
  def __init__(self, nodo_declaracion):
    self.id = "CLASE"
    self.definiciones = mapear(nombreNodo, BuscarDefiniciones(nodo_declaracion.definicion.contenido))
  def esClase(self):
    return True

class EntornoFuncion(Entorno):
  def __init__(self, nodo_declaracion):
    self.id = "FUNCION"
    self.definiciones = mapear(lambda x : x.identificador,
      filtrar(lambda x : type(x) is AST_identificador, nodo_declaracion.parametros.parametros))
  def esFuncion(self):
    return True

def BuscarDefiniciones(nodo_o_lista):
  resultado = []
  if type(nodo_o_lista) == type([]):
    resultado = fold(lambda rec, x : rec + BuscarDefiniciones(x), [], nodo_o_lista)
  elif type(nodo_o_lista) is AST_export:
    resultado = BuscarDefiniciones(nodo_o_lista.exportable)
  elif type(nodo_o_lista) is AST_declaracion_variable:
    resultado = [nodo_o_lista]
  elif type(nodo_o_lista) is AST_declaracion_funcion:
    resultado = [nodo_o_lista]
  elif type(nodo_o_lista) is AST_declaracion_clase:
    resultado = [nodo_o_lista]
  return resultado

def nombreNodo(nodo):
  if type(nodo) is AST_declaracion_variable:
    return nodo.nombre.identificador
  elif type(nodo) is AST_declaracion_funcion:
    return nodo.nombre.identificador
  elif type(nodo) is AST_declaracion_clase:
    return nombreNodo(nodo.nombre)
  elif type(nodo) is AST_tipo_base:
    return nodo.base.identificador
  elif type(nodo) is AST_tipo_compuesto:
    return nombreNodo(nodo.base)
  falla()

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

def nombreModulo(elemento):
  # if isinstance(elemento, Archivo):
  #   # Si encuentro un alias en elemento.ast uso ese. Si no:
  palabras = elemento.nombre.split("_")
  nombre = palabras[0]
  for palabra in palabras[1:]:
    if len(palabra) > 0:
      nombre += palabra[0].upper() + palabra[1:]
  return nombre[0].upper() + nombre[1:]

def limpiarAst(nodo, datos):
  if nodo is None:
    return None
  tipo = type(nodo)
  if tipo == type([]):
    return mapear(lambda x : limpiarAst(x, datos), nodo)
  if tipo == AST_programa:
    nuevasDeclaraciones = limpiarAst(nodo.declaraciones, datos)
    nuevoNodo = AST_programa(nuevasDeclaraciones)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_comentario:
    nuevoNodo = AST_comentario(nodo.contenido)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_espacios:
    nuevoNodo = AST_espacios(nodo.espacios)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_salto:
    nuevoNodo = AST_salto(nodo.espacios)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_sintaxis:
    nuevoNodo = AST_sintaxis(nodo.contenido)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_declaracion_funcion:
    nuevoNombre = limpiarAst(nodo.nombre, datos)
    datos.entrar(nodo)
    nuevosParametros = limpiarAst(nodo.parametros, datos)
    nuevoCuerpo = limpiarAst(nodo.cuerpo, datos)
    datos.salir()
    if datos.enEntornoArchivo():
      nuevoNombre.clausura(' = function')
    funcion_incompleta = AST_funcion_incompleta(nuevosParametros, nuevoCuerpo)
    nuevoNodo = AST_declaracion_funcion(nuevoNombre, funcion_incompleta)
    if datos.enEntornoArchivo():
      nuevoNodo.apertura('*/')
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    if datos.enEntornoArchivo():
      nuevoNodo.apertura('/*')
    return nuevoNodo
  if tipo == AST_declaracion_clase:
    nuevoNombre = limpiarAst(nodo.nombre, datos)
    datos.entrar(nodo)
    nuevaDefinicion = limpiarAst(nodo.definicion, datos)
    datos.salir()
    if datos.enEntornoArchivo():
      nuevoNombre.clausura('= class ')
    nuevoNodo = AST_declaracion_clase(nuevoNombre, nuevaDefinicion)
    if datos.enEntornoArchivo():
      nuevoNodo.apertura('*/')
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    if datos.enEntornoArchivo():
      nuevoNodo.apertura('/*')
    return nuevoNodo
  if tipo == AST_declaracion_tipo:
    nuevoNombre = limpiarAst(nodo.nombre, datos)
    nuevaDefinicion = limpiarAst(nodo.definicion, datos)
    nuevoNodo = AST_declaracion_tipo(nuevoNombre, nuevaDefinicion)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    nuevoNodo.apertura('/*')
    nuevoNodo.clausura('*/')
    return nuevoNodo
  if tipo == AST_declaracion_variable:
    nuevoNombre = limpiarAst(nodo.nombre, datos)
    nuevaAsignacion = limpiarAst(nodo.asignacion, datos)
    if datos.enEntornoArchivo():
      nuevoNombre.identificador = datos.limpiarNombre(nuevoNombre.identificador)
      nuevoNodo = AST_asignacion(nuevoNombre, nuevaAsignacion)
      if len(nodo.otros) > 0:
        falla()
      nuevoNodo.apertura('*/')
      imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
      nuevoNodo.apertura('/*')
    else:
      nuevoNodo = AST_declaracion_variable(nuevoNombre, nuevaAsignacion)
      nuevosOtros = limpiarAst(nodo.otros, datos)
      for o in nuevosOtros:
        nuevoNodo.identificador_adicional(o)
      imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_cuerpo:
    nuevoContenido = limpiarAst(nodo.contenido, datos)
    nuevoNodo = AST_cuerpo(nuevoContenido)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_expresion_literal:
    nuevoNodo = AST_expresion_literal(nodo.literal)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_format_string:
    nuevoNodo = AST_format_string(nodo.tmp) # TODO: corregir tras parsear el contenido
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_expresion_objeto:
    nuevosCampos = limpiarAst(nodo.campos, datos)
    nuevoNodo = AST_expresion_objeto(nuevosCampos)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_expresion_lista:
    nuevosElementos = limpiarAst(nodo.elementos, datos)
    nuevoNodo = AST_expresion_lista(nuevosElementos)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_expresion_identificador:
    nuevosIdentificador = limpiarAst(nodo.identificador, datos)
    nuevoNodo = AST_expresion_identificador(nuevosIdentificador)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_expresion_funcion:
    datos.entrar(nodo)
    nuevosParametros = limpiarAst(nodo.parametros, datos)
    nuevoCuerpo = limpiarAst(nodo.cuerpo, datos)
    datos.salir()
    funcion_incompleta = AST_funcion_incompleta(nuevosParametros, nuevoCuerpo)
    nuevoNodo = AST_expresion_funcion(funcion_incompleta)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_expresion_acceso:
    nuevoObjeto = limpiarAst(nodo.objeto, datos)
    nuevoCampo = limpiarAst(nodo.campo, datos)
    nuevoModificador = AST_modificador_objeto_acceso(nuevoCampo)
    nuevoNodo = AST_expresion_acceso(nuevoObjeto, nuevoModificador)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_expresion_index:
    nuevoObjeto = limpiarAst(nodo.objeto, datos)
    nuevoIndice = limpiarAst(nodo.indice, datos)
    nuevoModificador = AST_modificador_objeto_index(nuevoIndice)
    nuevoNodo = AST_expresion_index(nuevoObjeto, nuevoModificador)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_operador:
    nuevoIzq = limpiarAst(nodo.izq, datos)
    nuevoDer = limpiarAst(nodo.der, datos)
    nuevoOtro = limpiarAst(nodo.other, datos)
    nuevoNodo = AST_operador(nuevoIzq, nodo.op, nuevoDer, nuevoOtro)
    if nodo.tieneParentesis():
      nuevoNodo.conParentesis()
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_expresion_new:
    nuevoTipo = limpiarAst(nodo.tipo, datos)
    nuevoNodo = AST_expresion_new(nuevoTipo)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_invocacion:
    nuevaFuncion = limpiarAst(nodo.funcion, datos)
    nuevosArgumentos = limpiarAst(nodo.argumentos, datos)
    nuevoNodo = AST_invocacion(nuevaFuncion, nuevosArgumentos)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_iteracion:
    nuevaVariable = limpiarAst(nodo.variable, datos)
    nuevoRango = limpiarAst(nodo.rango, datos)
    nuevoNodo = AST_iteracion(nuevaVariable, nuevoRango)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_asignacion:
    nuevoAsignable = limpiarAst(nodo.asignable, datos)
    nuevoValor = limpiarAst(nodo.valor, datos)
    nuevoNodo = AST_asignacion(nuevoAsignable, nuevoValor)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_combinador:
    clase = nodo.clase
    nuevaExpresion = limpiarAst(nodo.expresion, datos)
    nuevoNodo = AST_combinador(clase, nuevaExpresion)
    nuevoCuerpo = limpiarAst(nodo.cuerpo, datos)
    nuevoNodo.agregar_cuerpo(nuevoCuerpo)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_return:
    nuevaExpresion = limpiarAst(nodo.expresion, datos)
    nuevoNodo = AST_return(nuevaExpresion)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_parametros:
    nuevosParametros = limpiarAst(nodo.parametros, datos)
    nuevosDecoradores = limpiarAst(nodo.decoradoresFuncion, datos)
    nuevoNodo = AST_parametros(nuevosParametros, nuevosDecoradores)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_argumentos:
    nuevaLista = limpiarAst(nodo.lista, datos)
    nuevoNodo = AST_argumentos()
    nuevoNodo.lista = nuevaLista
    nuevoNodo.tmp = nodo.tmp
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_campos:
    nuevaLista = limpiarAst(nodo.lista, datos)
    nuevoNodo = AST_campos()
    nuevoNodo.lista = nuevaLista
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_campo:
    nuevaClave = limpiarAst(nodo.clave, datos)
    nuevoValor = limpiarAst(nodo.valor, datos)
    nuevoNodo = AST_campo(nuevaClave, nuevoValor)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_elementos:
    nuevaLista = limpiarAst(nodo.lista, datos)
    nuevoNodo = AST_elementos()
    nuevoNodo.lista = nuevaLista
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_identificador:
    nuevoNombre = datos.limpiarNombre(nodo.identificador)
    nuevoNodo = AST_identificador(nuevoNombre)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_identificadores:
    nuevaLista = limpiarAst(nodo.identificadores, datos)
    nuevoNodo = AST_identificadores(nuevaLista)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_indexacion_clase:
    nuevoIdentificador = limpiarAst(nodo.identificador, datos)
    nuevoNodo = AST_indexacion_clase(nuevoIdentificador)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_identificador_objeto:
    nuevosCampos = limpiarAst(nodo.campos, datos)
    nuevoNodo = AST_identificador_objeto(nuevosCampos)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_import:
    nuevoArchivo = limpiarAst(nodo.archivo, datos)
    nuevosImportables = limpiarAst(nodo.importables, datos)
    nuevoAlias = limpiarAst(nodo.opt_alias, datos)
    nuevoNodo = AST_import(nuevoArchivo, nuevosImportables, nuevoAlias, nodo.es_tipo)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_export:
    nuevaDeclaracion = limpiarAst(nodo.exportable, datos)
    nuevaDeclaracion.apertura('\n')
    nuevoNodo = AST_export(nuevaDeclaracion)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    nuevoNodo.apertura('// ')
    return nuevoNodo
  if tipo == AST_decorador_tipo:
    nuevoTipo = AST_tipo_base(nodo.tipo.restore()) # limpiarAst(nodo.tipo, datos)
    nuevoNodo = AST_decorador_tipo(nuevoTipo)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    comentar(nuevoNodo)
    return nuevoNodo
  if tipo == AST_decorador_subtipo:
    nuevoTipo = limpiarAst(nodo.tipo, datos)
    nuevoNodo = AST_decorador_subtipo(nuevoTipo)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_decorador_opcional:
    nuevoNodo = AST_decorador_opcional()
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    comentar(nuevoNodo)
    return nuevoNodo
  if tipo == AST_decorador_default:
    nuevaAsignacion = limpiarAst(nodo.default, datos)
    nuevoNodo = AST_decorador_default(nuevaAsignacion)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_decorador_alias:
    nuevoAlias = limpiarAst(nodo.alias, datos)
    nuevoNodo = AST_decorador_alias(nuevoAlias)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    comentar(nuevoNodo)
    return nuevoNodo
  if tipo == AST_decorador_comotipo:
    nuevoTipo = limpiarAst(nodo.tipo, datos)
    nuevoNodo = AST_decorador_comotipo(nuevoTipo)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    comentar(nuevoNodo)
    return nuevoNodo
  if tipo == AST_decorador_keyword:
    nuevoIdentificador = limpiarAst(nodo.identificador, datos)
    nuevoNodo = AST_decorador_keyword(nuevoIdentificador)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    comentar(nuevoNodo)
    return nuevoNodo
  if tipo == AST_decorador_implementacion:
    nuevoNombre = limpiarAst(nodo.nombre, datos)
    nuevoNodo = AST_decorador_implementacion(nuevoNombre)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    comentar(nuevoNodo)
    return nuevoNodo
  if tipo == AST_decorador_extension:
    nuevoNombre = limpiarAst(nodo.nombre, datos)
    nuevoNodo = AST_decorador_extension(nuevoNombre)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    comentar(nuevoNodo)
    return nuevoNodo
  if tipo == AST_tipo_base:
    nuevaBase = limpiarAst(nodo.base, datos)
    nuevoNodo = AST_tipo_base(nuevaBase)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_tipo_lista:
    nuevoNodo = AST_tipo_lista()
    nuevoTipo = limpiarAst(nodo.rec, datos)
    nuevoNodo.set_rec(nuevoTipo)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_tipo_objeto:
    nuevosCampos = limpiarAst(nodo.campos, datos)
    nuevoNodo = AST_tipo_objeto(nuevosCampos)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_tipo_flecha:
    nuevosParametros = limpiarAst(nodo.parametros, datos)
    nuevoResultado = limpiarAst(nodo.tipo_salida, datos)
    nuevoNodo = AST_tipo_flecha(nuevosParametros, nuevoResultado)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_tipo_suma:
    nuevosTipos = limpiarAst(nodo.sub_tipos, datos)
    nuevoNodo = AST_tipo_suma(nuevosTipos)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_tipo_producto:
    nuevosTipos = limpiarAst(nodo.sub_tipos, datos)
    nuevoNodo = AST_tipo_producto(nuevosTipos)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_tipo_tupla:
    nuevosTipos = limpiarAst(nodo.sub_tipos, datos)
    nuevoNodo = AST_tipo_tupla(nuevosTipos)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_tipo_compuesto:
    nuevaBase = limpiarAst(nodo.base, datos)
    nuevosTipos = limpiarAst(nodo.sub_tipos, datos)
    nuevoNodo = AST_tipo_compuesto(nuevaBase, nuevosTipos)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_tipo_varios:
    nuevosTipos = limpiarAst(nodo.sub_tipos, datos)
    nuevoNodo = AST_tipo_varios(nuevosTipos)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_tipo_derivado:
    nuevaExpresion = limpiarAst(nodo.expresion, datos)
    nuevoNodo = AST_tipo_derivado(nuevaExpresion)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_tipo_void:
    nuevoNodo = AST_tipo_void()
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_campos_tipo:
    nuevoNodo = AST_campos_tipo()
    nuevaLista = limpiarAst(nodo.lista, datos)
    nuevoNodo.lista = nuevaLista
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  if tipo == AST_campo_tipo:
    nuevaClave = limpiarAst(nodo.clave, datos)
    nuevoTipo = limpiarAst(nodo.tipo, datos)
    nuevoNodo = AST_campo_tipo(nuevaClave, nuevoTipo)
    imitarEspaciosYDecoradores(nuevoNodo, nodo, datos)
    return nuevoNodo
  falla()

def imitarEspaciosYDecoradores(nodo, otro, datos):
  nuevosDecoradores = limpiarAst(otro.decoradores, datos)
  for d in nuevosDecoradores:
    nodo.agregar_decorador(d)
  nuevosDecoradoresPre = limpiarAst(otro.decoradores_pre, datos)
  for d in nuevosDecoradoresPre:
    nodo.agregar_decorador_pre(d)
  nuevosEspaciosAbre = limpiarAst(otro.abre, datos)
  nodo.apertura(nuevosEspaciosAbre)
  nuevosEspaciosCierra = limpiarAst(otro.cierra, datos)
  nodo.clausura(nuevosEspaciosCierra)

def comentar(nodo):
  nodo.apertura("/*")
  nodo.clausura("*/")

def falla():
  breakpoint()