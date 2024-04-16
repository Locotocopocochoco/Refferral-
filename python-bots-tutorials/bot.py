import telebot
from resources import Resources
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import time
import re

bot = telebot.TeleBot('your botfather token')
ADMIN_USER_ID = 5937299779
ref_bonus = Resources('global', 'ref_bonus')
currency = Resources('global', 'currency')
bonus_amount = Resources('global', 'bonus_amount')
min_with = Resources('global','min_with').value()
max_with = Resources('global','max_with').value()

required_channels = ['@refdemobotcheck','@karancoder']
payment_channel = "@refdemobotcheck"

def is_member_of_channel(user_id):
    for channel in required_channels:
        status = bot.get_chat_member(channel, user_id).status
        if status not in ['member', 'administrator', 'creator']:
            return False
    return True

markup = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton("💲 Balance")
button2 = KeyboardButton("🔗 Ref Stats")
button3 = KeyboardButton("📤 Withdraw")
button4 = KeyboardButton("🥳 Earn More")
button5 = KeyboardButton("🎁 Bonus")        
markup.add(button1)
markup.add(button2, button3)
markup.add(button4, button5)

def menu(message):
    bot.send_message(
        message.from_user.id,
        "🏡 Home",
        reply_markup=markup
    )

back = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton("✘ Cancel")
back.add(button)
    
def cancel(user_id):
    bot.send_message(user_id,
                 "Operation successfully canceled.",
                 reply_markup=markup)
    
    
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.chat.id
    ref_by = message.text.split()[1] if len(message.text.split()) > 1 and message.text.split()[1].isdigit() else None
    
    referred = Resources(user_id,"ref_by")
    refer = referred.get_property("ref_by")
    
    if ref_by and int(ref_by) != int(user_id) and refer == None:
        bot.send_message(user_id,ref_by)
        referred.set_property('ref_by',ref_by)
        referred.set_property('referred',0)
        # bot.send_message(ref_by, f"You referred {message.chat.first_name} and earned {ref_bonus} coins.")
    
    if not is_member_of_channel(user_id):
        inline_markup = InlineKeyboardMarkup()
        for channel in required_channels:
            channel_link = f"https://t.me/{channel.replace('@', '')}"
            inline_button = InlineKeyboardButton(f"Join {channel}", url=channel_link)
            inline_markup.add(inline_button)

        bot.send_message(
            user_id,
            "💡 You Must Join Our All Channels To Get Payment",
            parse_mode='HTML',
            reply_markup=inline_markup
        )

        reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = KeyboardButton("✅ Joined")
        reply_markup.add(start_button)

        bot.send_message(
            user_id,
            "After Join All Channels Click the ✅ Joined Button",
            reply_markup=reply_markup
        )
        return
    refby = referred.get_property("ref_by")
    if refby != None and referred.get_property("referred") == 0:
        balance = Resources(refby,"balance")
        bot.send_message(refby, f"*{message.from_user.first_name}* verified, *+{ref_bonus.value()}* {currency.value()}.",parse_mode="markdown")
        balance.add(ref_bonus.value())
        referred.set_property('referred',1)

    menu(message)

# user balance command code
@bot.message_handler(func=lambda message: message.text == "✅ Joined")
def joined(message):
    send_welcome(message)

@bot.message_handler(func=lambda message: message.text == "💲 Balance")
def balance_command(message):    
    try:
        user_id = message.from_user.id
        balance = Resources(user_id, 'balance')
        msg = f"<b>💵 Your Balance:</b> {balance.value():.4f} {currency.value()}"
        bot.send_message(user_id, msg, parse_mode='html')
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        bot.send_message(user_id, error_message, parse_mode='html')
        bot.send_message(ADMIN_USER_ID, error_message, parse_mode='html')


@bot.message_handler(func=lambda message: message.text == "🎁 Bonus")
def bonus_command(message):
    user_id = message.from_user.id
    balance = Resources(user_id, 'balance')
    bonus_cooldown_seconds = 3600

    try:
        current_time = time.time()
        last_claim_time = balance.get_property('last_claim_time') or 0

        if current_time - last_claim_time >= bonus_cooldown_seconds:
            balance.add(bonus_amount.value())
            balance.set_property('last_claim_time', current_time)
            bot.reply_to(message, f"Congratulations! You claimed a bonus of {bonus_amount.value()}. Added to your balance.")
        else:
            remaining_seconds = int(bonus_cooldown_seconds - (current_time - last_claim_time))
            hours, remainder = divmod(remaining_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            bot.reply_to(
                message,
                f"Sorry, you need to wait {hours} hours, {minutes} minutes, and {seconds} seconds before claiming another bonus."
            )

    except Exception as e:
        # Handle the exception (e.g., log it or reply with an error message)
        error_message = f"An error occurred: {str(e)}"
        bot.reply_to(message, error_message)
        

@bot.message_handler(func=lambda message: message.text == "💲 Balance")
def balance_command(message):
    user_id = message.chat.id
    try:  
        balance = Resources(user_id, 'balance')
        msg = f"<b>💵 Your Balance:</b> {balance.value():.4f} {currency.value()}"
        bot.send_message(user_id, msg, parse_mode='html')
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        bot.send_message(user_id, error_message, parse_mode='html')
        bot.send_message(ADMIN_USER_ID, error_message, parse_mode='html')
       
@bot.message_handler(func=lambda message: message.text == "🔗 Ref Stats")       
def referral_command(message):
    user_id = message.chat.id
    try:
        bot_username = bot.get_me().username 
        referral_link = f"https://t.me/{bot_username}?start={user_id}"
        total_refs = Resources(user_id, 'total_ref')
        bot.send_message(user_id, f"<b>Total Invited:</b> {total_refs.value()}  Users\n\n<b>Referral Link:</b>{referral_link}\n\n<b><u>Share it with friends and get {ref_bonus.value()} {currency.value()} for eachreferral</u></b>",parse_mode='html')
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        bot.send_message(user_id, error_message, parse_mode='html')
        bot.send_message(ADMIN_USER_ID, error_message, parse_mode='html')        


@bot.message_handler(func=lambda message: message.text == "🥳 Earn More")
def earnmore_command(message):
    user_id = message.chat.id
    bot.send_message(user_id, "No task available yet.")
    
    
@bot.message_handler(func=lambda message: message.text == "📤 Withdraw")
def withdraw_command(message):
    start_withdrawal(message)
    
    
def start_withdrawal(message):
    user_id = str(message.from_user.id)
    
    try:
        balance = Resources(user_id,'balance').value()
        
        if balance >= min_with:
            bot.send_message(user_id, f"Please enter your {currency.value()} wallet address for withdrawal:",reply_markup=back)
            bot.register_next_step_handler(message, get_withdrawal_wallet)
        else:
            bot.send_message(user_id, f"You need a minimum balance of {min_with} {currency.value()} to withdraw.")
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        bot.send_message(user_id, error_message, parse_mode='html')
        bot.send_message(ADMIN_USER_ID, error_message, parse_mode='html')  
        
        
# Example usage in a Telegram bot context
def get_withdrawal_wallet(message):
    try:
        global max_with
        user_id = str(message.from_user.id)
        withdrawal_wallet = message.text.strip()

        if message.text == "✘ Cancel":
          cancel(user_id)
          return

        if not withdrawal_wallet:
            bot.send_message(user_id, "Invalid wallet address. Please enter a valid wallet address.",reply_markup=markup)
            return

        wallet = Resources(user_id,"wallet")
        wallet.set_property("wallet",withdrawal_wallet)

        balance = Resources(user_id,"balance").value()

        if balance < max_with:
          max_with =  balance
        bot.send_message(user_id, f"<b>Send now the amount of {currency.value()} you want to withdraw </b>\n\nMax: {max_with:.4f} {currency.value()}",parse_mode="html")
        bot.register_next_step_handler(message, process_withdrawal_amount)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        bot.send_message(user_id, error_message, parse_mode='html')
        bot.send_message(ADMIN_USER_ID, error_message, parse_mode='html') 

def process_withdrawal_amount(message):
    try:
        user_id = str(message.from_user.id)

        if message.text == "✘ Cancel":
          cancel(user_id)
          return

        balance = Resources(user_id,"balance")

        withdrawal_amount_str = message.text
        if not re.match(r'^\d+(\.\d{1,8})?$', withdrawal_amount_str):
            bot.send_message(user_id, "Invalid withdrawal amount. Please enter a valid number.",reply_markup=markup)
            return
        withdrawal_amount = float(withdrawal_amount_str)
        if withdrawal_amount < min_with or withdrawal_amount > max_with or withdrawal_amount > balance.value():
            bot.send_message(user_id, "Invalid withdrawal amount. Please enter a valid amount within the withdrawallimits.  ",reply_markup=markup)
            return
        wallet = Resources(user_id,"wallet")
        balance.cut(withdrawal_amount)
        msg = f"""Withdraw Request Successfully

Status: Pending
User: {message.chat.first_name}
Amount: {withdrawal_amount} {currency.value()}
Address: {wallet.value()}
"""

        bot.send_message(user_id,msg,reply_markup=markup,parse_mode="markdown",disable_web_page_preview=True)
        bot.send_message(payment_channel,msg,parse_mode="markdown",disable_web_page_preview=True)
        
        
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        bot.send_message(user_id, error_message, parse_mode='html')
        bot.send_message(ADMIN_USER_ID, error_message, parse_mode='html') 
    
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    bot.reply_to(message,"No command found")

if __name__ == '__main__':
  while True:
    try:
      print("bot is running")
      bot.polling(non_stop=True)
    except Exception as e:
      print(f"Bot polling failed: {e}")
      bot.send_message(5337150824, f"Bot polling failed: {e}")
      time.sleep(10)
