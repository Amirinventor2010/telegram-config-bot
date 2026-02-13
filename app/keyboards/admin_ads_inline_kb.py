from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def ad_manage_keyboard(ad_id: int, is_active: bool):
    status_text = "🔴 غیرفعال کن" if is_active else "🟢 فعال کن"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=status_text,
                    callback_data=f"toggle_ad:{ad_id}"
                ),
                InlineKeyboardButton(
                    text="❌ حذف",
                    callback_data=f"delete_ad:{ad_id}"
                ),
            ]
        ]
    )
