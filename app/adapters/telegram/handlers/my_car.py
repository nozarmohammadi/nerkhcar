"""Button 'my car': typed name, year and km, then two button questions."""
from datetime import datetime
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from app.adapters.telegram import dbrun
from app.adapters.telegram.handlers import my_car_flow as flow, my_car_year_prompt as yp
from app.adapters.telegram.handlers.my_car_flow import MyCar
from app.adapters.telegram.keyboards import my_car as k
from app.adapters.telegram.texts import menu
from app.adapters.telegram.texts import my_car as t
from app.config import Settings
from app.core import my_car_calc, my_car_input, my_car_view
from app.core import body_parts as body_logic
from app.data import repo_catalog, repo_estimates, repo_prices
from app.core import my_car_years
from app.core import daily_text, used_base_auto
from app.data import repo_published
router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")
@router.message(F.text == menu.BTN_MY_CAR)
async def on_start(message: Message, settings: Settings, state: FSMContext) -> None:
    await state.clear()
    catalog = dbrun.run(settings, repo_catalog.list_user_trims)
    names = sorted({row["model"] for row in catalog}) if catalog else []
    if not names:
        await message.answer(t.NO_DATA)
        return
    await state.update_data(names=names, catalog=catalog)
    await state.set_state(MyCar.name)
    await message.answer(t.ASK_NAME, reply_markup=k.cancel_kb())
@router.message(MyCar.name, F.text, ~F.text.in_(menu.MENU_BUTTONS))
async def on_name(message: Message, state: FSMContext, settings: Settings) -> None:
    names = (await state.get_data())["names"]
    found = my_car_input.search(names, message.text)
    if not found:
        await message.answer(t.NOT_FOUND, reply_markup=k.cancel_kb())
        return
    if len(found) == 1:
        data = await state.get_data()
        catalog = data.get("catalog", [])
        trim = next((row for row in catalog if row["model"] == found[0]), None)
        update = {"name": found[0]}
        if trim is not None:
            update["trim_id"] = trim["trim_id"]
        await state.update_data(**update)
        await state.set_state(MyCar.year)
        await message.answer(yp.year_prompt(settings, found[0]), reply_markup=k.cancel_kb())
        return
    await state.update_data(found=found)
    await state.set_state(MyCar.pick)
    text, kb = flow.pick_screen(found)
    await message.answer(text, reply_markup=kb)
@router.callback_query(MyCar.pick, F.data.regexp(r"^mc:m:\d+$"))
async def on_pick(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    found = (await state.get_data())["found"]
    index = int(cb.data.split(":")[2])
    if index >= len(found):
        await cb.answer()
        return
    catalog = (await state.get_data())["catalog"]
    trim = next(row for row in catalog if row["model"] == found[index])
    await state.update_data(name=found[index], trim_id=trim["trim_id"])
    await state.set_state(MyCar.year)
    await cb.message.edit_text(yp.year_prompt(settings, found[index]), reply_markup=k.cancel_kb())
    await cb.answer()
@router.message(MyCar.year, F.text, ~F.text.in_(menu.MENU_BUTTONS))
async def on_year(
    message: Message, state: FSMContext, settings: Settings
) -> None:
    current = used_base_auto.current_year(datetime.now())
    year = my_car_input.read_year(message.text, current)
    if year is None:
        await message.answer(t.BAD_YEAR, reply_markup=k.cancel_kb())
        return
    data = await state.get_data()
    published = dbrun.run(settings, repo_published.get)
    rows = published["rows"] if published else []
    if my_car_years.check_year(rows, data["name"], year) == "after_last":
        last = my_car_years.last_year(rows, data["name"])
        await message.answer(
            t.YEAR_AFTER_LAST.format(year=daily_text.fa(last)),
            reply_markup=k.cancel_kb())
        return
    await state.update_data(year=my_car_years.match_year(rows, data["name"], year))
    await state.set_state(MyCar.km)
    await message.answer(t.ASK_KM_TYPED, reply_markup=k.km_skip_kb())

@router.callback_query(MyCar.km, F.data == "mc:km:skip")
async def on_km_skip(cb: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(km=None)
    await state.set_state(MyCar.body_mode)
    await cb.message.edit_text(
        t.ASK_BODY,
        reply_markup=k.body_mode_kb(t.BODY_MODE_LABELS),
    )
    await cb.answer()

@router.message(MyCar.km, F.text, ~F.text.in_(menu.MENU_BUTTONS))
async def on_km(message: Message, state: FSMContext) -> None:
    km = my_car_input.read_km(message.text)
    if km is None:
        await message.answer(t.BAD_KM, reply_markup=k.cancel_kb())
        return
    await state.update_data(km=km)
    await state.set_state(MyCar.body_mode)
    await message.answer(
        t.ASK_BODY,
        reply_markup=k.body_mode_kb(t.BODY_MODE_LABELS),
    )

@router.callback_query(MyCar.body_mode, F.data.regexp(r"^mc:bm:[01]$"))
async def on_body_mode(cb: CallbackQuery, state: FSMContext) -> None:
    mode = "repaint" if cb.data.endswith(":0") else "replaced"
    await state.update_data(body_mode=mode, body_parts=[])
    await state.set_state(MyCar.body_parts)
    await cb.message.edit_text(
        t.ASK_BODY_PARTS,
        reply_markup=k.body_parts_kb(t.BODY_PART_LABELS, set()),
    )
    await cb.answer()

@router.callback_query(MyCar.body_parts, F.data.regexp(r"^mc:bp:.+$"))
async def on_body_part(cb: CallbackQuery, state: FSMContext) -> None:
    key = cb.data.split(":", 2)[2]
    data = await state.get_data()
    selected = set(data.get("body_parts", []))
    if key == "done":
        body = body_logic.classify(data["body_mode"], list(selected))
        await state.update_data(body=body, body_parts=list(selected))
        await state.set_state(MyCar.chassis)
        text, kb = flow.choice_screen("chassis")
        await cb.message.edit_text(text, reply_markup=kb)
    else:
        if key in selected:
            selected.remove(key)
        else:
            selected.add(key)
        await state.update_data(body_parts=list(selected))
        await cb.message.edit_reply_markup(
            reply_markup=k.body_parts_kb(t.BODY_PART_LABELS, selected)
        )
    await cb.answer()

@router.callback_query(MyCar.chassis, F.data.regexp(r"^mc:c:\d+$"))
async def on_chassis(cb: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(chassis=int(cb.data.split(":")[2]))
    await state.set_state(MyCar.color)
    await cb.message.edit_text(
        t.ASK_COLOR,
        reply_markup=k.color_kb(t.COLOR_LABELS),
    )
    await cb.answer()

@router.callback_query(MyCar.color, F.data.regexp(r"^mc:cl:\d+$"))
async def on_color(
    cb: CallbackQuery, state: FSMContext, settings: Settings
) -> None:
    index = int(cb.data.split(":")[2])
    if index >= len(t.COLOR_LABELS):
        await cb.answer()
        return
    answers = await state.get_data(); answers["color"] = t.COLOR_LABELS[index][0]
    await state.clear(); data = dbrun.run(settings, repo_published.get)
    price = dbrun.run(
        settings,
        lambda conn: repo_prices.get_price(
            conn, answers["trim_id"], answers["year"]
        ),
    )
    zero = None if price is None else price.low
    result = my_car_calc.compute(data, answers, zero=zero)
    if result["status"] != "ok":
        await cb.message.edit_text(t.NO_DATA)
    else:
        dbrun.run(
            settings,
            lambda conn: repo_estimates.add(
                conn, cb.from_user.id, answers, result
            ),
        )
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
