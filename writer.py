from enum import Enum


class Writer(Enum):
    EDGAR_ALLAN_POE = "edgar-allan-poe-poems"

    MAYA_ANGELOU = "maya-angelou-poems"

    SYLVIA_PLATH = "sylvia-plath-poems"

    ROBERT_BURNS = "robert-burns-poems"

    BAQI = "baqi-poems"


def get_filename(writer):
    return "data/" + writer.value + ".csv"
