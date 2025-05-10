import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 加载 .env 文件中的环境变量
load_dotenv()

# 获取 BOT_TOKEN 和 OWNER_ID 环境变量
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

# 确保 BOT_TOKEN 和 OWNER_ID 环境变量已经设置
if not BOT_TOKEN or not OWNER_ID:
    raise RuntimeError("请设置 BOT_TOKEN 和 OWNER_ID 环境变量")

# 将 OWNER_ID 转换为整数
OWNER_ID = int(OWNER_ID)

# 用来存储用户消息和回复的映射关系
user_map = {}

# 处理用户发送的消息
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    if message:
        forwarded = await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"[来自 {user.first_name} ({user.id}) 的消息]:\n{message.text}"
        )
        user_map[forwarded.message_id] = user.id

# 处理 Bot 主人的回复消息
async def handle_owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.reply_to_message:
        reply_to = update.message.reply_to_message
        original_user_id = user_map.get(reply_to.message_id)
        if original_user_id:
            await context.bot.send_message(
                chat_id=original_user_id,
                text=f"[来自Bot主人的回复]:\n{update.message.text}"
            )

# 设置 Telegram Bot 应用
app = ApplicationBuilder().token(BOT_TOKEN).build()

# 添加消息处理器
app.add_handler(MessageHandler(filters.TEXT & (~filters.User(OWNER_ID)), handle_user_message))
app.add_handler(MessageHandler(filters.TEXT & filters.User(OWNER_ID), handle_owner_reply))

# 启动机器人
app.run_polling()
