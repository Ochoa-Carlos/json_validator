"""This module handles ReporteDeVolumenMensual validations."""
import re
from typing import Optional, TypeVar, Union

from src.complements import ComplementBuilder
from src.complements.enumerators import ComplementTypeEnum
from src.complements.helpers import complement_builder
from src.constants import UTC_FORMAT_REGEX, cal_value_caracteres
from src.custom_exceptions import (ClaveError, EntregasError, LongitudError,
                                   RecepcionesError, RegexError, TipadoError,
                                   ValorError, ValorMinMaxError)
from src.decorators import exception_wrapper
from src.dict_type_validator import DictionaryTypeValidator
from src.dict_types import deliveries_dict, exists_control, recepctions_dict

ComplementType = TypeVar("ComplementType", bound="ComplementBuilder")


class MonthlyVolumeReportValidator:
    """Validation of VolumenMensualReporte."""

    def __init__(self, monthly_volume_report: dict, product_key: str, caracter: str):
        self.monthly_report = monthly_volume_report
        self.product_key = product_key
        self.caracter = caracter
        self._errors = {}
        self._report_errors = []
        self._executed_functions = set()

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
    #     DictionaryTypeValidator().validate_dict_type(dict_to_validate=self.monthly_report, dict_type=month_report_dict)

    @exception_wrapper
    def _validate_control_existencias(self) -> None:
        if not (inv_control := self.monthly_report.get("ControlDeExistencias")):
            return

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=inv_control, dict_type=exists_control):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)

        month_volume = inv_control.get("VolumenExistenciasMes")
        month_measure_date = inv_control.get("FechaYHoraEstaMedicionMes")

        if month_volume is None:
            self.catch_error(err_type=ClaveError, err_message="Error: 'VolumenExistenciasMes' no fue encontrada.")
        if month_measure_date is None:
            self.catch_error(err_type=ClaveError, err_message="Error: 'FechaYHoraEstaMedicionMes' no fue encontrada.")
        if month_volume and not -100000000000.0 <= month_volume <= 100000000000.0:
            self._min_max_value_error(
                key="VolumenExistenciasMes", value=month_volume, min_val=-100000000000.0, max_val=100000000000.0,
                )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message="Error:'VolumenExistenciasMes'
            # no está en el rango min -100000000000.0 o max 100000000000.0")
        if month_measure_date and not re.match(UTC_FORMAT_REGEX, month_measure_date):
            self.catch_error(
                err_type=TipadoError,
                err_message="Error: 'FechaYHoraEstaMedicionMes' no se expresa en UTC 'yyyy-mm-ddThh:mm:ss+-hh:mm'."
                )

    @exception_wrapper
    def _validate_recepciones(self) -> None:
        if (receptions := self.monthly_report.get("Recepciones")) is None:
            self.catch_error(err_type=RecepcionesError, err_message="Error: 'Recepciones' no fue declarada.")
            # raise RecepcionesError("Error: 'Recepciones' no fue declarada.")

        if err := DictionaryTypeValidator().validate_dict_type(dict_to_validate=receptions, dict_type=recepctions_dict):
            type_err = err.get("type_err")
            err_message = err.get("err_message")
            self.catch_error(err_type=type_err, err_message=err_message)

        total_receptions_month = receptions.get("TotalRecepcionesMes")
        amount_volume_reception_month = receptions.get("SumaVolumenRecepcionMes")
        month_documents = receptions.get("TotalDocumentosMes")
        cal_value = receptions.get("PoderCalorifico")
        amount_receptions_month = receptions.get("ImporteTotalRecepcionesMensual")
        complement = receptions.get("Complemento")

        if total_receptions_month is None:
            self.catch_error(
                err_type=RecepcionesError,
                err_message="Error: 'TotalRecepcionesMes' no fue declarada."
                )
        if amount_volume_reception_month is None:
            self.catch_error(
                err_type=RecepcionesError,
                err_message="Error: 'SumaVolumenRecepcionMes' no fue declarada."
                )
        if month_documents is None:
            self.catch_error(
                err_type=RecepcionesError,
                err_message="Error: 'TotalDocumentosMes' no fue declarada."
                )
        if amount_receptions_month is None:
            self.catch_error(
                err_type=RecepcionesError,
                err_message="Error: 'ImporteTotalRecepcionesMensual' no fue declarada."
                )
        if complement is None:
            self.catch_error(
                err_type=RecepcionesError,
                err_message="Error: Valor 'Complemento' no fue declarada en clave 'Recepciones'."
                )

        if total_receptions_month and not 0 <= total_receptions_month <= 100000000:
            self._min_max_value_error(
                key="TotalRecepcionesMes", value=total_receptions_month, min_val=0, max_val=100000000,
                )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message="Error: 'TotalRecepcionesMes' no está en el rango min 0 o max 100000000.")
        if self.product_key == "PR09" and self.caracter in cal_value_caracteres and cal_value is None:
            self.catch_error(
                err_type=RecepcionesError,
                err_message=f"""Error: 'PoderCalorifico' es requerido para caracteres {cal_value_caracteres} y Producto 'PR09'."""
                )
        if month_documents and month_documents > 1000000:
            self._min_max_value_error(
                key="TotalDocumentosMes", value=month_documents, min_val=0, max_val=1000000,
                )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message="Error: 'TotalDocumentosMes' no está en el rango max 1000000.")
        if amount_receptions_month and not 0 <= amount_receptions_month <= 100000000000.0:
            self._min_max_value_error(
                key="ImporteTotalRecepcionesMensual", value=amount_receptions_month, min_val=0, max_val=100000000000.0,
                )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message="Error: 'ImporteTotalRecepcionesMensual' no está en el rango min 0 o max 100000000000.0")

    # @exception_wrapper
    def __validate_recepciones_complemento(self) -> None:
        receives = self.monthly_report.get("Recepciones")
        if (complement := receives.get("Complemento")) is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'Complemento' no fue expresada."
                )
            return

        if not complement:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'Complemento' vacía."
                )
            return

        if (comp_type := complement[0].get("TipoComplemento")) is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'TipoComplemento' no fue expresada."
                )
            return

        if self._check_complement(complement_type=comp_type):
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
        if amount_volume_deliveries_month is None:
            self.catch_error(err_type=EntregasError, err_message="Error: 'SumaVolumenEntregadoMes' no fue declarada.")
        if month_documents is None:
            self.catch_error(err_type=EntregasError, err_message="Error: 'TotalDocumentosMes' no fue declarada.")
        if amount_deliveries_month is None:
            self.catch_error(err_type=EntregasError, err_message="Error: 'ImporteTotalEntregasMes' no fue declarada.")
        if complement is None:
            self.catch_error(
                err_type=EntregasError,
                err_message="Error: Valor 'Complemento' no fue declarada en clave 'Entregas'."
                )

        if total_deliveries_month and not 0 <= total_deliveries_month <= 10000000:
            self._min_max_value_error(
                key="TotalEntregasMes", value=total_deliveries_month, min_val=0, max_val=10000000,
                )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message="Error: 'TotalEntregasMes' no está en el rango min 0 o max 10000000."
            #     )
        if self.product_key == "PR09" and (deliveries.get("PoderCalorifico")) is None:
            self.catch_error(
                err_type=EntregasError,
                err_message="Error: 'PoderCalorifico' es requerido para caracteres Producto 'PR09'."
                )
        if month_documents and not 0 <= month_documents <= 100000000:
            self._min_max_value_error(
                key="TotalDocumentosMes", value=month_documents, min_val=0, max_val=100000000,
                )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message="Error: 'TotalDocumentosMes' no está en el rango min 0 o max 100000000."
            #     )
        # amount_deliveries_month = 1.222222
        if amount_deliveries_month and not 0 <= round(amount_deliveries_month, 3) <= 100000000000.0:
            self._min_max_value_error(
                key="ImporteTotalEntregasMes", value=round(amount_deliveries_month, 3),
                min_val=0, max_val=100000000000.0,
                )
            # self.catch_error(
            #     err_type=ValorMinMaxError,
            #     err_message="Error: 'ImporteTotalEntregasMes' no está en el rango min 0 o max 100000000000.0"
            #     )

    # @exception_wrapper
    def __validate_entregas_complemento(self) -> None:
        deliveries = self.monthly_report.get("Entregas")

        if (complement := deliveries.get("Complemento")) is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'Complemento' no fue expresada."
                )
            return

        if not complement:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'Complemento' vacía."
                )
            return

        if (comp_type := complement[0].get("TipoComplemento")) is None:
            self.catch_error(
                err_type=ClaveError,
                err_message="Error: clave 'TipoComplemento' no fue expresada."
                )
            return

        if self._check_complement(complement_type=comp_type):
            complement_obj = complement_builder(complement_data=complement, complement_type=comp_type)
            complement_obj.validate_complemento()

            if complement_errors := complement_obj.errors:
                self._report_errors.extend(complement_obj.get_error_list())
                self._errors = self._errors | complement_errors

    def _check_complement(self, complement_type: str) -> bool:
        """Check if complement is a valid complement."""
        if complement_type not in {en.value for en in ComplementTypeEnum}:
            self.catch_error(err_type=TipadoError, err_message=f"Error: TipoComplemento {complement_type} no válido.")
            return False
        return True

    def catch_error(self, err_type: BaseException, err_message: str, source: Optional[str] = None) -> None:
        """Store given error in class error list.
        :param err_type: Class from BaseException inherit.\n
        :param err_message: Message of the given error.\n
        :param source: Source reference of the error\n
        :return: None."""
        self.errors = {
            "type_error": err_type.__name__, 
            "error": err_message,
            "source": source,
            }

    def _min_max_value_error(
            self,
            key: str,
            value: Union[int, float, str],
            min_val: Union[int, float, str],
            max_val: Union[int, float, str],
            source: Optional[str] = None,
        ) -> None:
        """Store LongitudError in self.errors.\n
        :param key: Dict key element.\n
        :param value: value that unmatch range.\n
        :param min_val: minimium value.\n
        :param max_val: maximum value.\n
        :param source: Object reference where key and value are palced.\n
        :return: None."""
        self.catch_error(
            err_type=ValorMinMaxError,
            err_message=f"Error: clave {key} con valor {value} no tiene el valor min {min_val} ó max {max_val}.",
            source=source
        )

    def _longitud_error(
            self,
            key: str,
            value: Union[int, float],
            min_long: Union[int, float],
            max_long: Union[int, float],
            source: Optional[str] = None,
        ) -> None:
        """Store LongitudError in self.errors.\n
        :param key: Dict key element.\n
        :param value: value that unmatch lenght.\n
        :param min_long: minimium lenght.\n
        :param max_long: maximum lenght.\n
        :param source: Object reference where key and value are palced.\n
        :return: None."""
        self.catch_error(
            err_type=LongitudError,
            err_message=f"Error: clave {key} con valor {value} no tiene una longitud min {min_long} ó max {max_long}.",
            source=source
        )

    def _value_error(
            self,
            key: str,
            value: Union[int, float],
            source: Optional[str] = None,
        ) -> None:
        """Store ValorError in self.errors.\n
        :param key: Dict key element.\n
        :param value: value that is invalid.\n
        :param source: Object reference where key and value are palced.\n
        :return: None."""
        self.catch_error(
            err_type=ValorError,
            err_message=f"Error: valor '{value}' en clave {key} no válido.",
            source=source
        )

    def _regex_error(
            self,
            key: str,
            value: Union[int, float],
            pattern: str,
            source: Optional[str] = None,
        ) -> None:
        """Store RegexError in self.errors.\n
        :param key: Dict Key element.\n
        :param value: value that unmatch regex.\n
        :param patter: Reggex pattern.\n
        :param source: Object reference where key and value are palced.\n
        :return: None."""
        self.catch_error(
            err_type=RegexError,
            err_message=f"Error: clave {key} con valor {value} no cumple con el patrón {pattern}",
            source=source
        )

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
