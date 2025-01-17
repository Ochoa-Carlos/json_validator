from typing import Any

product_dict = {
    "ClaveProducto": str,
    "ClaveSubProducto": str,
    # "ReporteDeVolumenMensual": dict,
    "ComposOctanajeGasolina": int,
    "GasolinaConCombustibleNoFosil": int,
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
    "VolumenExistenciasMes": float,
    "FechaYHoraEstaMedicionMes": str
}

recepctions_dict = {
    "TotalRecepcionesMes": int,
    # "SumaVolumenRecepcionMes": dict,
    "TotalDocumentosMes": int,
    "PoderCalorifico": Any,
    "ImporteTotalRecepcionesMensual": float,
    "Complemento": list
}

deliveries_dict = {
    "TotalEntregasMes": int,
    # "SumaVolumenEntregadoMes": ,
    # "PoderCalorifico": ,
    "TotalDocumentosMes": int,
    "ImporteTotalEntregasMes": float,
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
