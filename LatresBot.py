import logging
from salaisuus import * #salaisuus.py file contains the secret token that botFather provides when creating a bot. It is stored in variable named secretToken. 

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import requests

import json

import sqlite3

from datetime import datetime, timedelta

import asyncio

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
    await update.message.reply_text("""Komennot:
    
/start
/tilaa Tilaa tiedotteen uusista kursseista
/peruTilaus Peru tiedotteen
/help Näyttää tämän viestin""")


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
    
    res1 = cur.execute("""SELECT TapahtumaID,Nimi,Ajankohta FROM courses WHERE notificationSent = 0 """)
    courseList = res1.fetchall()

    res2 = cur.execute("SELECT chat_id FROM chats")
    chatList = res2.fetchall()
    
    for i in courseList:

        for j in chatList:
            r = requests.get("https://koulutuskalenteri.mpk.fi/Koulutuskalenteri?&type=search&id="+str(i[0])+"&culture=")

            page = r.text
            registration =page[716:751]

            message = str(i[1])+"\n"+str(i[2])+"\nIlmoittautuminen: "+registration+"\n\nhttps://koulutuskalenteri.mpk.fi/Koulutuskalenteri/Tutustu-tarkemmin/id/"+str(i[0]) 

            await application.bot.sendMessage(chat_id=j[0], text=message)
        cur.execute("UPDATE courses SET notificationSent = 1 WHERE TapahtumaID =?",(i[0],))
        con.commit()
        


async def getCourses(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.today() + timedelta(days = 180)
    
    
    i = 1
    while(i <= 80):
        nextMonth = today + timedelta(days = 7)
        start = str(today.day)+"."+str(today.month)+"."+str(today.year)
        end = str(nextMonth.day)+"."+str(nextMonth.month)+"."+str(nextMonth.year)
        makeQuery(start,end,"false")
    
        today = today + timedelta(days=7)
        i = i +1
        await asyncio.sleep(2)
    today = datetime.today()
    
    
    


def makeQuery(start,end,online):
    url = "https://koulutuskalenteri.mpk.fi/Koulutuskalenteri?&type=search&format=json&group=&unit=&unit_id=&sub_unit_id=&organizer_unit_id=&target=&coursetype=&keyword_id=&method=&area=&location=&profile=&status=&nature=&culture=&start="+start+"&end="+end+"&q=&top=&only_my_events=false&VerkkoKoulutus="+online+"&lisaysAikaleima=false&nayta_Vain_Ilmo_Auki=false"
    #print(url)
    r = requests.get(url)
    courses = json.loads(r.text)
    for i in courses:
        
        cur.execute("""SELECT 1 FROM courses WHERE TapahtumaID = ?""",(i["TapahtumaID"],))

        if(cur.fetchone() == None):
            print("Adding to database")
            cur.execute("INSERT INTO courses (TapahtumaID,Nimi,Ajankohta,notificationSent) VALUES(?,?,?,0)",(i["TapahtumaID"],i["Nimi"],i["Ajankohta"]))
            con.commit()
 
        

def main():
    
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tilaa", tilaa))
    application.add_handler(CommandHandler("peruTilaus", peruTilaus))
   
    application.run_polling()


application.job_queue.run_repeating(getCourses,3600)
application.job_queue.run_repeating(sendInfo,30)

if __name__ == '__main__':
    main()


