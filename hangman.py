#HANGMAN in Python
import random

def show_hangman(hangman_art, errors):
    for line in hangman_art[errors]:
        print(line)

def welcoming_sequence():
    print("Welcome to the Hangman game.")
    print("We will show you the first and last letters of a word, and letter by letter you have to guess it.")
    print("You have right to 6 wrong guesses, either letters or the final word.")
    print("Good luck!")
    print()
    print()

def current_guessed_word(word, guessed_letters):
    guessed_word = ""
    for letter in word:
        if letter in guessed_letters:
            guessed_word += letter
        else:
            guessed_word += "_"
    return guessed_word

def main():
    words = ("apple", "banana", "coconut", "pear")
    hangman_art = {0: ("   ",
                   "   ",
                   "   "),
                   1: (" O ",
                   "   ",
                   "   "),
                2: (" O ",
                   " | ",
                   "   "),
                3: (" O ",
                   "/| ",
                   "   "),
                4: (" O ",
                   "/|\\",
                   "   "),
                5: (" O ",
                   "/|\\",
                   "/  "),
                6: (" O ",
                   "/|\\",
                   "/ \\")}

    welcoming_sequence()

    word = random.choice(words)
    print(f"### For the developer: word is: {word}###")
    errors = 0
    guessed_letters = []  # ALL the letters tried so far (right and wrong)
    guessed_letters.append(word[0])
    guessed_letters.append(word[-1])

    while errors < 6:
        print()
        current = current_guessed_word(word, guessed_letters)
        if current == word:
            print(f"Congrats, the word was exactly '{word}'!")
            break

        print(f"Your word: '{current}' ")
        print()

        invalid = True
        while invalid:
            guess = input("Type the word or a letter that might be in it: ").strip().lower()
            if (len(guess) > 1 and not len(guess) == len(word)) or len(guess) < 1 or not guess.isalpha(): #INVALID VALUE
                print(f"'{guess}' is not a valid. Please type in either the full word or a single letter.")
                print(f"You have made {errors} mistakes and you have got {6 - errors} more shots.")
            else:
                invalid = False

        if guess == word:
            print()
            print()
            print(f"Congrats, the word was exactly {word}!") #RIGHT WORD GOT DIRECTLY
            break

        elif guess in guessed_letters: #LETTER ALREADY TRIED, NO PENALTY
            print(f"You already tried the letter {guess}, try another one.")

        elif len(guess) == len(word): #WRONG WORD
            print(f"Sorry, {guess} is not the correct word.")
            errors += 1
            print(f"You have made {errors} mistakes and you have got {6 - errors} more shots.")

        elif guess in word: #RIGHT LETTER BUT INCOMPLETE WORD
            print(f"You got the letter {guess} right, keep going!")
            print(f"You have made {errors} mistakes and you have got {6 - errors} more shots.")
            guessed_letters.append(guess)

        else: #WRONG LETTER
            print(f"Sorry, the letter {guess} is not in the final word.")
            errors += 1
            print(f"You have made {errors} mistakes and you have got {6 - errors} more shots.")
            guessed_letters.append(guess)

        if errors > 0:
            print()
            show_hangman(hangman_art, errors)

    if errors == 6:
        print()
        print(f"The word was {word}. Better luck next time!")


if __name__ == "__main__":
    main()
