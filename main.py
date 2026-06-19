import telebot
import requests
import os

# هنجيب التوكن من إعدادات الاستضافة للأمان
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# 1. أمر البداية /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "⚽ مرحباً بك في بوت الكرة المتكامل! 🌍\n\n"
        "إليك الخدمات المتاحة حالياً:\n"
        "🔍 **البحث عن لاعب:** اكتب اسم أي لاعب بالإنجليزية (مثل: Messi, Mo Salah) لمعرفة تفاصيله.\n"
        "📅 **مواعيد الماتشات:** اكتب أمر /matches لمعرفة أهم المباريات القادمة."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# 2. أمر مواعيد الماتشات /matches
@bot.message_handler(commands=['matches'])
def get_matches(message):
    waiting_msg = bot.reply_to(message, "جاري جلب مواعيد المباريات الهامة... ⏳")
    
    # سيرفر مجاني ومفتوح لمواعيد الماتشات
    url = "https://worldcupjson.net/matches/current" 
    try:
        response = requests.get(url)
        if response.status_code == 200:
            matches_data = response.json()
            if not matches_data:
                bot.edit_message_text("📅 لا توجد مباريات جارية أو قريبة جداً حالياً. تابعنا لاحقاً!", message.chat.id, waiting_msg.message_id)
                return
                
            reply = "📅 **أهم المباريات الحالية/القادمة:**\n\n"
            for match in matches_data[:5]: # عرض أول 5 مباريات
                home = match.get('home_team', {}).get('country', 'غير معروف')
                away = match.get('away_team', {}).get('country', 'غير معروف')
                status = match.get('status', 'قريباً')
                reply += f"⚽ {home} ضد {away}\nالاحالة: {status}\n-------------------\n"
            
            bot.edit_message_text(reply, message.chat.id, waiting_msg.message_id)
        else:
            bot.edit_message_text("⚠️ السيرفر مشغول حالياً، جرب تطلب المواعيد تاني كمان شوية.", message.chat.id, waiting_msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ حصل خطأ أثناء جلب الماتشات. جرب لاحقاً.", message.chat.id, waiting_msg.message_id)

# 3. استقبال اسم اللاعب والبحث عنه
@bot.message_handler(func=lambda message: True)
def search_player(message):
    player_name = message.text.strip()
    
    # لو المستخدم كتب أمر من الأوامر متعتبروش اسم لاعب
    if player_name.startswith('/'):
        return

    searching_msg = bot.reply_to(message, "جاري البحث عن اللاعب في الموسوعة العالمية... 🔍")
    url = f"https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p={player_name}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data and data.get("player"):
            player = data["player"][0]
            info = f"⚽ **معلومات اللاعب:** {player.get('strPlayer')}\n\n"
            info += f"🏃‍♂️ **المركز:** {player.get('strPosition', 'غير معروف')}\n"
            info += f"🏢 **النادي الحالي:** {player.get('strTeam', 'غير معروف')}\n"
            info += f"🌍 **الجنسية:** {player.get('strNationality', 'غير معروف')}\n"
            info += f"📅 **تاريخ الميلاد:** {player.get('dateBorn', 'غير معروف')}\n"
            
            if player.get('strThumb'):
                bot.send_photo(message.chat.id, player['strThumb'], caption=info, parse_mode="Markdown")
                bot.delete_message(message.chat.id, searching_msg.message_id)
            else:
                bot.edit_message_text(info, message.chat.id, searching_msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text(f"❌ لم أجد لاعب باسم '{player_name}'. تأكد من كتابة الاسم بالإنجليزي صح.", message.chat.id, searching_msg.message_id)
    except Exception as e:
        bot.edit_message_text("⚠️ حصلت مشكلة في الاتصال بسيرفر اللاعبين.", message.chat.id, searching_msg.message_id)

# تشغيل البوت
if __name__ == "__main__":
    print("البوت شغال بنجاح...")
    bot.infinity_polling()
          
