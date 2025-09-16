from vehiclecodescan.parser.foxwell import RawDiagnosticEntry
from vehiclecodescan.parser.interpret import interpret_codes


def test_interpret_known_and_unknown_codes():
    entries = [
        RawDiagnosticEntry(code="P0300"),
        RawDiagnosticEntry(code="P9999"),
    ]

    interpreted = interpret_codes(entries, "en")

    assert interpreted[0].known is True
    assert interpreted[0].severity == "high"
    assert "Misfire" in interpreted[0].description

    assert interpreted[1].known is False
    assert interpreted[1].severity == "unknown"
    assert "P9999" in interpreted[1].description
