import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# កំណត់តាម Environment Variables (កុំដាក់ Token ឬ ID ផ្ទាល់ក្នុងកូដ Public)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))
VIP_INVITE_LINK = os.environ.get("VIP_INVITE_LINK", "https://t.me/+RqTiOTj0znwwZjNl").strip()
QR_IMAGE_PATH = os.environ.get("QR_IMAGE_PATH", "qr.jpg").strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    caption = (
        "👋 សូមស្វាគមន៍មកកាន់ **ប្រជុំរឿង VIP Bot**!\n\n"
        "📸 សូមផ្ញើរូបភាពវិក្កយបត្រ (Slip) នៃការទូទាត់ប្រាក់របស់អ្នកមកទីនេះ "
        "ដើម្បីស្នើសុំចូលឆានែល VIP។"
    )
    if QR_IMAGE_PATH and os.path.exists(QR_IMAGE_PATH):
        with open(QR_IMAGE_PATH, "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=caption, parse_mode="Markdown")
    else:
        await update.message.reply_text(caption, parse_mode="Markdown")


async def handle_slip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user = update.effective_user
    if not message or not user:
        return

    # ឆ្លើយតបទៅកាន់អ្នកប្រើប្រាស់ភ្លាមៗ
    await message.reply_text(
        "✅ បានទទួលវិក្កយបត្រ (Slip) របស់អ្នកហើយ!\n"
        "សូមរង់ចាំ Admin ពិនិត្យ និងផ្ទៀងផ្ទាត់បន្តិច។"
    )

    if not ADMIN_CHAT_ID:
        logger.warning("ADMIN_CHAT_ID is not set. Cannot forward VIP request.")
        return

    full_name = user.full_name or user.first_name or "User"
    username_text = f"@{user.username}" if user.username else "គ្មាន"
    admin_caption = (
        "📩 **មានការស្នើសុំចូល VIP ថ្មី!**\n"
        f"- ឈ្មោះ: {full_name}\n"
        f"- Username: {username_text}\n"
        f"- User ID: `{user.id}`\n\n"
        "STATUS: ⏳ រង់ចាំពិនិត្យ (Pending)"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ អនុម័ត (Approve)", callback_data=f"approve:{user.id}"),
                InlineKeyboardButton("❌ បដិសេធ (Reject)", callback_data=f"reject:{user.id}"),
            ]
        ]
    )

    if message.photo:
        file_id = message.photo[-1].file_id
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=file_id,
            caption=admin_caption,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
    elif message.document:
        await context.bot.send_document(
            chat_id=ADMIN_CHAT_ID,
            document=message.document.file_id,
            caption=admin_caption,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )


async def handle_admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return

    await query.answer()

    if update.effective_user and update.effective_user.id != ADMIN_CHAT_ID:
        await query.answer("អ្នកមិនមែនជា Admin ទេ។", show_alert=True)
        return

    action, target_id_str = query.data.split(":", 1)
    target_user_id = int(target_id_str)

    base_caption = query.message.caption or ""
    if "STATUS:" in base_caption:
        prefix = base_caption.split("STATUS:")[0]
    else:
        prefix = base_caption + "\n\n"

    if action == "approve":
        new_caption = f"{prefix}STATUS: ✅ បានអនុម័តរួចរាល់ (Approved)"
        if query.message.photo:
            await query.edit_message_caption(caption=new_caption, parse_mode="Markdown")
        else:
            await query.edit_message_text(text=new_caption, parse_mode="Markdown")

        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "🎉 **ការទូទាត់ប្រាក់របស់អ្នកត្រូវបាន Admin ផ្ទៀងផ្ទាត់ និងអនុម័តជោគជ័យ!**\n\n"
                f"សូមចុចទីនេះដើម្បីចូលឆានែល VIP:\n{VIP_INVITE_LINK}"
            ),
            parse_mode="Markdown",
        )
    elif action == "reject":
        new_caption = f"{prefix}STATUS: ❌ បានបដិសេធ (Rejected)"
        if query.message.photo:
            await query.edit_message_caption(caption=new_caption, parse_mode="Markdown")
        else:
            await query.edit_message_text(text=new_caption, parse_mode="Markdown")

        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "❌ **សំណើចូល VIP របស់អ្នកត្រូវបានបដិសេធ។**\n"
                "សូមពិនិត្យវិក្កយបត្រម្តងទៀត ឬទាក់ទង Admin ដើម្បីសួរព័ត៌មានបន្ថែម។"
            ),
            parse_mode="Markdown",
        )


def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is missing! Set BOT_TOKEN before running.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_slip))
    app.add_handler(CallbackQueryHandler(handle_admin_decision, pattern=r"^(approve|reject):\d+$"))

    logger.info("Bot is starting with polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
