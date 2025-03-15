from typing import Any
from src.utils.definitions import CantidadMonetaria, ValorNumerico, PositiveNumber, PositiveNegativeNumber


product_dict = {
    "ClaveProducto": str,
    "ClaveSubProducto": str,
    # "ReporteDeVolumenMensual": dict,
    "ComposOctanajeGasolina": int,
    "GasolinaConCombustibleNoFosil": str,
    "ComposDeCombustibleNoFosilEnGasolina": int,
    "DieselConCombustibleNoFosil": str,
    "ComposDeCombustibleNoFosilEnDiesel": int,
    "TurbosinaConCombustibleNoFosil": str,
    "ComposDeCombustibleNoFosilEnTurbosina": int,
    "ComposDePropanoEnGasLP": float,
    "ComposDeButanoEnGasLP": float,
    "DensidadDePetroleo": float,
    "ComposDeAzufreEnPetroleo": float,
    "Otros": str,
    "MarcaComercial": str,
    "Marcaje": str,
    "ConcentracionSustanciaMarcaje": float,
    "GasNaturalOCondensados": list,
}

complement = {
    "TipoComplemento": str,
    # "Transporte": ,
    # "Dictamen": ,
    # "Certificado": ,
    "Nacional": list,
    "Extranjero": list,
    "Aclararcion": str
}

complement_transport = {
    "PermisoTransporte": str,
    "ClaveVehiculo": str,
    "TarifaDeTransporte": CantidadMonetaria,
    "CargoPorCapacidadTransporte": CantidadMonetaria,
    "CargoPorUsoTrans": CantidadMonetaria,
    "CargoVolumetricoTransporte": CantidadMonetaria,
}

complement_dictamen = {
    "RfcDictamen": str,
    "LoteDictamen": str,
    "NumeroFolioDictamen": str,
    "FechaEmisionDictamen": str,
    "ResultadoDictamen": str,
}

complement_certified = {
    "RfcCertificado": str,
    "NumeroFolioCertificado": str,
    "FechaEmisionCertificado": str,
    "ResultadoCertificado": str,
}

complement_national = {
    "RfcClienteOProveedor": str,
    "NombreClienteOProveedor": str,
    "PermisoProveedor": str,
    "CFDIs": list,
}

complement_cfdis = {
    "Cfdi": str,
    "TipoCfdi": str,
    "PrecioCompra": CantidadMonetaria,
    "Contraprestacion": CantidadMonetaria,
    "TarifaDeAlmacenamiento": CantidadMonetaria,
    "CargoPorCapacidadAlmac": CantidadMonetaria,
    "CargoPorUsoAlmac": CantidadMonetaria,
    "CargoVolumetricoAlmac": CantidadMonetaria,
    "Descuento": CantidadMonetaria,
    "FechaYHoraTransaccion": str,
    # "VolumenDocumentado": ,
}

complement_foreign = {
    "PermisoImportacion": str,
    "Pedimentos": list,
}

compl_foreign_pedimentos = {
    "PuntoDeInternacion": str,
    "PaisOrigen": str,
    "MedioDeTransEntraAduana": str,
    "PedimentoAduanal": str,
    "Incoterms": str,
    "PrecioDeImportacion": CantidadMonetaria,
    # "VolumenDocumentado": ,
}

compl_volumen = {
    "ValorNumerico": ValorNumerico,
    "UnidadDeMedida": str,
}

# month_report_dict = {
#     "ControlDeExistencias": {
#         "VolumenExistenciasMes": float,
#         "FechaYHoraEstaMedicionMes": str
#     },
#     "Recepciones": {
#         "TotalRecepcionesMes": int,
#         # "SumaVolumenRecepcionMes": dict,
#         "TotalDocumentosMes": int,
#         # "PoderCalorifico": Any,
#         "ImporteTotalRecepcionesMensual": float,
#         "Complemento": list
#     },
#     "Entregas": {
#         "TotalEntregasMes": int,
#         # "SumaVolumenEntregadoMes": ,
#         # "PoderCalorifico": ,
#         "TotalDocumentosMes": int,
#         "ImporteTotalEntregasMes": float,
#         "Complemento": list
#     }
# }

exists_control = {
    "VolumenExistenciasMes": PositiveNegativeNumber,
    "FechaYHoraEstaMedicionMes": str
}

recepctions_dict = {
    "TotalRecepcionesMes": int,
    # "SumaVolumenRecepcionMes": dict,
    "TotalDocumentosMes": int,
    "PoderCalorifico": dict,
    "ImporteTotalRecepcionesMensual": PositiveNumber,
    "Complemento": list
}

deliveries_dict = {
    "TotalEntregasMes": int,
    # "SumaVolumenEntregadoMes": ,
    # "PoderCalorifico": ,
    "TotalDocumentosMes": int,
    "ImporteTotalEntregasMes": PositiveNumber,
    "Complemento": list
}

gas_dict = {
    "ComposGasNaturalOCondensados": str,
    "FraccionMolar": float,
    "PoderCalorifico": float
}

log_dict = {
    "NumeroRegistro": int,
    "FechaYHoraEvento": str,
    "UsuarioResponsable": str,
    "TipoEvento": int,
    "DescripcionEvento": str,
    "IdentificacionComponenteAlarma": str
}
