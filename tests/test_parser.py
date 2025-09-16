from vehiclecodescan.parser.foxwell import parse_foxwell_output


def test_parse_foxwell_csv(tmp_path):
    csv_content = "Code,Status\nP0300,Pending\nP0420,Stored\n"
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(csv_content, encoding="utf-8")

    entries = parse_foxwell_output(csv_path)

    assert [entry.code for entry in entries] == ["P0300", "P0420"]
    assert entries[0].status == "pending"
    assert entries[1].status == "stored"


def test_parse_foxwell_text(tmp_path):
    text = "Found codes: P0171 (pending) and P0442"
    text_path = tmp_path / "sample.txt"
    text_path.write_text(text, encoding="utf-8")

    entries = parse_foxwell_output(text_path)

    codes = {entry.code for entry in entries}
    assert codes == {"P0171", "P0442"}
