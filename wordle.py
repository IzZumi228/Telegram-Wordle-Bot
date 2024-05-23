import random

def main():
    word = choose_random('words_database.txt')

    if not word:
        print("Sorry, we ran out of words")
        return
    print(word)
    while True:
        guess = input("Please enter 5-character word: ")
        if len(guess) == 5:
            answer, flag = wordle5(word, guess)
            print(answer)
            if flag:
                break

def choose_random(path):
    rd_line = random.randint(0, 999)
    with open(path, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            if i == rd_line:
                return line.lower().strip()
                


def wordle5(word, guess):
    answer = [""] * 5
    flag = True

    word_check = [[word[i], i] for i in range(5)]
    guess_check = [[guess[i], i] for i in range(5)]

    letters = list((set(word).intersection(set(guess))))

    word_indexes = {i: [] for i in letters}
    guess_indexes = {i: [] for i in letters}

    for i in range(len(letters)):
        for j in range(5):
            if word_check[j][0] == letters[i]:
                word_indexes[word_check[j][0]].append(word_check[j][1])

    for i in range(len(letters)):
        for j in range(5):
            if guess_check[j][0] == letters[i]:
                guess_indexes[guess_check[j][0]].append(guess_check[j][1])

    for i in range(5):
        if guess[i] in word_indexes:
            index = set(word_indexes[guess[i]]).intersection(set(guess_indexes[guess[i]]))
            if not index:
                answer[guess_indexes[guess[i]].pop()] = "🟡"
                flag = False
            else:
                while index:
                    answer[index.pop()] = "🟢"


    
    for i in range(5):
        if answer[i] not in ["🟢", "🟡"]:
            answer[i] = "🔴"
            flag = False
    
    return (" ".join(answer), flag)


if __name__ == "__main__":
    main()



