from enum import Enum


class ComplementType(Enum):
    ALMACENAMIENTO = "Almacenamiento"
    CDLR = "CDLR"
    COMERCIALIZACION = "Comercializacion"
    DISTRIBUCION = "Distribucion"
    EXPENDIO = "Expendio"
    EXTRACCION = "Extraccion"
    REFINACION = "Refinacion"
    TRANSPORTE = "Transporte"


class CfdiType(Enum):
    INGRESO = "Ingreso"
    EGRESO = "Egreso"
    TRASLADO = "Traslado"
    