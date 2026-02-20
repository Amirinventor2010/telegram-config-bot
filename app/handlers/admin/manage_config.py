from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.database.models import Config
from app.keyboards.admin_config_inline_kb import (
    config_manage_keyboard,
    config_pagination_keyboard
)

router = Router()

CONFIGS_PER_PAGE = 10


# =====================================================
# 🎛 Pagination State
# =====================================================
class AdminConfigPagination(StatesGroup):
    offset = State()
    config_type = State()


# =====================================================
# 📡 مدیریت کانفیگ V2Ray
# =====================================================
@router.message(F.text == "📡 مدیریت کانفیگ V2Ray")
async def list_v2ray_configs(message: Message, state: FSMContext):
    await load_configs(message, state, "v2ray")


# =====================================================
# 🛰 مدیریت کانفیگ NPV
# =====================================================
@router.message(F.text == "🛰 مدیریت کانفیگ NPV")
async def list_npv_configs(message: Message, state: FSMContext):
    await load_configs(message, state, "npv")


async def load_configs(message: Message, state: FSMContext, config_type: str):

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Config)
            .where(Config.type == config_type)
            .order_by(Config.id.desc())
        )
        configs = result.scalars().all()

    if not configs:
        await message.answer("❌ هیچ کانفیگی ثبت نشده است.")
        return

    await state.update_data(
        configs=[{
            "id": c.id,
            "type": c.type,
            "active": c.is_active,
            "value": c.value,
            "title": c.title
        } for c in configs],
        offset=0,
        config_type=config_type
    )

    await send_admin_config_page(message, state)


# =====================================================
# ➡️ صفحه بعد
# =====================================================
@router.callback_query(F.data == "next_admin_configs")
async def next_admin_configs(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    if not data:
        await callback.answer("اطلاعات منقضی شده.", show_alert=True)
        return

    await callback.answer()
    await send_admin_config_page(callback.message, state)


# =====================================================
# 📄 ارسال صفحه
# =====================================================
async def send_admin_config_page(message, state: FSMContext):

    data = await state.get_data()
    configs = data.get("configs", [])
    offset = data.get("offset", 0)

    if not configs:
        await message.answer("❌ داده‌ای موجود نیست.")
        await state.clear()
        return

    next_offset = offset + CONFIGS_PER_PAGE
    page = configs[offset:next_offset]

    if not page:
        await message.answer("❌ مورد بیشتری وجود ندارد.")
        await state.clear()
        return

    await state.update_data(offset=next_offset)

    for item in page:

        status = "🟢 فعال" if item["active"] else "🔴 غیرفعال"

        text = (
            f"🆔 ID: <code>{item['id']}</code>\n"
            f"📦 نوع: {item['type']}\n"
            f"📝 عنوان: {item['title']}\n"
            f"📊 وضعیت: {status}\n\n"
            f"{item['value']}"
        )

        await message.answer(
            text,
            reply_markup=config_manage_keyboard(
                item["id"],
                item["active"]
            )
        )

    if next_offset < len(configs):
        await message.answer(
            "برای مشاهده ادامه:",
            reply_markup=config_pagination_keyboard()
        )
    else:
        await state.clear()


# =====================================================
# ❌ حذف کانفیگ
# =====================================================
@router.callback_query(F.data.startswith("delete_config:"))
async def delete_config(callback: CallbackQuery):

    config_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Config).where(Config.id == config_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            await callback.answer("یافت نشد.", show_alert=True)
            return

        await session.delete(config)
        await session.commit()

    await callback.message.edit_text("✅ کانفیگ حذف شد.")
    await callback.answer()


# =====================================================
# 🔄 فعال / غیرفعال
# =====================================================
@router.callback_query(F.data.startswith("toggle_config:"))
async def toggle_config(callback: CallbackQuery):

    config_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Config).where(Config.id == config_id)
        )
        config = result.scalar_one_or_none()

        if not config:
            await callback.answer("یافت نشد.", show_alert=True)
            return

        config.is_active = not config.is_active
        await session.commit()

        status = "🟢 فعال" if config.is_active else "🔴 غیرفعال"

        text = (
            f"🆔 ID: <code>{config.id}</code>\n"
            f"📦 نوع: {config.type}\n"
            f"📝 عنوان: {config.title}\n"
            f"📊 وضعیت: {status}\n\n"
            f"{config.value}"
        )

        await callback.message.edit_text(
            text,
            reply_markup=config_manage_keyboard(
                config.id,
                config.is_active
            )
        )

    await callback.answer("وضعیت تغییر کرد.")