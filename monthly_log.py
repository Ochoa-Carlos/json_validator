import re
from typing import Union

from constants import UTC_FORMAT_REGEX, component_alarm, event_type
from custom_exceptions import (BitacoraMensualError, LongitudError,
                               ValorMinMaxError)


# TODO VER EL TIPO DE OBJETO QUE ES EN REALIDAD MONTH LOG
class MonthlyLogValidator:

    def __init__(self, month_log: Union[dict, list]) -> None:
        self.month_log = month_log if isinstance(month_log, dict) else month_log[0]

    def validate_log(self) -> None:
        print("====== bitacora mensual=======")
        self._validate_numero_registro()
        self._validate_fecha_evento()
        self._validate_usuario_responsable()
        self._validate_tipo_evento()
        self._validate_descripcion_evento()
        self._validate_id_comp_alarma()

    def _validate_numero_registro(self) -> None:
        if (rec_number := self.month_log.get("NumeroRegistro")) is None:
            raise BitacoraMensualError("Error: 'NumeroRegistro' no fue declarada.")
        if not 0 <= rec_number <= 1000000:
            raise ValorMinMaxError("Error: 'NumeroRegistro' no está en el rango min 0 o max 1000000.")

    def _validate_fecha_evento(self) -> None:
        if (event_date := self.month_log.get("FechaYHoraEvento")) is None:
            raise BitacoraMensualError("Error: 'FechaYHoraEvento' no fue declarada.")
        if not re.match(UTC_FORMAT_REGEX, event_date):
            raise TypeError(
                "Error: 'FechaYHoraEvento' no se expresa en UTC 'yyyy-mm-ddThh:mm:ss+-hh:mm'."
            )

    def _validate_usuario_responsable(self) -> None:
        if (resp_user := self.month_log.get("UsuarioResponsable")) is None:
            return
        print("usuario")
        print(resp_user)
        if not 1 <= len(resp_user) <= 1000:
            raise LongitudError("Error: 'UsuarioResponsable' no cumple con la longitud min 1 o max 1000.")

# TODO validar correctamente el tipo de evento
    def _validate_tipo_evento(self) -> None:
        if (event := self.month_log.get("TipoEvento")) is None:
            raise BitacoraMensualError("Error: 'TipoEvento' no fue declarada.")
        if event not in event_type:
            raise ValorMinMaxError("Error: 'TipoEvento' no está en el rango min 1 o max 21.")


# TODO averiguar el manifestacion de la dscripcion del evento exacto de la difff para evento tipo 7
    def _validate_descripcion_evento(self) -> None:
        if (desc_event := self.month_log.get("DescripcionEvento")) is None:
            raise BitacoraMensualError("Error: 'DescripcionEvento' no fue declarada.")
        if not 2 <= len(desc_event) <= 250:
            raise LongitudError("Error: 'DescripcionEvento' no cumple con la longitud min 2 o max 250.")

    def _validate_id_comp_alarma(self) -> None:
        if self.month_log.get("TipoEvento") not in component_alarm:
            return
        component_id = self.month_log.get("IdentificacionComponenteAlarma")
        if not 2 <= len(component_id) <= 250:
            raise LongitudError("Error: 'IdentificacionComponenteAlarma' no cumple con la longitud min 2 o max 250.")
