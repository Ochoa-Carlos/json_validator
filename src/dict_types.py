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
    "Transporte": dict,
    "Trasvase": list,
    "Dictamen": dict,
    "Certificado": dict,
    "Nacional": list,
    "Extranjero": list,
    "Aclaracion": str,
}

complement_transport = {
    "PermisoTransporte": str,
    "ClaveDeVehiculo": str,
    "TarifaDeTransporte": CantidadMonetaria,
    "CargoPorCapacidadTrans": CantidadMonetaria,
    "CargoPorUsoTrans": CantidadMonetaria,
    "CargoVolumetricoTrans": CantidadMonetaria,
}

complement_trasvase = {
    "NombreTrasvase": str,
    "RfcTrasvase": str,
    "PermisoTrasvase": str,
    "DescripcionTrasvase": str,
    "CfdiTrasvase": str,
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
    "VolumenDocumentado": dict,
}

com_complement = {
    "TipoComplemento": str,
    "TerminalAlmYDist": dict,
    "Trasvase": list,
    "Dictamen": dict,
    "Certificado": dict,
    "Nacional": list,
    "Extranjero": list,
    "Aclaracion": str,
}

com_terminal_alm_dist = {
    "Almacenamiento": dict,
    "Transporte": dict,
}

national_client_or_supplier = {
    "RfcClienteOProveedor": str,
    "NombreClienteOProveedor": str,
    "PermisoClienteOProveedor": str,
    "CFDIs": list,
}

cfdis_sale_purchase = {
    "Cfdi": str,
    "TipoCfdi": str,
    "PrecioVentaOCompraOContrap": CantidadMonetaria,
    "VolumenDocumentado": dict,
    "FechaYHoraTransaccion": str,
}

foreign_import_export = {
    "PermisoImportacionOExportacion": str,
    "Pedimentos": list,
}

pedimentos_import_export = {
    "PuntoDeInternacionOExtraccion": str,
    "PaisOrigenODestino": str,
    "MedioDeTransEntraOSaleAduana": str,
    "PedimentoAduanal": str,
    "Incoterms": str,
    "PrecioDeImportacionOExportacion": CantidadMonetaria,
    "VolumenDocumentado": dict,
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
    "VolumenDocumentado": dict,
}

compl_volumen = {
    "ValorNumerico": ValorNumerico,
    "UnidadDeMedida": str,
}

terminal_alm = {
    "TerminalAlmYDist": str,
    "PermisoAlmYDist": str,
    "TarifaDeAlmacenamiento": CantidadMonetaria,
    "CargoPorCapacidadAlmac": CantidadMonetaria,
    "CargoPorUsoAlmac": CantidadMonetaria,
    "CargoVolumetricoAlmac": CantidadMonetaria,
}

transp_complement = {
    "TipoComplemento": str,
    "TerminalAlmYDist": dict,
    "Trasvase": list,
    "Dictamen": dict,
    "Certificado": dict,
    "Nacional": list,
    "Aclaracion": str,
}

# En Transporte el objeto TerminalAlmYDist es plano: no anida Almacenamiento ni Transporte.
transp_terminal_alm_dist = {
    "TerminalAlmYDist": str,
    "PermisoAlmYDist": str,
}

transp_cfdis = {
    "Cfdi": str,
    "TipoCfdi": str,
    "Contraprestacion": CantidadMonetaria,
    "TarifaDeTransporte": CantidadMonetaria,
    "CargoPorCapacidadDeTrans": CantidadMonetaria,
    "CargoPorUsoTrans": CantidadMonetaria,
    "CargoVolumetricoTrans": CantidadMonetaria,
    "Descuento": CantidadMonetaria,
    "FechaYHoraTransaccion": str,
    "VolumenDocumentado": dict,
}

exo_complement = {
    "TipoComplemento": str,
    "TerminalAlmYDist": dict,
    "Trasvase": list,
    "Dictamen": dict,
    "Certificado": dict,
    "Nacional": list,
    "Extranjero": list,
    "Aclaracion": str,
}

exo_terminal_alm_dist = {
    "Almacenamiento": dict,
    "Transporte": dict,
}

exo_storage = {
    "TerminalAlmYDist": str,
    "PermisoAlmYDist": str,
    "TarifaDeAlmac": CantidadMonetaria,
    "CargoPorCapacidadAlmac": CantidadMonetaria,
    "CargoPorUsoAlmac": CantidadMonetaria,
    "CargoVolumetricoAlmac": CantidadMonetaria,
}

exo_cfdis = {
    "Cfdi": str,
    "TipoCfdi": str,
    "PrecioCompra": CantidadMonetaria,
    "PrecioDeVentaAlPublico": CantidadMonetaria,
    "PrecioVenta": CantidadMonetaria,
    "FechaYHoraTransaccion": str,
    "VolumenDocumentado": dict,
}

dis_complement = {
    "TipoComplemento": str,
    "TerminalAlmYTrans": dict,
    "Trasvase": list,
    "Dictamen": dict,
    "Certificado": dict,
    "Nacional": list,
    "Extranjero": list,
    "Aclaracion": str,
}

dis_terminal_alm_trans = {
    "Almacenamiento": dict,
    "Transporte": dict,
}

dis_storage = {
    "TerminalAlm": str,
    "PermisoAlmacenamiento": str,
    "TarifaDeAlmacenamiento": CantidadMonetaria,
    "CargoPorCapacidadAlmac": CantidadMonetaria,
    "CargoPorUsoAlmac": CantidadMonetaria,
    "CargoVolumetricoAlmac": CantidadMonetaria,
}

dis_transport = {
    "PermisoTransporte": str,
    "ClaveDeVehiculo": str,
    "TarifaDeTransporte": CantidadMonetaria,
    "CargoPorCapacidadTrans": CantidadMonetaria,
    "CargoPorUsoTrans": CantidadMonetaria,
    "CargoVolumetricoTrans": CantidadMonetaria,
    "TarifaDeSuministro": CantidadMonetaria,
}

cdlrgn_complement = {
    "TipoComplemento": str,
    "TerminalAlmYTrans": dict,
    "Trasvase": list,
    "Dictamen": dict,
    "Certificado": dict,
    "Nacional": list,
    "Extranjero": list,
    "Aclaracion": str,
}

cdlrgn_terminal_alm_trans = {
    "Almacenamiento": dict,
    "Transporte": dict,
}

cdlrgn_storage = {
    "TerminalAlm": str,
    "PermisoAlmacenamiento": str,
}

cdlrgn_transport = {
    "PermisoTransporte": str,
    "ClaveDeVehiculo": str,
}

national_client = {
    "RfcCliente": str,
    "NombreCliente": str,
    "CFDIs": list,
}

cdlrgn_cfdis = {
    "Cfdi": str,
    "TipoCfdi": str,
    "Contraprestacion": CantidadMonetaria,
    "FechaYHoraTransaccion": str,
    "VolumenDocumentado": dict,
}

cdlrgn_foreign = {
    "PermisoImportacionOExportacion": str,
    "Pedimentos": list,
}

cdlrgn_foreign_pedimentos = {
    "PuntoDeInternacionOExtraccion": str,
    "PaisOrigenODestino": str,
    "MedioDeTransEntraOSaleAduana": str,
    "PedimentoAduanal": str,
    "Incoterms": str,
    "PrecioDeImportacion": CantidadMonetaria,
    "VolumenDocumentado": dict,
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
