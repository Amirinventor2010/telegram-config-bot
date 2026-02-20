from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# =========================
# 👑 منوی اصلی ادمین
# =========================
def admin_main_keyboard(include_admin_manage: bool = False):
    keyboard = [
        [
            KeyboardButton(text="📊 آمار کاربران"),
            KeyboardButton(text="👥 مدیریت کاربران"),
        ],
        [
            KeyboardButton(text="🗂 مدیریت کانفیگ و پروکسی"),
            KeyboardButton(text="📢 مدیریت تبلیغات"),
        ],
    ]

    if include_admin_manage:
        keyboard.append(
            [KeyboardButton(text="👑 مدیریت ادمین‌ها")]
        )

    keyboard.append(
        [KeyboardButton(text="🔙 بازگشت به منوی کاربر")]
    )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


# =========================
# 👑 منوی مدیریت ادمین‌ها
# =========================
def admin_manage_admins_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ افزودن ادمین"),
                KeyboardButton(text="➖ حذف ادمین"),
            ],
            [
                KeyboardButton(text="🔙 بازگشت به پنل"),
            ]
        ],
        resize_keyboard=True
    )


# =========================
# 👥 مدیریت کاربران
# =========================
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


# =========================
# 🗂 مدیریت کانفیگ و پروکسی
# =========================
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


# =========================
# 📢 مدیریت تبلیغات
# =========================
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


# =========================
# ➕ افزودن کانفیگ
# =========================
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


# =========================
# 🛠 مدیریت کانفیگ (فقط انتخاب نوع)
# =========================
def admin_manage_config_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📡 مدیریت کانفیگ V2Ray"),
                KeyboardButton(text="🛰 مدیریت کانفیگ NPV"),
            ],
            [
                KeyboardButton(text="🔙 بازگشت به مدیریت"),
            ]
        ],
        resize_keyboard=True
    )
