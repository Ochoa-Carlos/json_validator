import re

from constants import UTC_FORMAT_REGEX, cal_value_caracteres
from custom_exceptions import EntregasError, RecepcionesError, ValorMinMaxError
from decorators import exception_wrapper
from dict_type_validator import DictionaryTypeValidator
from dict_types import recepctions_dict, exists_control, deliveries_dict


# TODO hacer validaciones de tipo al inicio de la ejecucion de validacion y no por funcion
class MonthlyVolumeReportValidator:

    def __init__(self, monthly_volume_report: dict, product_key: str, caracter: str):
        self.monthly_report = monthly_volume_report
        self.product_key = product_key
        self.caracter = caracter
        self._errors = {}
        self._executed_functions = set()

    def validate_report(self) -> None:
        # self._validate_reporte_tipado()
        self._validate_control_existencias()
        self._validate_recepciones()
        self._validate_entregas()

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
            raise KeyError("Error: 'VolumenExistenciasMes' no fue encontrada.")
        if month_measure_date is None:
            raise KeyError("Error: 'FechaYHoraEstaMedicionMes' no fue encontrada.")
        if not -100000000000.0 <= month_volume <= 100000000000.0:
            raise ValorMinMaxError(
                "Error: 'VolumenExistenciasMes' no está en el rango min -100000000000.0 o max 100000000000.0."
            )
        if not re.match(UTC_FORMAT_REGEX, month_measure_date):
            raise TypeError(
                "Error: 'FechaYHoraEstaMedicionMes' no se expresa en UTC 'yyyy-mm-ddThh:mm:ss+-hh:mm'."
                )

    @exception_wrapper
    def _validate_recepciones(self) -> None:
        if (receptions := self.monthly_report.get("Recepciones")) is None:
            raise RecepcionesError("Error: 'Recepciones' no fue declarada.")

        DictionaryTypeValidator().validate_dict_type(dict_to_validate=receptions, dict_type=recepctions_dict)
        total_receptions_month = receptions.get("TotalRecepcionesMes")
        amount_volume_reception_month = receptions.get("SumaVolumenRecepcionMes")
        month_documents = receptions.get("TotalDocumentosMes")
        cal_value = receptions.get("PoderCalorifico")
        amount_receptions_month = receptions.get("ImporteTotalRecepcionesMensual")
        complement = receptions.get("Complemento")

        if total_receptions_month is None:
            raise RecepcionesError("Error: 'TotalRecepcionesMes' no fue declarada.")
        if amount_volume_reception_month is None:
            raise RecepcionesError("Error: 'SumaVolumenRecepcionMes' no fue declarada.")
        if month_documents is None:
            raise RecepcionesError("Error: 'TotalDocumentosMes' no fue declarada.")
        if amount_receptions_month is None:
            raise RecepcionesError("Error: 'ImporteTotalRecepcionesMensual' no fue declarada.")
        # TODO VERFICIAR SI COMPLEMENTO ES O NO REQUERIDA  SI SI ES 
        # if complement is None:
        #     raise RecepcionesError("Error: 'Complemento' no fue declarada.")

        if not 0 <= total_receptions_month <= 100000000:
            raise ValorMinMaxError(
                "Error: 'TotalRecepcionesMes' no está en el rango min 0 o max 100000000."
            )
        if self.product_key == "PR09" and self.caracter in cal_value_caracteres and cal_value is None:
            raise RecepcionesError(
                f"""Error: 'PoderCalorifico' es requerido para caracteres {cal_value_caracteres} y Producto 'PR09'."""
                )
        if month_documents > 1000000:
            raise ValorMinMaxError(
                "Error: 'TotalDocumentosMes' no está en el rango max 1000000."
            )
        if not 0 <= amount_receptions_month <= 100000000000.0:
            raise ValorMinMaxError(
                "Error: 'ImporteTotalRecepcionesMensual' no está en el rango min 0 o max 100000000000.0"
            )

    @exception_wrapper
    def _validate_entregas(self) -> None:
        if (deliveries := self.monthly_report.get("Entregas")) is None:
            raise EntregasError("Error: 'Entregas' no fue declarada")

        DictionaryTypeValidator().validate_dict_type(dict_to_validate=deliveries, dict_type=deliveries_dict)
        total_deliveries_month = deliveries.get("TotalEntregasMes")
        amount_volume_deliveries_month = deliveries.get("SumaVolumenEntregadoMes")
        month_documents = deliveries.get("TotalDocumentosMes")
        amount_deliveries_month = deliveries.get("ImporteTotalEntregasMes")
        complement = deliveries.get("Complemento")

        if total_deliveries_month is None:
            raise EntregasError("Error: 'TotalEntregasMes' no fue declarada.")
        if amount_volume_deliveries_month is None:
            raise EntregasError("Error: 'SumaVolumenEntregadoMes' no fue declarada.")
        if month_documents is None:
            raise EntregasError("Error: 'TotalDocumentosMes' no fue declarada.")
        if amount_deliveries_month is None:
            raise EntregasError("Error: 'ImporteTotalEntregasMes' no fue declarada.")
        # TODO VERFICIAR SI COMPLEMENTO ES O NO REQUERIDA  SI SI ES
        # if complement is None:
        #     raise EntregasError("Error: 'Complemento' no fue declarada.")

        if not 0 <= total_deliveries_month <= 10000000:
            raise ValorMinMaxError(
                "Error: 'TotalEntregasMes' no está en el rango min 0 o max 10000000."
                )
        if self.product_key == "PR09":
            if (deliveries.get("PoderCalorifico")) is None:
                raise EntregasError(
                    "Error: 'PoderCalorifico' es requerido para caracteres Producto 'PR09'."
                )
        if not 0 <= month_documents <= 100000000:
            raise ValorMinMaxError(
                "Error: 'TotalDocumentosMes' no está en el rango min 0 o max 100000000."
                )
        amount_deliveries_month = 1.222222
        if not 0 <= round(amount_deliveries_month, 3) <= 100000000000.0:
            raise ValorMinMaxError(
                "Error: 'ImporteTotalEntregasMes' no está en el rango min 0 o max 100000000000.0"
                )

    @property
    def errors(self) -> dict:
        """Get errors from montly volume report validation obj."""
        return self._errors

    @errors.setter
    def errors(self, errors: dict) -> None:
        """set errors in montly volume report validation obj."""
        self._errors[errors["func_error"]] = errors["error"]

    @property
    def exc_funcs(self) -> dict:
        """Get excecuted function in montly volume report validation class."""
        return self._executed_functions

    @exc_funcs.setter
    def exc_funcs(self, executed_function: str) -> None:
        """set excecuted function in montly volume report validation class."""
        self._executed_functions.add(executed_function)
