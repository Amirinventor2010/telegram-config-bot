from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# =========================
# 👤 منوی اصلی کاربر
# =========================
def user_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📥 دریافت کانفیگ"),
            ],
            [
                KeyboardButton(text="🌐 دریافت پروکسی"),
            ]
        ],
        resize_keyboard=True
    )


# =========================
# 📥 زیرمنوی دریافت کانفیگ
# =========================
def config_submenu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📡 کانفیگ V2Ray"),
                KeyboardButton(text="🛰 کانفیگ NPV"),
            ],
            [
                KeyboardButton(text="🔙 بازگشت"),
            ]
        ],
        resize_keyboard=True
    )
