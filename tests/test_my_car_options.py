from app.core import my_car_options as o


def test_km_and_bounds():
    assert o.km_of(0) == 10000 and o.km_of(6) == 350000
    assert o.km_of(7) is None and o.km_of(-1) is None


def test_body_chassis():
    assert o.body_of(0) == "clean" and o.body_of(4) is None
    assert o.chassis_of(2) == "major" and o.chassis_of(3) is None


def test_years():
    ys = o.year_choices(1405)
    assert ys[0] == 1405 and len(ys) == 16 and ys[-1] == 1390
