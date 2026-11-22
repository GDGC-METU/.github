import pytest

from waste_sorter.serial_protocol import encode_sort


@pytest.mark.parametrize("label,line", [
    ("plastic", b"SORT:PLASTIC\n"), ("PAPER", b"SORT:PAPER\n"),
    ("metal", b"SORT:METAL\n"), ("unknown", b"SORT:UNKNOWN\n"),
])
def test_encode_sort(label, line):
    assert encode_sort(label) == line


def test_rejects_unrecognized_label():
    with pytest.raises(ValueError):
        encode_sort("glass")
