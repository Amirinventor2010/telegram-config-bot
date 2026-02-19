from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.database.models import Config
from app.config import settings


router = Router()


# =========================
# 🧠 Pagination State
# =========================
class ProxyPagination(StatesGroup):
    offset = State()


PROXIES_PER_PAGE = 5


# =========================
# 🌐 دریافت پروکسی
# =========================
@router.message(F.text == "🌐 دریافت پروکسی")
async def start_get_proxies(message: Message, state: FSMContext):

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Config)
            .where(
                Config.type == "proxy",
                Config.is_active == True
            )
            .order_by(Config.id.desc())
        )

        proxies = result.scalars().all()

    if not proxies:
        await message.answer(settings.NO_PROXY_TEXT)
        return

    await state.update_data(
        proxies=[p.value for p in proxies],
        offset=0
    )

    await send_proxies_page(message, state)


# =========================
# ➡️ صفحه بعدی
# =========================
@router.callback_query(F.data == "next_proxies")
async def next_proxies(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await send_proxies_page(callback.message, state, edit=True)


# =========================
# 📄 ارسال صفحه
# =========================
async def send_proxies_page(message: Message, state: FSMContext, edit=False):

    data = await state.get_data()
    proxies = data.get("proxies", [])
    offset = data.get("offset", 0)

    next_offset = offset + PROXIES_PER_PAGE
    page = proxies[offset:next_offset]

    if not page:
        text = "❌ پروکسی بیشتری موجود نیست."
        if edit:
            await message.edit_text(text)
        else:
            await message.answer(text)
        await state.clear()
        return

    text = f"🌐 <b>{settings.BOT_NAME}</b> — لیست پروکسی‌ها\n\n"

    for idx, proxy in enumerate(page, start=offset + 1):
        text += "━━━━━━━━━━━━━━\n"
        text += f"🔹 پروکسی {idx}\n"
        text += f"{proxy}\n\n"   # ✅ بدون <code>

    await state.update_data(offset=next_offset)

    if edit:
        await message.edit_text(
            text,
            reply_markup=_proxy_pagination_keyboard()
        )
    else:
        await message.answer(
            text,
            reply_markup=_proxy_pagination_keyboard()
        )


# =========================
# 🔘 کیبورد اختصاصی پروکسی
# =========================
def _proxy_pagination_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➡️ دریافت پروکسی بعدی",
                    callback_data="next_proxies"
                )
            ]
        ]
    )
