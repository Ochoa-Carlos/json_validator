import re
from typing import TypeVar

from complements import ComplementBuilder, StorageComplement
from complements.helpers import complement_builder
from constants import UTC_FORMAT_REGEX, cal_value_caracteres
from custom_exceptions import EntregasError, RecepcionesError, ValorMinMaxError
from decorators import exception_wrapper
from dict_type_validator import DictionaryTypeValidator
from dict_types import deliveries_dict, exists_control, recepctions_dict

ComplementType = TypeVar("ComplementType", bound="ComplementBuilder")


# TODO hacer validaciones de tipo al inicio de la ejecucion de validacion y no por funcion
class MonthlyVolumeReportValidator:

    def __init__(self, monthly_volume_report: dict, product_key: str, caracter: str):
        self.monthly_report = monthly_volume_report
        self.product_key = product_key
        self.caracter = caracter
        self._errors = {}
        self._report_errors = []
        self._executed_functions = set()

# TODO hacer ufncion para validar el complemento de las entregas
    def validate_report(self) -> None:
        # self._validate_reporte_tipado()
        self._validate_control_existencias()
        self._validate_recepciones()
        self.__validate_recepciones_complemento()
        self._validate_entregas()
        self.__validate_entregas_complemento()

    # @exception_wrapper
    # def _validate_reporte_tipado(self) -> None:
    #     self._validate_control_existencias()
        # DictionaryTypeValidator().validate_dict_type(dict_to_validate=self.monthly_report, dict_type=month_report_dict)

    @exception_wrapper
    def _validate_control_existencias(self) -> None:
        if not (inv_control := self.monthly_report.get("ControlDeExistencias")):
            return

        DictionaryTypeValidator().validate_dict_type(dict_to_validate=inv_control, dict_type=exists_control)
        month_volume = inv_control.get("VolumenExistenciasMes")
        month_measure_date = inv_control.get("FechaYHoraEstaMedicionMes")

        if month_volume is None:
            self.catch_error(err_type=KeyError, err_message="Error: 'VolumenExistenciasMes' no fue encontrada.")
            # raise KeyError("Error: 'VolumenExistenciasMes' no fue encontrada.")
        if month_measure_date is None:
            self.catch_error(err_type=KeyError, err_message="Error: 'FechaYHoraEstaMedicionMes' no fue encontrada.")
            # raise KeyError("Error: 'FechaYHoraEstaMedicionMes' no fue encontrada.")
        if not -100000000000.0 <= month_volume <= 100000000000.0:
            self.catch_error(
                err_type=ValorMinMaxError,
                err_message="Error: 'VolumenExistenciasMes' no está en el rango min -100000000000.0 o max 100000000000.0.")
            # raise ValorMinMaxError(
            #     "Error: 'VolumenExistenciasMes' no está en el rango min -100000000000.0 o max 100000000000.0."
            # )
        if not re.match(UTC_FORMAT_REGEX, month_measure_date):
            self.catch_error(
                err_type=TypeError,
                err_message="Error: 'FechaYHoraEstaMedicionMes' no se expresa en UTC 'yyyy-mm-ddThh:mm:ss+-hh:mm'.")
            # raise TypeError(
            #     "Error: 'FechaYHoraEstaMedicionMes' no se expresa en UTC 'yyyy-mm-ddThh:mm:ss+-hh:mm'."
            #     )

    @exception_wrapper
    def _validate_recepciones(self) -> None:
        if (receptions := self.monthly_report.get("Recepciones")) is None:
            self.catch_error(err_type=RecepcionesError, err_message="Error: 'Recepciones' no fue declarada.")
            # raise RecepcionesError("Error: 'Recepciones' no fue declarada.")

        DictionaryTypeValidator().validate_dict_type(dict_to_validate=receptions, dict_type=recepctions_dict)
        total_receptions_month = receptions.get("TotalRecepcionesMes")
        amount_volume_reception_month = receptions.get("SumaVolumenRecepcionMes")
        month_documents = receptions.get("TotalDocumentosMes")
        cal_value = receptions.get("PoderCalorifico")
        amount_receptions_month = receptions.get("ImporteTotalRecepcionesMensual")
        complement = receptions.get("Complemento")

        if total_receptions_month is None:
            self.catch_error(err_type=RecepcionesError, err_message="Error: 'TotalRecepcionesMes' no fue declarada.")
            # raise RecepcionesError("Error: 'TotalRecepcionesMes' no fue declarada.")
        if amount_volume_reception_month is None:
            self.catch_error(err_type=RecepcionesError, err_message="Error: 'SumaVolumenRecepcionMes' no fue declarada.")
            # raise RecepcionesError("Error: 'SumaVolumenRecepcionMes' no fue declarada.")
        if month_documents is None:
            self.catch_error(err_type=RecepcionesError, err_message="Error: 'TotalDocumentosMes' no fue declarada.")
            # raise RecepcionesError("Error: 'TotalDocumentosMes' no fue declarada.")
        if amount_receptions_month is None:
            self.catch_error(err_type=RecepcionesError, err_message="Error: 'ImporteTotalRecepcionesMensual' no fue declarada.")
            # raise RecepcionesError("Error: 'ImporteTotalRecepcionesMensual' no fue declarada.")
        if complement is None:
            self.catch_error(err_type=RecepcionesError, err_message="Error: Valor 'Complemento' no fue declarada en clave 'Recepciones'.")
            # raise RecepcionesError("Error: Valor 'Complemento' no fue declarada en clave 'Recepciones'.")

        if not 0 <= total_receptions_month <= 100000000:
            self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'TotalRecepcionesMes' no está en el rango min 0 o max 100000000.")
            # raise ValorMinMaxError(
            #     "Error: 'TotalRecepcionesMes' no está en el rango min 0 o max 100000000."
            # )
        if self.product_key == "PR09" and self.caracter in cal_value_caracteres and cal_value is None:
            self.catch_error(err_type=RecepcionesError, err_message=f"""Error: 'PoderCalorifico' es requerido para caracteres {cal_value_caracteres} y Producto 'PR09'.""")
            # raise RecepcionesError(
            #     f"""Error: 'PoderCalorifico' es requerido para caracteres {cal_value_caracteres} y Producto 'PR09'."""
            #     )
        if month_documents > 1000000:
            self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'TotalDocumentosMes' no está en el rango max 1000000.")
            # raise ValorMinMaxError(
            #     "Error: 'TotalDocumentosMes' no está en el rango max 1000000."
            # )
        if not 0 <= amount_receptions_month <= 100000000000.0:
            self.catch_error(err_type=ValorMinMaxError, err_message="Error: 'ImporteTotalRecepcionesMensual' no está en el rango min 0 o max 100000000000.0")
            # raise ValorMinMaxError(
            #     "Error: 'ImporteTotalRecepcionesMensual' no está en el rango min 0 o max 100000000000.0"
            # )

    # @exception_wrapper
    def __validate_recepciones_complemento(self) -> None:
        receives = self.monthly_report.get("Recepciones")
        complement = receives.get("Complemento")
        comp_type = complement[0].get("TipoComplemento")
# TODO FALTA EL COMPLEMENTO TRANSPORTE
        if comp_type == "Transporte":
            return
        complement_obj = complement_builder(complement_data=complement, complement_type=comp_type)
        complement_obj.validate_complemento()

        if complement_errors := complement_obj.errors:
            self._report_errors.extend(complement_obj.get_error_list())
            self._errors = self._errors | complement_errors


    @exception_wrapper
    def _validate_entregas(self) -> None:
        if (deliveries := self.monthly_report.get("Entregas")) is None:
            self.catch_error(err_type=EntregasError, err_message="Error: 'Entregas' no fue declarada")
            # raise EntregasError("Error: 'Entregas' no fue declarada")

        total_deliveries_month = deliveries.get("TotalEntregasMes")
        amount_volume_deliveries_month = deliveries.get("SumaVolumenEntregadoMes")
        month_documents = deliveries.get("TotalDocumentosMes")
        amount_deliveries_month = deliveries.get("ImporteTotalEntregasMes")
        complement = deliveries.get("Complemento")

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=deliveries, dict_type=deliveries_dict):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)
        if total_deliveries_month is None:
            self.catch_error(err_type=EntregasError, err_message="Error: 'TotalEntregasMes' no fue declarada.")
            # raise EntregasError("Error: 'TotalEntregasMes' no fue declarada.")
        if amount_volume_deliveries_month is None:
            self.catch_error(err_type=EntregasError, err_message="Error: 'SumaVolumenEntregadoMes' no fue declarada.")
            # raise EntregasError("Error: 'SumaVolumenEntregadoMes' no fue declarada.")
        if month_documents is None:
            self.catch_error(err_type=EntregasError, err_message="Error: 'TotalDocumentosMes' no fue declarada.")
            # raise EntregasError("Error: 'TotalDocumentosMes' no fue declarada.")
        if amount_deliveries_month is None:
            self.catch_error(err_type=EntregasError, err_message="Error: 'ImporteTotalEntregasMes' no fue declarada.")
            # raise EntregasError("Error: 'ImporteTotalEntregasMes' no fue declarada.")
        if complement is None:
            self.catch_error(err_type=EntregasError, err_message="Error: Valor 'Complemento' no fue declarada en clave 'Entregas'.")
            # raise EntregasError("Error: Valor 'Complemento' no fue declarada en clave 'Entregas'.")

        if not 0 <= total_deliveries_month <= 10000000:
            self.catch_error(err_type=ValorMinMaxError,
                             err_message="Error: 'TotalEntregasMes' no está en el rango min 0 o max 10000000.")
            # raise ValorMinMaxError(
            #     "Error: 'TotalEntregasMes' no está en el rango min 0 o max 10000000."
            #     )
        if self.product_key == "PR09":
            if (deliveries.get("PoderCalorifico")) is None:
                self.catch_error(err_type=EntregasError,
                                 err_message="Error: 'PoderCalorifico' es requerido para caracteres Producto 'PR09'.")
                # raise EntregasError(
                #     "Error: 'PoderCalorifico' es requerido para caracteres Producto 'PR09'."
                # )
        if not 0 <= month_documents <= 100000000:
            self.catch_error(err_type=ValorMinMaxError,
                             err_message="Error: 'TotalDocumentosMes' no está en el rango min 0 o max 100000000.")
            # raise ValorMinMaxError(
            #     "Error: 'TotalDocumentosMes' no está en el rango min 0 o max 100000000."
            #     )
        amount_deliveries_month = 1.222222
        if not 0 <= round(amount_deliveries_month, 3) <= 100000000000.0:
            self.catch_error(err_type=ValorMinMaxError,
                             err_message="Error: 'ImporteTotalEntregasMes' no está en el rango min 0 o max 100000000000.0")
            # raise ValorMinMaxError(
            #     "Error: 'ImporteTotalEntregasMes' no está en el rango min 0 o max 100000000000.0"
            #     )

#         comp_type = complement[0].get("TipoComplemento")

# # TODO FALTA EL COMPLEMENTO TRANSPORTE
#         if comp_type == "Transporte":
#             return
#         complement_obj = complement_builder(complement_data=complement, complement_type=comp_type)
#         complement_obj.validate_complemento()

#         if complement_errors := complement_obj.errors:
#             err = complement_obj.get_error_list()
#             self._report_errors.extend(err)
#             self._errors = self._errors | complement_errors

    # @exception_wrapper
    def __validate_entregas_complemento(self) -> None:
        receives = self.monthly_report.get("Entregas")
        complement = receives.get("Complemento")
        comp_type = complement[0].get("TipoComplemento")
        # TODO FALTA EL COMPLEMENTO TRANSPORTE
        if comp_type == "Transporte":
            return
        complement_obj = complement_builder(complement_data=complement, complement_type=comp_type)
        complement_obj.validate_complemento()

        if complement_errors := complement_obj.errors:
            self._report_errors.extend(complement_obj.get_error_list())
            self._errors = self._errors | complement_errors

    def catch_error(self, err_type: str | Exception, err_message: str) -> dict:
        """Catch error from validations."""
        self.errors = {
            "type_error": err_type.__name__, 
            "error": err_message
            }

    @property
    def errors(self) -> dict:
        """Get errors from montly volume report validation obj."""
        return self._report_errors

    @errors.setter
    def errors(self, errors: dict) -> None:
        """set errors in montly volume report validation obj."""
        self._report_errors.append(errors)
        self._errors[errors["type_error"]] = errors["error"]

    @property
    def exc_funcs(self) -> dict:
        """Get excecuted function in montly volume report validation class."""
        return self._executed_functions

    @exc_funcs.setter
    def exc_funcs(self, executed_function: str) -> None:
        """set excecuted function in montly volume report validation class."""
        self._executed_functions.add(executed_function)
