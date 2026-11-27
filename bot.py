import asyncio
import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
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


def get_env_config() -> tuple[str, int, int]:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_raw = os.getenv("ADMIN_CHAT_ID", "").strip()
    vip_chat_raw = os.getenv("VIP_CHAT_ID", "").strip()

    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is missing! Set BOT_TOKEN before running.")
    if not admin_raw:
        raise ValueError("ADMIN_CHAT_ID environment variable is missing! Set ADMIN_CHAT_ID before running.")
    if not vip_chat_raw:
        raise ValueError(
            "VIP_CHAT_ID environment variable is missing! "
            "Set VIP_CHAT_ID (e.g. -100...) so each approved user gets a unique invite link."
        )

    try:
        admin_chat_id = int(admin_raw)
    except ValueError as exc:
        raise ValueError("ADMIN_CHAT_ID must be a valid integer Telegram chat/user ID.") from exc

    try:
        vip_chat_id = int(vip_chat_raw)
    except ValueError as exc:
        raise ValueError(
            "VIP_CHAT_ID must be a valid integer Telegram channel/group ID (e.g. -100...)."
        ) from exc

    return bot_token, admin_chat_id, vip_chat_id


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    welcome_text = (
        "សួស្តី! ស្វាគមន៍មកកាន់ ប្រជុំរឿង VIP 🎬✨\n\n"
        "បន្ទាប់ពីបង់ប្រាក់រួច សូមផ្ញើរូបភាពវិក្កយបត្រ (Slip) ត្រឡប់មកទីនេះ "
        "ដើម្បីឱ្យ Admin ពិនិត្យ និងផ្តល់ Link ចូល VIP ជូនអ្នក។\n\n"
        "ប្រសិនបើអ្នកធ្លាប់ចូលរួចហើយចាកចេញ ហើយចង់ចូលម្តងទៀត "
        "អ្នកអាចបង់ប្រាក់ និងផ្ញើ Slip ថ្មីមកទីនេះជាលើកទី 2 បានជាធម្មតា។\n\n"
        "Admin សូមអភ័យទោសទុកជាមុនចំពោះការចំណាយនេះ "
        "ហើយសង្ឃឹមថាអ្នកទាំងអស់គ្នានឹងយោគយល់។ "
        "Admin ក៏ចង់ផុសជូនមើល Free ដូចមុនដែរ "
        "តែរឿងខ្លះជាប់ Copyright ផុសជាសាធារណៈមិនបាន "
        "ទើបបង្កើត Channel VIP នេះឡើង។\n\n"
        "អរគុណខ្លាំងមែនទែនសម្រាប់ការគាំទ្រជានិច្ច! 🙏❤️"
    )
    if os.path.exists("qr.jpg"):
        with open("qr.jpg", "rb") as qr_file:
            await update.message.reply_photo(photo=qr_file, caption=welcome_text)
    else:
        await update.message.reply_text(welcome_text)


async def handle_slip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.photo or not update.effective_user:
        return

    _, admin_chat_id, _ = get_env_config()
    user = update.effective_user
    photo_file_id = update.message.photo[-1].file_id
    caption_text = update.message.caption or "(គ្មានចំណារ)"

    username_display = f"@{user.username}" if user.username else "(គ្មាន username)"
    admin_caption = (
        "🧾 មានសំណើ VIP ថ្មី (Slip Photo)\n"
        f"• ឈ្មោះ: {user.full_name}\n"
        f"• Username: {username_display}\n"
        f"• User ID: {user.id}\n"
        f"• ចំណារ: {caption_text}"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve:{user.id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject:{user.id}"),
            ]
        ]
    )

    await context.bot.send_photo(
        chat_id=admin_chat_id,
        photo=photo_file_id,
        caption=admin_caption,
        reply_markup=keyboard,
    )

    await update.message.reply_text(
        "✅ បានទទួលវិក្កយបត្រ (Slip) របស់អ្នកហើយ! សូមរង់ចាំ Admin ពិនិត្យ និងផ្ទៀងផ្ទាត់បន្តិច។"
    )


async def handle_other_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(
        "សូមផ្ញើរូបភាពវិក្កយបត្រ (Slip) ការបង់ប្រាក់ ឬវាយ /start ដើម្បីមើលព័ត៌មានណែនាំ។"
    )


async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return

    _, admin_chat_id, vip_chat_id = get_env_config()
    if query.from_user.id != admin_chat_id:
        await query.answer("អ្នកមិនមែនជា Admin ទេ។", show_alert=True)
        return

    parts = query.data.split(":", maxsplit=1)
    if len(parts) != 2:
        await query.answer("ទិន្នន័យប៊ូតុងមិនត្រឹមត្រូវ។", show_alert=True)
        return

    action, target_id_raw = parts
    try:
        target_user_id = int(target_id_raw)
    except ValueError:
        await query.answer("User ID មិនត្រឹមត្រូវ។", show_alert=True)
        return

    base_caption = query.message.caption or "" if query.message else ""

    if action == "approve":
        try:
            await context.bot.unban_chat_member(
                chat_id=vip_chat_id,
                user_id=target_user_id,
                only_if_banned=True,
            )
        except TelegramError as exc:
            logger.warning("unban_chat_member skipped/failed for %s: %s", target_user_id, exc)

        approved_users = context.bot_data.setdefault("approved_users", set())
        approved_users.add(target_user_id)

        invite = await context.bot.create_chat_invite_link(
            chat_id=vip_chat_id,
            creates_join_request=True,
            name=f"VIP-{target_user_id}",
        )
        invite_link_to_send = invite.invite_link

        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "🎉 សំណើ VIP របស់អ្នកត្រូវបានអនុម័ត!\n"
                "សូមចុច Link ខាងក្រោម ហើយចុច Request to Join — Bot នឹងអនុម័តឱ្យចូលដោយស្វ័យប្រវត្តិ៖\n"
                f"{invite_link_to_send}"
            ),
        )
        new_caption = f"{base_caption}\n\n✅ ស្ថានភាព៖ បានអនុម័ត (បង្កើត Join Request Link រួចរាល់)"
        if query.message:
            await query.message.edit_caption(caption=new_caption, reply_markup=None)
        await query.answer("បានបង្កើត Link និងផ្ញើទៅ User រួចរាល់។")

    elif action == "reject":
        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "❌ សូមអភ័យទោស Slip របស់អ្នកមិនត្រូវបានអនុម័តទេ។ "
                "សូមពិនិត្យការទូទាត់ ឬផ្ញើ Slip ម្តងទៀត។"
            ),
        )
        new_caption = f"{base_caption}\n\n❌ ស្ថានភាព៖ បានបដិសេធ (Rejected)"
        if query.message:
            await query.message.edit_caption(caption=new_caption, reply_markup=None)
        await query.answer("បានបដិសេធសំណើ។")


async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    join_req = update.chat_join_request
    if not join_req or not join_req.from_user:
        return

    _, _, vip_chat_id = get_env_config()
    if join_req.chat.id != vip_chat_id:
        return

    user_id = join_req.from_user.id
    approved_users = context.bot_data.get("approved_users", set())

    if user_id in approved_users:
        try:
            await join_req.approve()
            approved_users.discard(user_id)
            logger.info("Auto-approved join request for user %s", user_id)
        except TelegramError as exc:
            logger.error("Failed to approve join request for %s: %s", user_id, exc)


def main() -> None:
    bot_token, _, _ = get_env_config()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_slip_photo))
    app.add_handler(MessageHandler(~filters.PHOTO & ~filters.COMMAND, handle_other_message))
    app.add_handler(CallbackQueryHandler(handle_admin_callback))
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    logger.info("Starting Telegram VIP Bot polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
