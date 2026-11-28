from vietsky.validate import check_coordinates


def test_coordinates_ok():
    assert check_coordinates([{"name": "Hà Nội", "lat": "21.03", "lon": "105.85"}]) == []


def test_coordinates_outside():
    errors = check_coordinates([{"name": "X", "lat": "35.0", "lon": "105.85"}])
    assert len(errors) == 1


def test_coordinates_not_number():
    errors = check_coordinates([{"name": "X", "lat": "abc", "lon": "105.85"}])
    assert "Non-numeric" in errors[0]
