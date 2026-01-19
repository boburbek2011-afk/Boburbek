import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# O'yin holatlari saqlash
game_states = {}

# G'alaba kombinatsiyalari
WINNING_COMBOS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Gorizontal
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertikal
    [0, 4, 8], [2, 4, 6]              # Diagonal
]

# Asosiy menyu tugmalari
def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("✊✌️✋ Tosh-Qaychi-Qog'oz", callback_data='rps_game'),
            InlineKeyboardButton("❌⭕️ XO O'yini", callback_data='xo_game')
        ],
        [InlineKeyboardButton("📋 Qoidalar", callback_data='rules')],
        [InlineKeyboardButton("ℹ️ Bot haqida", callback_data='about')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Tosh-Qaychi-Qog'oz tugmalari
def rps_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("✊ Tosh", callback_data='rps_rock'),
            InlineKeyboardButton("✌️ Qaychi", callback_data='rps_scissors'),
            InlineKeyboardButton("✋ Qog'oz", callback_data='rps_paper')
        ],
        [InlineKeyboardButton("🔙 Asosiy menyu", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# XO doskasi
def xo_board_keyboard(board):
    keyboard = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            cell = board[i + j]
            symbol = " "
            if cell == "X":
                symbol = "❌"
            elif cell == "O":
                symbol = "⭕️"
            else:
                symbol = "⬜️"
            row.append(InlineKeyboardButton(symbol, callback_data=f'xo_{i+j}'))
        keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton("🔄 Yangilash", callback_data='xo_refresh'),
        InlineKeyboardButton("🔙 Menyuga", callback_data='main_menu')
    ])
    
    return InlineKeyboardMarkup(keyboard)

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"""
🎮 Assalomu alaykum {user.first_name}!

Mening ismim GameBot! Men bilan quyidagi o'yinlarni o'ynashingiz mumkin:

1. ✊✌️✋ Tosh, Qaychi, Qog'oz
2. ❌⭕️ XO (Krestkalar)

Quyidagi tugmalardan foydalanib o'yinni tanlang!
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )

# Asosiy menyu
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🎮 Asosiy menyu\n\nO'ynash uchun o'yin tanlang:",
        reply_markup=main_menu_keyboard()
    )

# Tosh-Qaychi-Qog'oz o'yini
async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✊✌️✋ Tosh, Qaychi, Qog'oz\n\n"
        "Tanlovingizni qiling:",
        reply_markup=rps_keyboard()
    )

# Tosh-Qaychi-Qog'oz natijasi
async def rps_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    choice = query.data.split('_')[1]
    
    # Kompyuter tanlovi
    options = ['rock', 'scissors', 'paper']
    comp_choice = random.choice(options)
    
    # Tanlov matnlari
    choices_text = {
        'rock': '✊ Tosh',
        'scissors': '✌️ Qaychi', 
        'paper': '✋ Qog\'oz'
    }
    
    user_text = choices_text[choice]
    comp_text = choices_text[comp_choice]
    
    # G'olibni aniqlash
    if choice == comp_choice:
        result = "🏳️ Durrang!"
    elif (choice == 'rock' and comp_choice == 'scissors') or \
         (choice == 'scissors' and comp_choice == 'paper') or \
         (choice == 'paper' and comp_choice == 'rock'):
        result = "🎉 Siz yutingiz!"
    else:
        result = "🤖 Kompyuter yuti!"
    
    # Natija keyboard
    keyboard = [
        [InlineKeyboardButton("🔄 Yana o'ynash", callback_data='rps_game')],
        [InlineKeyboardButton("🔙 Asosiy menyu", callback_data='main_menu')]
    ]
    
    await query.edit_message_text(
        f"✊✌️✋ Tosh, Qaychi, Qog'oz\n\n"
        f"Siz tanladingiz: {user_text}\n"
        f"Kompyuter tanladi: {comp_text}\n\n"
        f"{result}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# XO o'yini boshlash
async def xo_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Yangi o'yin holati
    game_states[user_id] = {
        'board': [' ' for _ in range(9)],
        'player_turn': True,
        'game_over': False
    }
    
    await query.edit_message_text(
        "❌⭕️ XO O'yini\n\n"
        "Siz: ❌\n"
        f"Holat: Sizning navbatingiz\n\n"
        "Doska:",
        reply_markup=xo_board_keyboard(game_states[user_id]['board'])
    )

# XO o'yini harakati
async def xo_move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # O'yin holatini tekshirish
    if user_id not in game_states:
        await xo_game_start(update, context)
        return
    
    game_state = game_states[user_id]
    
    # Agar o'yin tugagan bo'lsa
    if game_state['game_over']:
        await query.answer("O'yin tugagan! Yangi o'yin boshlang.", show_alert=True)
        return
    
    # Tugma ma'lumotini olish
    data = query.data
    
    if data == 'xo_refresh':
        await query.edit_message_text(
            "❌⭕️ XO O'yini\n\n"
            "Siz: ❌\n"
            f"Holat: {'Sizning navbatingiz' if game_state['player_turn'] else 'Kompyuter navbati'}\n\n"
            "Doska:",
            reply_markup=xo_board_keyboard(game_state['board'])
        )
        return
    
    elif data == 'main_menu':
        await main_menu(update, context)
        return
    
    # Katak indeksini olish
    index = int(data.split('_')[1])
    
    # Agar katak band bo'lsa
    if game_state['board'][index] != ' ':
        await query.answer("Bu katak allaqachon band!", show_alert=True)
        return
    
    # Foydalanuvchi harakati
    game_state['board'][index] = 'X'
    
    # G'olibni tekshirish
    winner = check_xo_winner(game_state['board'])
    
    if winner:
        game_state['game_over'] = True
        winner_text = "🎉 Siz yutingiz!" if winner == 'X' else "🤖 Kompyuter yuti!"
        
        await query.edit_message_text(
            f"❌⭕️ XO O'yini\n\n"
            f"{winner_text}\n\n"
            "Yakuniy doska:",
            reply_markup=xo_board_keyboard(game_state['board'])
        )
        return
    
    # Durrangni tekshirish
    if ' ' not in game_state['board']:
        game_state['game_over'] = True
        await query.edit_message_text(
            "❌⭕️ XO O'yini\n\n"
            "🏳️ Durrang! Hech kim yutmadi.\n\n"
            "Yakuniy doska:",
            reply_markup=xo_board_keyboard(game_state['board'])
        )
        return
    
    # Kompyuter harakati
    comp_move = find_best_move(game_state['board'])
    if comp_move is not None:
        game_state['board'][comp_move] = 'O'
        
        # Kompyuter harakatidan keyin tekshirish
        winner = check_xo_winner(game_state['board'])
        
        if winner:
            game_state['game_over'] = True
            winner_text = "🎉 Siz yutingiz!" if winner == 'X' else "🤖 Kompyuter yuti!"
            
            await query.edit_message_text(
                f"❌⭕️ XO O'yini\n\n"
                f"{winner_text}\n\n"
                "Yakuniy doska:",
                reply_markup=xo_board_keyboard(game_state['board'])
            )
            return
        
        # Durrangni tekshirish
        if ' ' not in game_state['board']:
            game_state['game_over'] = True
            await query.edit_message_text(
                "❌⭕️ XO O'yini\n\n"
                "🏳️ Durrang! Hech kim yutmadi.\n\n"
                "Yakuniy doska:",
                reply_markup=xo_board_keyboard(game_state['board'])
            )
            return
    
    # Navbatni yangilash
    game_state['player_turn'] = not game_state['player_turn']
    
    await query.edit_message_text(
        "❌⭕️ XO O'yini\n\n"
        "Siz: ❌\n"
        f"Holat: {'Sizning navbatingiz' if game_state['player_turn'] else 'Kompyuter navbati'}\n\n"
        "Doska:",
        reply_markup=xo_board_keyboard(game_state['board'])
    )

# XO g'olibini tekshirish
def check_xo_winner(board):
    for combo in WINNING_COMBOS:
        a, b, c = combo
        if board[a] == board[b] == board[c] and board[a] != ' ':
            return board[a]
    return None

# Kompyuter uchun eng yaxshi harakat
def find_best_move(board):
    # Avval g'alaba qozonish imkoniyatini tekshirish
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'O'
            if check_xo_winner(board) == 'O':
                board[i] = ' '
                return i
            board[i] = ' '
    
    # Foydalanuvchining g'alabasini to'sish
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'X'
            if check_xo_winner(board) == 'X':
                board[i] = ' '
                return i
            board[i] = ' '
    
    # Markazni olish
    if board[4] == ' ':
        return 4
    
    # Boshqa bo'sh kataklarni tekshirish
    empty_cells = [i for i in range(9) if board[i] == ' ']
    if empty_cells:
        return random.choice(empty_cells)
    
    return None

# Qoidalar
async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    rules_text = """
📋 O'yin Qoidalari:

✊✌️✋ Tosh, Qaychi, Qog'oz:
- Tosh qaychini sindiradi (✊ > ✌️)
- Qaychi qog'ozni kesadi (✌️ > ✋)
- Qog'oz toshni o'rab oladi (✋ > ✊)

❌⭕️ XO O'yini:
- Siz ❌ belgisisiz
- 3 ta bir xil belgini ketma-ket qo'ygan yutar
- Gorizontal, vertikal yoki diagonal qator
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Asosiy menyu", callback_data='main_menu')]]
    
    await query.edit_message_text(
        rules_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Bot haqida
async def about_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    about_text = """
ℹ️ GameBot Haqida

Bu bot 2 ta klassik o'yinni o'z ichiga oladi:
1. Tosh, Qaychi, Qog'oz
2. XO (Krestkalar)

Bot yaratuvchi: Siz
Dasturlash tili: Python
Kutubxona: python-telegram-bot

Quvonch bilan o'ynang! 🎮
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Asosiy menyu", callback_data='main_menu')]]
    
    await query.edit_message_text(
        about_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Xato handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Xato yuz berdi: {context.error}")

# Asosiy funksiya
def main():
    # API TOKENNI O'RNATING!
    # Eski tokenni O'CHIRIB, yangisini oling!
    API_TOKEN = "8089682606:AAGKqlbznSBII0BDmt3-7-dMJQgtdpNJoJk"
    
    # Application yaratish
    application = Application.builder().token(API_TOKEN).build()
    
    # Handlerlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='main_menu'))
    application.add_handler(CallbackQueryHandler(rps_game, pattern='rps_game'))
    application.add_handler(CallbackQueryHandler(rps_choice, pattern='^rps_'))
    application.add_handler(CallbackQueryHandler(xo_game_start, pattern='xo_game'))
    application.add_handler(CallbackQueryHandler(xo_move, pattern='^xo_'))
    application.add_handler(CallbackQueryHandler(show_rules, pattern='rules'))
    application.add_handler(CallbackQueryHandler(about_bot, pattern='about'))
    
    # Xato handler
    application.add_error_handler(error_handler)
    
    # Botni ishga tushirish
    print("Bot ishga tushmoqda...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()