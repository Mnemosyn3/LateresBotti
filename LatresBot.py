import logging
from salaisuus import *

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler



import sqlite3


con = sqlite3.connect("kurssit.db")

cur = con.cursor()

res = cur.execute("CREATE TABLE IF NOT EXISTS chats (chat_id INT);")




application = ApplicationBuilder().token(secretToken).build()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, biip boop")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Commands:\n/start\n/tilaa tilaa kurssit\n/help")

async def tilaa(update: Update,context: ContextTypes.DEFAULT_TYPE):
    
    print("test")
    cur.execute("INSERT INTO chats (chat_id) VALUES(?)",(update.effective_chat.id,))
    con.commit()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Saat nyt tietoa koulutuksista.")
    
    

async def sendInfo(context: ContextTypes.DEFAULT_TYPE):
    
    res = cur.execute("SELECT chat_id FROM chats")
    iterable_list = res.fetchall()
    print(iterable_list)
    for i in iterable_list:

        await application.bot.sendMessage(chat_id=i[0], text="pöö")
        

def main():
    
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tilaa", tilaa))
   
    application.run_polling()

application.job_queue.run_repeating(sendInfo,10)
if __name__ == '__main__':
    main()


