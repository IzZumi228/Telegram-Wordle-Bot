import telebot
import json
from wordle import wordle5, choose_random



TOKEN = '7079075089:AAEYE1IQ8jnx3uSyKz6XovcEbQHHiFjktW4'
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# Initialize dictionaries
user_states = {}
user_scores = {}
individual_scores = {}

def construct_stats(chat_id):
    if chat_id in user_scores or chat_id in individual_scores:
        return
    user_scores[chat_id] = {}
    individual_scores[chat_id] = {}


# File paths for storing scores
USER_SCORES_FILE = 'user_scores.json'
INDIVIDUAL_SCORES_FILE = 'individual_scores.json'

def save_data(chat_id):
    with open(USER_SCORES_FILE, 'w', encoding='utf-8') as user_file:
        json.dump(user_scores[chat_id], user_file)
    with open(INDIVIDUAL_SCORES_FILE, 'w', encoding='utf-8') as individual_file:
        json.dump(individual_scores[chat_id], individual_file)

def load_data(chat_id):
    global user_scores
    global individual_scores

    try:
        with open(USER_SCORES_FILE, 'r', encoding='utf-8') as user_file:
            user_scores[chat_id] = json.load(user_file)
    except FileNotFoundError:
        user_scores = {}

    try:
        with open(INDIVIDUAL_SCORES_FILE, 'r', encoding='utf-8') as individual_file:
            individual_scores[chat_id] = json.load(individual_file)
    except FileNotFoundError:
        individual_scores = {}

def reset_game(chat_id):
    word = choose_random('words_database.txt')
    user_states[chat_id] = {
        "word": word,
        "guesses": [],
        "guess_count": {},
        "total_guess_count": 0
    }

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет, чтобы начать игру воспользуйтесь командой /wordle5")
    construct_stats(message.chat.id)

@bot.message_handler(commands=['wordle5'])
def start_wordle(message):
    chat_id = message.chat.id
    reset_game(chat_id)
    bot.send_message(chat_id, "Игра началась! Введите слово из 5 букв:")
    construct_stats(message.chat.id)
    

@bot.message_handler(commands=['groupstats'])
def group_states(message):
    load_data(message.chat.id)
    chat_info = bot.get_chat(message.chat.id)
    chat_name = chat_info.title if chat_info.title else "No title available"
    if not user_scores:
        bot.reply_to(message, "Пока нет информации о пользователях.")
        return

    scores_message = f"Результаты пользователей для группы {chat_name}:\n"
    for user_id, score in user_scores[message.chat.id].items():
        user_info = bot.get_chat(user_id)
        username = user_info.username if user_info.username else user_info.first_name
        scores_message += f"@{username}: {score} угаданных слов\n"
    
    bot.reply_to(message, scores_message)


@bot.message_handler(commands=['mystats'])
def group_states(message):
    load_data(message.chat.id)
    username = message.from_user.username if message.from_user.username else message.from_user.first_name
    if username not in individual_scores[message.chat.id]:
        bot.reply_to(message, "Вы пока не отгдали ни одного слова!")
    else:
        scores_message = f"Личная статистика {username}:\n"
        for tc, score in sorted(individual_scores[message.chat.id][username].items(), key=lambda x: x[0]):
            match (tc):
                case '1':
                    scores_message += f"Количество слов отгаданных за <b>одну</b> попытку: {score}\n"
                case '2':
                    scores_message += f"Количество слов отгаданных за <b>две</b> попытки: {score}\n"
                case '3':
                    scores_message += f"Количество слов отгаданных за <b>три</b> попытки: {score}\n"
                case '4':
                    scores_message += f"Количество слов отгаданных за <b>четыре</b> попытки: {score}\n"
                case '5':
                    scores_message += f"Количество слов отгаданных за <b>пять</b> попыток: {score}\n"
                case '6':
                    scores_message += f"Количество слов отгаданных за <b>шесть</b> попыток: {score}\n"

        if username == "cvkacry":
            scores_message += "Шахиста тебе нет равных! Королева! Лучшая!!!"    


        bot.reply_to(message, scores_message)
        scores_message = ''
@bot.message_handler(func=lambda m: len(m.text) == 5)
def handle_guess(message):
    chat_id = message.chat.id
    guess = message.text.strip().lower()
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else message.from_user.first_name

    if len(guess) != 5:
        bot.send_message(chat_id, "Пожалуйста, введите слово из 5 букв.")
        return

    if chat_id not in user_states:
        bot.send_message(chat_id, "Игра не начата. Используйте команду /wordle5, чтобы начать игру.")
        return
    game_state = user_states[chat_id]
    word = game_state["word"]
    answer, flag = wordle5(word, guess)

    if username in game_state['guess_count']:
        game_state['guess_count'][username] += 1
    else:
        game_state['guess_count'][username] = 1

    
    game_state["total_guess_count"] += 1
    

    bot.reply_to(message, f"Ваш результат: {answer}\nПопыток oсталось: <b>{6 - game_state["total_guess_count"]}</b>")

    if flag:
        bot.send_message(chat_id, f"Поздравляем, @{username}! Вы угадали слово правильно!\nЗагаданное слово: <b>{word}</b>\nПопыток потрачено: <b>{game_state['total_guess_count']}</b>")
        
        # Update the user's score
        if user_id in user_scores[message.chat.id]:
            user_scores[message.chat.id][user_id] += 1
        else:
            user_scores[message.chat.id][user_id] = 1

        for user, gc in game_state['guess_count'].items():
            if user not in individual_scores[message.chat.id]:
                individual_scores[message.chat.id][user] = {1: 0, 2: 0, 3:0, 4:0, 5:0, 6:0}
                individual_scores[message.chat.id][user][gc] += 1
            else:
                individual_scores[message.chat.id][user][gc] += 1
                
        
        save_data(chat_id)  # Save data after updating scores
        reset_game(chat_id)  # Reset the game for the next round

    elif game_state['total_guess_count'] > 5:
        bot.send_message(chat_id, f"К Сожалению слово не было отгадано.\nЗагаданное слово было: <b>{word}</b>\n")
        save_data(chat_id)  # Save data even if the game is lost
        reset_game(chat_id)

    else:
        bot.send_message(chat_id, "Попробуйте снова! Введите слово из 5 букв:")

    print(user_states)
    print(user_scores)
    print(individual_scores)

if __name__ == "__main__":

    bot.infinity_polling()
