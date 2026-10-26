"""Button 'my car': typed name, year and km, then two button questions."""
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.adapters.telegram import dbrun
from app.adapters.telegram.handlers import my_car_flow as flow
from app.adapters.telegram.handlers.my_car_flow import MyCar
from app.adapters.telegram.keyboards import my_car as k
from app.adapters.telegram.texts import menu
from app.adapters.telegram.texts import my_car as t
from app.config import Settings
from app.core import model_lookup, my_car_calc, my_car_input, my_car_view
from app.core import used_base_auto
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
    await state.update_data(names=names)
    await state.set_state(MyCar.name)
    await message.answer(t.ASK_NAME, reply_markup=k.cancel_kb())


@router.message(MyCar.name, F.text, ~F.text.in_(menu.MENU_BUTTONS))
async def on_name(message: Message, state: FSMContext) -> None:
    names = (await state.get_data())["names"]
    found = my_car_input.search(names, message.text)
    if not found:
        await message.answer(t.NOT_FOUND, reply_markup=k.cancel_kb())
        return
    await state.update_data(found=found)
    await state.set_state(MyCar.pick)
    text, kb = flow.pick_screen(found)
    await message.answer(text, reply_markup=kb)


@router.callback_query(MyCar.pick, F.data.regexp(r"^mc:m:\d+$"))
async def on_pick(cb: CallbackQuery, state: FSMContext) -> None:
    found = (await state.get_data())["found"]
    index = int(cb.data.split(":")[2])
    if index >= len(found):
        await cb.answer()
        return
    await state.update_data(name=found[index])
    await state.set_state(MyCar.year)
    await cb.message.edit_text(t.ASK_YEAR_TYPED, reply_markup=k.cancel_kb())
    await cb.answer()


@router.message(MyCar.year, F.text, ~F.text.in_(menu.MENU_BUTTONS))
async def on_year(message: Message, state: FSMContext) -> None:
    current = used_base_auto.current_year(datetime.now())
    year = my_car_input.read_year(message.text, current)
    if year is None:
        await message.answer(t.BAD_YEAR, reply_markup=k.cancel_kb())
        return
    await state.update_data(year=year)
    await state.set_state(MyCar.km)
    await message.answer(t.ASK_KM_TYPED, reply_markup=k.cancel_kb())


@router.message(MyCar.km, F.text, ~F.text.in_(menu.MENU_BUTTONS))
async def on_km(message: Message, state: FSMContext) -> None:
    km = my_car_input.read_km(message.text)
    if km is None:
        await message.answer(t.BAD_KM, reply_markup=k.cancel_kb())
        return
    await state.update_data(km=km)
    await state.set_state(MyCar.body)
    text, kb = flow.choice_screen("body")
    await message.answer(text, reply_markup=kb)


@router.callback_query(MyCar.body, F.data.regexp(r"^mc:b:\d+$"))
async def on_body(cb: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(body=int(cb.data.split(":")[2]))
    await state.set_state(MyCar.chassis)
    text, kb = flow.choice_screen("chassis")
    await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


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
    if current == "chassis":
        await state.set_state(MyCar.body)
        text, kb = flow.choice_screen("body")
        await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data == "mc:x")
async def on_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.edit_text(t.CANCELLED)
    await cb.answer()
