"""This module handle constants."""

complement_type = ["Almacenamiento", "CDLR", "Comercializacion",
                   "Distribucion", "Expendio", "Extraccion", "Refinacion", "Transporte"]

TRANSPORT_PERM_REGEX = r"^(PL/[0-9]{1,5}/TRA/OM/[0-9]{4})|(PL/[0-9]{1,5}/TRA/DUC/[0-9]{4})|(PL/[0-9]{1,5}/TRA/TM/[0-9]{4})|(PQ/[0-9]{1,5}/TRA/DUC/[0-9]{4})|(G/[0-9]{1,5}/TUP/[0-9]{4})|(G/[0-9]{1,5}/SAB/[0-9]{4})|(G/[0-9]{1,5}/TRA/OM/[0-9]{4})|(P/[0-9]{1,5}/TRA/TM/[0-9]{4})|(P/[0-9]{1,5}/TRA/OM/[0-9]{4})|(G/[0-9]{1,5}/TRA/[0-9]{4})|(GN/[0-9]{1,5}/P/TRA/DUC/[0-9]{4})|(GN/[0-9]{1,5}/TRA/DUC/[0-9]{4})|(P/[0-9]{1,5}/TRA/DUC/[0-9]{4})|(P/[0-9]{1,5}/P/TRA/DUC/[0-9]{4})|(LP/[0-9]{1,5}/TRA/DUC/[0-9]{4})|(G/[0-9]{1,5}/LPT/[0-9]{4})|(LP/[0-9]{1,5}/TRA/[0-9]{4})$"
TRANSPORT_PERM_EXO_REGEX = r"^(PL/[0-9]{1,5}/TRA/OM/[0-9]{4})|(PL/[0-9]{1,5}/TRA/DUC/[0-9]{4})|(PL/[0-9]{1,5}/TRA/TM/[0-9]{4})|(PQ/[0-9]{1,5}/TRA/DUC/[0-9]{4})|(G/[0-9]{1,5}/TUP/[0-9]{4})|(G/[0-9]{1,5}/SAB/[0-9]{4})|(G/[0-9]{1,5}/TRA/OM/[0-9]{4})|(G/[0-9]{1,5}/TRA/[0-9]{4})|(GN/[0-9]{1,5}/P/TRA/DUC/[0-9]{4})|(GN/[0-9]{1,5}/TRA/DUC/[0-9]{4})$"
TRANSP_PERM_CDLRGN_REGEX = r"^(G/[0-9]{1,5}/TUP/[0-9]{4})|(G/[0-9]{1,5}/SAB/[0-9]{4})|(G/[0-9]{1,5}/TRA/OM/[0-9]{4})|(G/[0-9]{1,5}/TRA/[0-9]{4})|(GN/[0-9]{1,5}/P/TRA/DUC/[0-9]{4})|(GN/[0-9]{1,5}/TRA/DUC/[0-9]{4})|(LP/[0-9]{1,5}/TRA/DUC/[0-9]{4})$"
PERMISSION_PROOVE_REGEX = r"^(H/[0-9]{1,5}/COM/[0-9]{4})|(PL/[0-9]{1,5}/DIS/OM/[0-9]{4})|(G/[0-9]{1,5}/COM/GN/[0-9]{4})|(G/[0-9]{1,5}/COM/PETRO/[0-9]{4})|(G/[0-9]{1,5}/COM/CEE/[0-9]{4})|(G/[0-9]{1,5}/DIS/[0-9]{4})|(G/[0-9]{1,5}/DIS/OM/[0-9]{4})|(LP/[0-9]{1,5}/DIST/AUT/[0-9]{4})|(LP/[0-9]{1,5}/DIST/PLA/[0-9]{4})|(LP/[0-9]{1,5}/DIST/DUC/[0-9]{4})|(G/[0-9]{1,5}/LPD/[0-9]{4})|(LP/[0-9]{1,5}/COM/[0-9]{4})|(LP/[0-9]{1,5}/DIST/REP/[0-9]{4})|(PL/[0-9]{1,5}/DIS/DUC/[0-9]{4})$"
PERMISSION_PROOVE_CLIENT_REGEX = r"(H/[0-9]{1,5}/COM/[0-9]{4})|(PL/[0-9]{1,5}/EXP/ES/[0-9]{4})|(PL/[0-9]{1,5}/EXP/ES/MM/[0-9]{4})|(PL/[0-9]{1,5}/EXP/ESA/[0-9]{4})|(PL/[0-9]{1,5}/DIS/OM/[0-9]{4})|(H/[0-9]{1,5}/COM/[0-9]{4})|(PL/[0-9]{1,5}/EXP/AE/[0-9]{4})|(G/[0-9]{1,5}/COM/GN/[0-9]{4})|(G/[0-9]{1,5}/COM/PETRO/[0-9]{4})|(G/[0-9]{1,5}/COM/CEE/[0-9]{4})|(G/[0-9]{1,5}/DIS/[0-9]{4})|(G/[0-9]{1,5}/DIS/OM/[0-9]{4})|(G/[0-9]{1,5}/EXP/ES/FE/[0-9]{4})|(G/[0-9]{1,5}/EXP/ES/MM/[0-9]{4})|(G/[0-9]{1,5}/LICUE/[0-9]{4})|(G/[0-9]{1,5}/REG/[0-9]{4})|(LP/[0-9]{1,5}/DIST/AUT/[0-9]{4})|(LP/[0-9]{1,5}/DIST/PLA/[0-9]{4})|(LP/[0-9]{1,5}/DIST/DUC/[0-9]{4})|(G/[0-9]{1,5}/LPD/[0-9]{4})|(LP/[0-9]{1,5}/EXP/ES/[0-9]{4})|(LP/[0-9]{1,5}/EXP/AUT/[0-9]{4})|(LP/[0-9]{1,5}/COM/[0-9]{4})|(LP/[0-9]{1,5}/DIST/REP/[0-9]{4})|(PL/[0-9]{1,5}/EXP/ESA/MM/[0-9]{4})|(PL/[0-9]{1,5}/DIS/DUC/[0-9]{4})|(SENER-REF-[0-9]{1,3}-[0-9]{4})|(SENER-TP-[0-9]{1,3}-[0-9]{4})|(SENER-CPG-[0-9]{1,3}-[0-9]{4})$"
PERMISSION_PROOVE_CLIENT_DIS_REGEX = r"^(H/[0-9]{1,5}/COM/[0-9]{4})|(PL/[0-9]{1,5}/EXP/ES/[0-9]{4})|(PL/[0-9]{1,5}/EXP/ES/MM/[0-9]{4})|(PL/[0-9]{1,5}/EXP/ESA/[0-9]{4})|(H/[0-9]{1,5}/COM/[0-9]{4})|(PL/[0-9]{1,5}/EXP/AE/[0-9]{4})|(G/[0-9]{1,5}/COM/GN/[0-9]{4})|(G/[0-9]{1,5}/COM/PETRO/[0-9]{4})|(G/[0-9]{1,5}/COM/CEE/[0-9]{4})|(G/[0-9]{1,5}/EXP/ES/FE/[0-9]{4})|(G/[0-9]{1,5}/EXP/ES/MM/[0-9]{4})|(G/[0-9]{1,5}/LICUE/[0-9]{4})|(G/[0-9]{1,5}/REG/[0-9]{4})|(LP/[0-9]{1,5}/EXP/ES/[0-9]{4})|(LP/[0-9]{1,5}/EXP/AUT/[0-9]{4})|(LP/[0-9]{1,5}/COM/[0-9]{4})|(PL/[0-9]{1,5}/EXP/ESA/MM/[0-9]{4})|(SENER-REF-[0-9]{1,3}-[0-9]{4})|(SENER-TP-[0-9]{1,3}-[0-9]{4})|(SENER-CPG-[0-9]{1,3}-[0-9]{4})$"
PERMISSION_PROOVE_CLIENT_EXO_REGEX = r"^(H/[0-9]{1,5}/COM/[0-9]{4})|(PL/[0-9]{1,5}/DIS/OM/[0-9]{4})|(G/[0-9]{1,5}/COM/GN/[0-9]{4})|(G/[0-9]{1,5}/DIS/[0-9]{4})|(G/[0-9]{1,5}/DIS/OM/[0-9]{4})|(LP/[0-9]{1,5}/DIST/AUT/[0-9]{4})|(LP/[0-9]{1,5}/DIST/PLA/[0-9]{4})|(LP/[0-9]{1,5}/DIST/DUC/[0-9]{4})|(G/[0-9]{1,5}/LPD/[0-9]{4})|(LP/[0-9]{1,5}/COM/[0-9]{4})|(LP/[0-9]{1,5}/DIST/REP/[0-9]{4})|(PL/[0-9]{1,5}/DIS/DUC/[0-9]{4})|(SENER-REF-[0-9]{1,3}-[0-9]{4})$"
PERMISSION_ALM_DIST_REGEX = r"^(PL/[0-9]{1,5}/DIS/OM/[0-9]{4})|(PL/[0-9]{1,5}/ALM/[0-9]{4})|(PQ/[0-9]{1,5}/ALM/[0-9]{4})|(PL/[0-9]{1,5}/ALM/AE/[0-9]{4})|(G/[0-9]{1,5}/ALM/[0-9]{4})|(P/[0-9]{1,5}/ALM/[0-9]{4})|(LP/[0-9]{1,5}/DIST/AUT/[0-9]{4})|(LP/[0-9]{1,5}/DIST/PLA/[0-9]{4})|(LP/[0-9]{1,5}/DIST/DUC/[0-9]{4})|(G/[0-9]{1,5}/LPD/[0-9]{4})|(LP/[0-9]{1,5}/ALM/[0-9]{4})|(G/[0-9]{1,5}/LPA/[0-9]{4})|(LP/[0-9]{1,5}/DIST/REP/[0-9]{4})|(PL/[0-9]{1,5}/DIS/DUC/[0-9]{4})$"
PERMISSION_ALM_CDLRGN_REGEX = r"^G/[0-9]{1,5}/ALM/[0-9]{4}$"
PERMISSION_ALM_REGEX = r"^(PL/[0-9]{1,5}/ALM/[0-9]{4})|(PQ/[0-9]{1,5}/ALM/[0-9]{4})|(PL/[0-9]{1,5}/ALM/AE/[0-9]{4})|(G/[0-9]{1,5}/ALM/[0-9]{4})|(P/[0-9]{1,5}/ALM/[0-9]{4})|(LP/[0-9]{1,5}/ALM/[0-9]{4})|(G/[0-9]{1,5}/LPA/[0-9]{4})$"
ADUANAL_PEDIMENTO = r"^[0-9]{2} (0[1-2]|0[5-8]|1[1-2]|14|1[6-9]|20|2[2-8]|3[0-1]|3[3-4]|3[7-9]|40|4[2-4]|4[6-8]|5[0-3]|6[4-5]|67|73|75|8[0-4]) [0-9]{4} [0-9](?!0{6})[0-9]{6}$"
INTERN_SPOT_REGEX = r"^(0[1-2]|0[5-8]|1[1-2]|14|1[6-9]|20|2[2-8]|3[0-1]|3[3-4]|3[7-9]|40|4[2-4]|4[6-8]|5[0-3]|6[4-5]|67|73|75|8[0-4])([0-7])?$"
FOLIO_CERTIFIED_REGEX = r"^([A-ZÑ]|\&){3}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}[0-9]{5}[12][0-9]{3}$"
FOLIO_DICTAMEN_REGEX = r"^([A-ZÑ]|\&){3}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}[0-9]{5}[12][0-9]{3}$"
# Folio built from a 12 or 13 character RFC, so it accepts both persona moral and persona fisica.
FOLIO_REGEX = r"^([A-ZÑ]|\&){3,4}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}[0-9]{5}[12][0-9]{3}$"
RFC_PERSONA_MORAL_REGEX = r"^([A-ZÑ]|\&){3}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}$"
CFDI_REGEX = r"^[a-f0-9A-F]{8}-[a-f0-9A-F]{4}-[a-f0-9A-F]{4}-[a-f0-9A-F]{4}-[a-f0-9A-F]{12}$"
# UUID that also rejects the sixteen placeholder folios built from a single repeated hex digit.
# The SAT publishes this pattern with inline "(?i)" flags in the middle of the expression, which
# Python's re rejects since 3.11; the a-f lookaheads use scoped "(?i:...)" flags instead.
CFDI_STRICT_REGEX = (
    r"^(?!00000000-0000-0000-0000-000000000000)"
    r"(?!11111111-1111-1111-1111-111111111111)"
    r"(?!22222222-2222-2222-2222-222222222222)"
    r"(?!33333333-3333-3333-3333-333333333333)"
    r"(?!44444444-4444-4444-4444-444444444444)"
    r"(?!55555555-5555-5555-5555-555555555555)"
    r"(?!66666666-6666-6666-6666-666666666666)"
    r"(?!77777777-7777-7777-7777-777777777777)"
    r"(?!88888888-8888-8888-8888-888888888888)"
    r"(?!99999999-9999-9999-9999-999999999999)"
    r"(?!(?i:aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa))"
    r"(?!(?i:bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb))"
    r"(?!(?i:cccccccc-cccc-cccc-cccc-cccccccccccc))"
    r"(?!(?i:dddddddd-dddd-dddd-dddd-dddddddddddd))"
    r"(?!(?i:eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee))"
    r"(?!(?i:ffffffff-ffff-ffff-ffff-ffffffffffff))"
    r"([a-f0-9A-F]{8}-[a-f0-9A-F]{4}-[a-f0-9A-F]{4}-[a-f0-9A-F]{4}-[a-f0-9A-F]{12})$"
)
RFC_REGEX = r"^([A-ZÑ]|\&){3,4}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}$"
DATE_REGEX = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
UTC_FORMAT_REGEX = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$"
IMPORT_PERMISSION_REGEX = r"^[a-zA-Z0-9]{4}C[a-zA-Z0-9]{9}$"
# Guide version 0.7.1 also admits the "G" prefixed nomenclature for import or export permissions.
IMPORT_EXPORT_PERMISSION_REGEX = r"^([a-zA-Z0-9]{4}C[a-zA-Z0-9]{9})$|^([G]{1}[0-9]{1,17})$"
# Any text of 1 to 150 characters that does not contain the pipe separator.
CLIENT_NAME_REGEX = r"^[^|]{1,150}$"
MEASURE_UNIT = r"^UM0[1-4]$"
