from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.database.models import AdChannel
from app.keyboards.admin_ads_inline_kb import ad_manage_keyboard

router = Router()


# =====================================================
# 🧠 State افزودن کانال
# =====================================================
class AddAdState(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_invite_link = State()
    waiting_for_type = State()


# =====================================================
# 📋 لیست کانال‌ها
# =====================================================
@router.message(F.text == "🛠 مدیریت کانال‌ها")
async def list_ads(message: Message):

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AdChannel).order_by(AdChannel.id.desc())
        )
        ads = result.scalars().all()

    if not ads:
        await message.answer("❌ هیچ کانال تبلیغاتی ثبت نشده است.\n\nاز گزینه افزودن استفاده کنید.")
        return

    for ad in ads:
        text = (
            f"🆔 ID: <code>{ad.id}</code>\n"
            f"📢 کانال: {ad.channel_id}\n"
            f"🔗 لینک: {ad.invite_link}\n"
            f"📂 نوع: {ad.ad_type}\n"
            f"📊 وضعیت: {'🟢 فعال' if ad.is_active else '🔴 غیرفعال'}"
        )

        await message.answer(
            text,
            reply_markup=ad_manage_keyboard(ad.id, ad.is_active)
        )


# =====================================================
# ➕ شروع افزودن کانال
# =====================================================
@router.message(F.text == "➕ افزودن کانال تبلیغاتی")
async def start_add_ad(message: Message, state: FSMContext):

    await state.clear()
    await state.set_state(AddAdState.waiting_for_channel_id)

    await message.answer(
        "📢 آیدی کانال را ارسال کنید:\n\n"
        "مثال: @mychannel"
    )


@router.message(AddAdState.waiting_for_channel_id)
async def get_channel_id(message: Message, state: FSMContext):

    channel_id = message.text.strip()

    if not channel_id.startswith("@"):
        await message.answer("❌ آیدی کانال باید با @ شروع شود.")
        return

    await state.update_data(channel_id=channel_id)
    await state.set_state(AddAdState.waiting_for_invite_link)

    await message.answer("🔗 لینک دعوت را ارسال کنید:")


@router.message(AddAdState.waiting_for_invite_link)
async def get_invite_link(message: Message, state: FSMContext):

    invite_link = message.text.strip()

    if not invite_link.startswith("http"):
        await message.answer("❌ لینک معتبر نیست.")
        return

    await state.update_data(invite_link=invite_link)
    await state.set_state(AddAdState.waiting_for_type)

    await message.answer("📂 نوع تبلیغ را ارسال کنید:\n\njoin یا view")


@router.message(AddAdState.waiting_for_type)
async def get_ad_type(message: Message, state: FSMContext):

    ad_type = message.text.strip().lower()

    if ad_type not in ["join", "view"]:
        await message.answer("❌ فقط join یا view مجاز است.")
        return

    data = await state.get_data()

    async with AsyncSessionLocal() as session:

        # جلوگیری از ثبت تکراری
        existing = await session.execute(
            select(AdChannel).where(
                AdChannel.channel_id == data["channel_id"]
            )
        )
        if existing.scalar_one_or_none():
            await message.answer("❌ این کانال قبلاً ثبت شده است.")
            await state.clear()
            return

        ad = AdChannel(
            channel_id=data["channel_id"],
            invite_link=data["invite_link"],
            ad_type=ad_type,
            is_active=True
        )

        session.add(ad)
        await session.commit()

    await state.clear()
    await message.answer("✅ کانال تبلیغاتی ثبت شد.")


# =====================================================
# ❌ حذف
# =====================================================
@router.callback_query(F.data.startswith("delete_ad:"))
async def delete_ad(callback: CallbackQuery):

    await callback.answer()

    ad_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AdChannel).where(AdChannel.id == ad_id)
        )
        ad = result.scalar_one_or_none()

        if not ad:
            await callback.answer("یافت نشد.", show_alert=True)
            return

        await session.delete(ad)
        await session.commit()

    await callback.message.edit_text("✅ حذف شد.")


# =====================================================
# 🔄 تغییر وضعیت
# =====================================================
@router.callback_query(F.data.startswith("toggle_ad:"))
async def toggle_ad(callback: CallbackQuery):

    await callback.answer()

    ad_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AdChannel).where(AdChannel.id == ad_id)
        )
        ad = result.scalar_one_or_none()

        if not ad:
            await callback.answer("یافت نشد.", show_alert=True)
            return

        ad.is_active = not ad.is_active
        await session.commit()

        text = (
            f"🆔 ID: <code>{ad.id}</code>\n"
            f"📢 کانال: {ad.channel_id}\n"
            f"🔗 لینک: {ad.invite_link}\n"
            f"📂 نوع: {ad.ad_type}\n"
            f"📊 وضعیت: {'🟢 فعال' if ad.is_active else '🔴 غیرفعال'}"
        )

        await callback.message.edit_text(
            text,
            reply_markup=ad_manage_keyboard(ad.id, ad.is_active)
        )
