from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.database.session import AsyncSessionLocal
from app.database.models import Config

router = Router()


# =====================================================
# 🧠 FSM State
# =====================================================
class AddAppState(StatesGroup):
    waiting_for_file = State()


# =====================================================
# 📁 شروع افزودن فایل اپلیکیشن
# =====================================================
@router.message(F.text == "📁 افزودن فایل اپلیکیشن")
async def start_add_app(message: Message, state: FSMContext):

    await message.answer(
        "📤 لطفاً فایل اپلیکیشن را ارسال کنید (APK / ZIP / هر فایل دیگر)."
    )

    await state.set_state(AddAppState.waiting_for_file)


# =====================================================
# 📥 دریافت فایل و ذخیره
# =====================================================
@router.message(AddAppState.waiting_for_file)
async def save_app_file(message: Message, state: FSMContext):

    if not message.document:
        await message.answer("❌ لطفاً فقط فایل ارسال کنید.")
        return

    file_id = message.document.file_id
    file_name = message.document.file_name

    async with AsyncSessionLocal() as session:

        new_app = Config(
            type="app",
            title=file_name,
            value=file_id,
            is_active=True
        )

        session.add(new_app)
        await session.commit()

    await message.answer("✅ فایل اپلیکیشن با موفقیت اضافه شد.")

    await state.clear()
