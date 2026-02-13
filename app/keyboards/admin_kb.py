from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def admin_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 آمار کاربران"),
                KeyboardButton(text="👥 مدیریت کاربران"),
            ],
            [
                KeyboardButton(text="🗂 مدیریت کانفیگ و پروکسی"),
                KeyboardButton(text="📢 مدیریت تبلیغات"),
            ],
            [
                KeyboardButton(text="🔙 بازگشت به منوی کاربر"),
            ]
        ],
        resize_keyboard=True
    )


def admin_users_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🚫 بن کاربر"),
                KeyboardButton(text="♻️ رفع بن کاربر"),
            ],
            [
                KeyboardButton(text="📢 ارسال همگانی"),
            ],
            [
                KeyboardButton(text="🔙 بازگشت به پنل"),
            ]
        ],
        resize_keyboard=True
    )


def admin_configs_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ افزودن کانفیگ"),
                KeyboardButton(text="🛠 مدیریت کانفیگ"),
            ],
            [
                KeyboardButton(text="➕ افزودن پروکسی"),
                KeyboardButton(text="🛠 مدیریت پروکسی"),
            ],
            [
                KeyboardButton(text="🔙 بازگشت به پنل"),
            ]
        ],
        resize_keyboard=True
    )


def admin_ads_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ افزودن کانال تبلیغاتی"),
                KeyboardButton(text="🛠 مدیریت کانال‌ها"),
            ],
            [
                KeyboardButton(text="🔙 بازگشت به پنل"),
            ]
        ],
        resize_keyboard=True
    )



def admin_add_config_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📡 افزودن V2Ray"),
                KeyboardButton(text="🛰 افزودن NPV"),
            ],
            [
                KeyboardButton(text="🔙 بازگشت به مدیریت"),
            ]
        ],
        resize_keyboard=True
    )


def admin_manage_config_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 لیست کانفیگ‌ها"),
                KeyboardButton(text="❌ حذف کانفیگ"),
            ],
            [
                KeyboardButton(text="🔄 فعال / غیرفعال"),
            ],
            [
                KeyboardButton(text="🔙 بازگشت به مدیریت"),
            ]
        ],
        resize_keyboard=True
    )


def admin_manage_proxy_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 لیست پروکسی‌ها"),
                KeyboardButton(text="❌ حذف پروکسی"),
            ],
            [
                KeyboardButton(text="🔄 فعال / غیرفعال"),
            ],
            [
                KeyboardButton(text="🔙 بازگشت به مدیریت"),
            ]
        ],
        resize_keyboard=True
    )
