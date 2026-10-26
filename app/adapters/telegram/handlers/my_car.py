"""Button 'my car': ask six questions, then show the estimate."""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.adapters.telegram import dbrun
from app.adapters.telegram.handlers import my_car_flow as flow
from app.adapters.telegram.handlers.my_car_flow import MyCar
from app.adapters.telegram.texts import my_car as t
from app.adapters.telegram.texts import menu
from app.config import Settings
from app.core import model_lookup, my_car_calc, my_car_view
from app.data import repo_published

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


@router.message(F.text == menu.BTN_MY_CAR)
async def on_start(message: Message, settings: Settings, state: FSMContext) -> None:
    await state.clear()
    data = dbrun.run(settings, repo_published.get)
    names = model_lookup.model_names(data["rows"]) if data else []
    if not names:
        await message.answer(t.NO_DATA)
        return
    await state.update_data(names=names, page=0)
    await state.set_state(MyCar.model)
    text, kb = flow.screen("model", await state.get_data())
    await message.answer(text, reply_markup=kb)


@router.callback_query(MyCar.model, F.data.regexp(r"^mc:p:\d+$"))
async def on_page(cb: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(page=int(cb.data.split(":")[2]))
    await flow.show(cb, state, "model")
    await cb.answer()


@router.callback_query(MyCar.model, F.data.regexp(r"^mc:m:\d+$"))
async def on_model(cb: CallbackQuery, state: FSMContext) -> None:
    names = (await state.get_data())["names"]
    index = int(cb.data.split(":")[2])
    if index >= len(names):
        await cb.answer()
        return
    await state.update_data(name=names[index])
    await flow.show(cb, state, "year")
    await cb.answer()


@router.callback_query(MyCar.year, F.data.regexp(r"^mc:y:\d+$"))
async def on_year(cb: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(year=int(cb.data.split(":")[2]))
    await flow.show(cb, state, "km")
    await cb.answer()


async def _answer(cb: CallbackQuery, state: FSMContext, key: str, nxt: str) -> None:
    await state.update_data(**{key: int(cb.data.split(":")[2])})
    await flow.show(cb, state, nxt)
    await cb.answer()


@router.callback_query(MyCar.km, F.data.regexp(r"^mc:k:\d+$"))
async def on_km(cb: CallbackQuery, state: FSMContext) -> None:
    await _answer(cb, state, "km", "body")


@router.callback_query(MyCar.body, F.data.regexp(r"^mc:b:\d+$"))
async def on_body(cb: CallbackQuery, state: FSMContext) -> None:
    await _answer(cb, state, "body", "chassis")


@router.callback_query(MyCar.chassis, F.data.regexp(r"^mc:c:\d+$"))
async def on_chassis(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    await state.update_data(chassis=int(cb.data.split(":")[2]))
    answers = await state.get_data()
    await state.clear()
    data = dbrun.run(settings, repo_published.get)
    result = my_car_calc.compute(data, answers)
    if result["status"] != "ok":
        await cb.message.edit_text(t.NO_DATA)
    else:
        text = my_car_view.build_text(result, answers["name"], answers["year"], t)
        await cb.message.edit_text(text)
    await cb.answer()


@router.callback_query(F.data == "mc:back")
async def on_back(cb: CallbackQuery, state: FSMContext) -> None:
    current = (await state.get_state() or "").split(":")[-1]
    if current in flow.PREV:
        await flow.show(cb, state, flow.PREV[current])
    await cb.answer()


@router.callback_query(F.data == "mc:x")
async def on_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.edit_text(t.CANCELLED)
    await cb.answer()
