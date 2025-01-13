let _cantidad : number = 0;

const _tamanio_maximo : number = 10;

type Estado = {
  cantAcciones : number
};

type Vacio = boolean;

export type maybeEstado = Estado | Vacio;

export const estadoActual : Estado = {
  cantAcciones: 0
};

export function sumar(cantidad_a_sumar: number) : void {
  let nueva_cantidad : number = _cantidad + cantidad_a_sumar > _tamanio_maximo
    ? _tamanio_maximo
    : _cantidad + cantidad_a_sumar
  ;
  _cantidad = nueva_cantidad;
  Avanzar(estadoActual);
};

const Avanzar = function(estadoActual : Estado) {
  estadoActual.cantAcciones ++;
};

function restarSi(condicion : (x: number) => boolean) : boolean {
  if (condicion(_cantidad)) {
    return true;
  }
  return false;
};

export class Control {
  constructor(private readonly nombre: string) {}

  controlar(Avanzar : ()=>void): string {
    Avanzar();
    restarSi((x)=>x>5);
    return this.nombre;
  }

  descontrolar() {
    Avanzar(this.sumar());
  }

  sumar() {
    return estadoActual;
  }

  static CURSOR = 5;
};