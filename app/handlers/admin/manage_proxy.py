from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, delete

from app.database.session import AsyncSessionLocal
from app.database.models import Config
from app.keyboards.admin_config_inline_kb import config_manage_keyboard



router = Router()


# =====================================================
# 📋 لیست پروکسی‌ها
# =====================================================
@router.message(F.text == "📋 لیست پروکسی‌ها")
async def list_proxies(message: Message):

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

    for proxy in proxies:

        status = "🟢 فعال" if proxy.is_active else "🔴 غیرفعال"

        text = (
            f"📦 <b>پروکسی #{proxy.id}</b>\n\n"
            f"📝 عنوان: {proxy.title}\n"
            f"📊 وضعیت: {status}\n"
        )

        await message.answer(
            text,
            reply_markup=config_manage_keyboard(
                proxy.id,
                proxy.is_active
            )
        )


# =====================================================
# 🔄 تغییر وضعیت پروکسی
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
            f"📊 وضعیت: {'🟢 فعال' if proxy.is_active else '🔴 غیرفعال'}\n"
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
# ❌ حذف پروکسی
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
