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

PROXIES_PER_PAGE = 10


# =====================================================
# 🎛 Pagination State
# =====================================================
class AdminProxyPagination(StatesGroup):
    offset = State()


# =====================================================
# 🛠 مدیریت پروکسی (ورود مستقیم به لیست)
# =====================================================
@router.message(F.text == "🛠 مدیریت پروکسی")
async def list_proxies(message: Message, state: FSMContext):

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Config)
            .where(Config.type == "proxy")
            .order_by(Config.id.desc())
        )
        proxies = result.scalars().all()

    if not proxies:
        await message.answer("❌ هیچ پروکسی ثبت نشده.")
        return

    await state.update_data(
        proxies=[{
            "id": p.id,
            "title": p.title,
            "value": p.value,
            "active": p.is_active
        } for p in proxies],
        offset=0
    )

    await send_proxy_page(message, state)


# =====================================================
# ➡️ صفحه بعد
# =====================================================
@router.callback_query(F.data == "next_admin_configs")
async def next_proxy_page(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    if not data:
        await callback.answer("اطلاعات منقضی شده.", show_alert=True)
        return

    await callback.answer()
    await send_proxy_page(callback.message, state)


# =====================================================
# 📄 ارسال صفحه
# =====================================================
async def send_proxy_page(message, state: FSMContext):

    data = await state.get_data()
    proxies = data.get("proxies", [])
    offset = data.get("offset", 0)

    if not proxies:
        await message.answer("❌ داده‌ای موجود نیست.")
        await state.clear()
        return

    next_offset = offset + PROXIES_PER_PAGE
    page = proxies[offset:next_offset]

    if not page:
        await message.answer("❌ مورد بیشتری وجود ندارد.")
        await state.clear()
        return

    await state.update_data(offset=next_offset)

    for proxy in page:

        status = "🟢 فعال" if proxy["active"] else "🔴 غیرفعال"

        text = (
            f"📦 <b>پروکسی #{proxy['id']}</b>\n\n"
            f"📝 عنوان: {proxy['title']}\n"
            f"📊 وضعیت: {status}\n\n"
            f"{proxy['value']}"
        )

        await message.answer(
            text,
            reply_markup=config_manage_keyboard(
                proxy["id"],
                proxy["active"]
            )
        )

    if next_offset < len(proxies):
        await message.answer(
            "برای مشاهده ادامه:",
            reply_markup=config_pagination_keyboard()
        )
    else:
        await state.clear()


# =====================================================
# 🔄 تغییر وضعیت پروکسی (بدون تغییر منطق)
# =====================================================
@router.callback_query(F.data.startswith("toggle_config:"))
async def toggle_proxy(callback: CallbackQuery):

    proxy_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Config).where(
                Config.id == proxy_id,
                Config.type == "proxy"
            )
        )
        proxy = result.scalar_one_or_none()

        if not proxy:
            await callback.answer("پروکسی یافت نشد.", show_alert=True)
            return

        proxy.is_active = not proxy.is_active
        await session.commit()

        status = "🟢 فعال شد" if proxy.is_active else "🔴 غیرفعال شد"

        text = (
            f"📦 <b>پروکسی #{proxy.id}</b>\n\n"
            f"📝 عنوان: {proxy.title}\n"
            f"📊 وضعیت: {'🟢 فعال' if proxy.is_active else '🔴 غیرفعال'}\n\n"
            f"{proxy.value}"
        )

        await callback.message.edit_text(
            text,
            reply_markup=config_manage_keyboard(
                proxy.id,
                proxy.is_active
            )
        )

    await callback.answer(f"✅ {status}")


# =====================================================
# ❌ حذف پروکسی (بدون تغییر منطق)
# =====================================================
@router.callback_query(F.data.startswith("delete_config:"))
async def delete_proxy(callback: CallbackQuery):

    proxy_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Config).where(
                Config.id == proxy_id,
                Config.type == "proxy"
            )
        )
        proxy = result.scalar_one_or_none()

        if not proxy:
            await callback.answer("پروکسی یافت نشد.", show_alert=True)
            return

        await session.delete(proxy)
        await session.commit()

    await callback.message.edit_text(
        "✅ پروکسی با موفقیت حذف شد."
    )

    await callback.answer()