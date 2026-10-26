from app.adapters.telegram.handlers import my_car


def test_router_has_handlers():
    assert len(my_car.router.callback_query.handlers) == 8
    assert len(my_car.router.message.handlers) == 1
