import logging
from salaisuus import *

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import requests
import json

import sqlite3


con = sqlite3.connect("kurssit.db")

cur = con.cursor()

res = cur.execute("CREATE TABLE IF NOT EXISTS chats (chat_id INT);")

res = cur.execute("CREATE TABLE IF NOT EXISTS courses (TapahtumaID INT,Nimi,Ajankohta,notificationSent );")



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

    cur.execute("""SELECT 1 FROM chats WHERE chat_id = ?""",(update.effective_chat.id,))

    if(cur.fetchone() == None):

        cur.execute("INSERT INTO chats (chat_id) VALUES(?)",(update.effective_chat.id,))
        con.commit()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Saat nyt tietoa koulutuksista.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Olet jo tilannut koulutustiedotteen.")


async def peruTilaus(update: Update,context: ContextTypes.DEFAULT_TYPE):

    cur.execute("""SELECT 1 FROM chats WHERE chat_id = ?""",(update.effective_chat.id,))

    if(cur.fetchone() == None):

       await context.bot.send_message(chat_id=update.effective_chat.id, text="Et ole tilannut koulutustiedotetta.")   
    else:
        cur.execute("DELETE FROM chats WHERE chat_id = ?",(update.effective_chat.id,))
        con.commit()

        await context.bot.send_message(chat_id=update.effective_chat.id, text="Tilauksesi on peruttu.")   

async def sendInfo(context: ContextTypes.DEFAULT_TYPE):
    
    res = cur.execute("SELECT chat_id FROM chats")
    iterable_list = res.fetchall()
    print(iterable_list)
    for i in iterable_list:

        await application.bot.sendMessage(chat_id=i[0], text="pöö")

async def getCourses(context: ContextTypes.DEFAULT_TYPE):
    url = "https://koulutuskalenteri.mpk.fi/Koulutuskalenteri?&type=search&format=json&group=&unit=&unit_id=&sub_unit_id=&organizer_unit_id=&target=&coursetype=&keyword_id=&method=&area=&location=&profile=&status=&nature=&culture=&start=24.02.2023&end=12.09.2023&q=&top=&only_my_events=false&VerkkoKoulutus=false&lisaysAikaleima=false&nayta_Vain_Ilmo_Auki=false"
    
    r = requests.get(url)

        

def main():
    
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tilaa", tilaa))
    application.add_handler(CommandHandler("peruTilaus", peruTilaus))
   
    application.run_polling()

application.job_queue.run_repeating(sendInfo,10)
application.job_queue.run_repeating(getCourses,10)

if __name__ == '__main__':
    main()


