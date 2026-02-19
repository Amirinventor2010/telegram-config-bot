import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # =========================
    # 🔐 Core
    # =========================
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_NAME = os.getenv("BOT_NAME", "FREECONFIG")

    # =========================
    # 👑 Multiple Admin Support
    # =========================
    # لیست ادمین‌ها از env به صورت: 111111,222222,333333
    ADMIN_IDS = [
        int(admin_id.strip())
        for admin_id in os.getenv("ADMIN_IDS", "").split(",")
        if admin_id.strip().isdigit()
    ]

    # اولین ادمین = سوپر ادمین
    @property
    def SUPER_ADMIN_ID(self) -> int:
        return self.ADMIN_IDS[0] if self.ADMIN_IDS else 0

    # برای سازگاری با کدهای قدیمی
    @property
    def ADMIN_ID(self) -> int:
        return self.SUPER_ADMIN_ID

    # =========================
    # 🏷 Config Tag Format
    # =========================
    CONFIG_TAG_FORMAT = os.getenv(
        "CONFIG_TAG_FORMAT",
        "{bot_name}-{number}"
    )

    def build_config_tag(self, number: int) -> str:
        return self.CONFIG_TAG_FORMAT.format(
            bot_name=self.BOT_NAME,
            number=number
        )

    # =========================
    # 🎨 Branding
    # =========================
    BRAND_TITLE = os.getenv(
        "BRAND_TITLE",
        "✨ FREECONFIG"
    )

    BRAND_DESCRIPTION = os.getenv(
        "BRAND_DESCRIPTION",
        "دریافت سریع کانفیگ و پروکسی"
    )

    START_MESSAGE_FOOTER = os.getenv(
        "START_MESSAGE_FOOTER",
        "از منوی زیر سرویس مورد نظر را انتخاب کنید 👇"
    )

    @property
    def WELCOME_TEXT(self):
        """
        متن خوش‌آمدگویی بدون فاصله‌های اضافه
        اگر هر بخش خالی باشد حذف می‌شود
        """
        parts = [
            self.BRAND_TITLE,
            self.BRAND_DESCRIPTION,
            self.START_MESSAGE_FOOTER,
        ]

        # حذف بخش‌های خالی یا فقط شامل فاصله
        cleaned_parts = [
            part.strip()
            for part in parts
            if part and part.strip()
        ]

        return "\n\n".join(cleaned_parts)

    # =========================
    # 🛠 Admin Panel
    # =========================
    ADMIN_PANEL_TITLE_TEMPLATE = os.getenv(
        "ADMIN_PANEL_TITLE",
        "⚙️ پنل مدیریت {bot_name}"
    )

    @property
    def ADMIN_PANEL_TITLE(self):
        return self.ADMIN_PANEL_TITLE_TEMPLATE.format(
            bot_name=self.BOT_NAME
        )

    ADMIN_PANEL_DESCRIPTION = os.getenv(
        "ADMIN_PANEL_DESCRIPTION",
        "مدیریت کامل سرویس‌ها"
    )

    ADMIN_PANEL_FOOTER = os.getenv(
        "ADMIN_PANEL_FOOTER",
        "از منوی زیر گزینه مورد نظر را انتخاب کنید"
    )

    # =========================
    # 📦 Config / Proxy Texts
    # =========================
    NO_CONFIG_TEXT = os.getenv(
        "NO_CONFIG_TEXT",
        "❌ در حال حاضر هیچ کانفیگ فعالی موجود نیست."
    )

    NO_PROXY_TEXT = os.getenv(
        "NO_PROXY_TEXT",
        "❌ در حال حاضر هیچ پروکسی فعالی موجود نیست."
    )

    # =========================
    # 🕒 Timezone
    # =========================
    TIMEZONE = os.getenv(
        "TIMEZONE",
        "Asia/Tehran"
    )

    # =========================
    # 🗄 Database
    # =========================
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")

    @property
    def database_url(self):
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}"
        )

    # =========================
    # 🚀 Redis
    # =========================
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")


settings = Settings()
