# Logica dell'impiccato SENZA input() e print().
#
# Nello script da terminale (hangman.py) la logica e l'interazione con l'utente
# sono mescolate: input() blocca e aspetta la tastiera, print() scrive sul terminale.
# Un server web non ha tastiera ne' terminale: riceve una richiesta HTTP e deve
# rispondere subito con dei dati. Per questo qui la logica e' separata:
# ogni funzione riceve dati e restituisce dati, e chi la chiama (il server)
# decide cosa farne.

import random

WORDS = ("apple", "banana", "coconut", "pear")
MAX_ERRORS = 6

# Stesso omino dello script, ma con il patibolo attorno,
# cosi' anche con 0 errori si vede qualcosa
_BODY = {
    0: ("   ", "   ", "   "),
    1: (" O ", "   ", "   "),
    2: (" O ", " | ", "   "),
    3: (" O ", "/| ", "   "),
    4: (" O ", "/|\\", "   "),
    5: (" O ", "/|\\", "/  "),
    6: (" O ", "/|\\", "/ \\"),
}

HANGMAN_ART = {
    errors: (
        "  +---+",
        "  |   |",
        f" {head}  |",
        f" {torso}  |",
        f" {legs}  |",
        "      |",
        "=========",
    )
    for errors, (head, torso, legs) in _BODY.items()
}


class HangmanGame:
    """Una partita. Nello script erano variabili locali di main();
    qui le teniamo dentro un oggetto, cosi' il server puo' conservarlo
    tra una richiesta e l'altra."""

    def __init__(self):
        self.word = random.choice(WORDS)
        self.errors = 0
        self.guessed_letters = [self.word[0], self.word[-1]]
        self.status = "playing"  # "playing", "won" oppure "lost"

    def masked_word(self):
        # Equivalente di current_guessed_word() dello script
        return "".join(l if l in self.guessed_letters else "_" for l in self.word)

    def guess(self, guess):
        """Applica un tentativo e restituisce un messaggio per il giocatore."""
        guess = guess.strip().lower()

        if self.status != "playing":
            return "The game is over. Start a new one!"

        if (len(guess) > 1 and len(guess) != len(self.word)) or len(guess) < 1 or not guess.isalpha():
            return f"'{guess}' is not valid. Type either the full word or a single letter."

        if guess == self.word:
            self.guessed_letters.extend(self.word)
            message = f"Congrats, the word was exactly '{self.word}'!"
        elif guess in self.guessed_letters:
            return f"You already tried the letter '{guess}', try another one."
        elif len(guess) == len(self.word):
            self.errors += 1
            message = f"Sorry, '{guess}' is not the correct word."
        elif guess in self.word:
            self.guessed_letters.append(guess)
            message = f"You got the letter '{guess}' right, keep going!"
        else:
            self.guessed_letters.append(guess)
            self.errors += 1
            message = f"Sorry, the letter '{guess}' is not in the word."

        # Controllo vittoria / sconfitta dopo ogni tentativo
        if self.masked_word() == self.word:
            self.status = "won"
            message = f"Congrats, the word was exactly '{self.word}'!"
        elif self.errors >= MAX_ERRORS:
            self.status = "lost"
            message = f"The word was '{self.word}'. Better luck next time!"

        return message

    def to_dict(self):
        """I dati che mandiamo al browser (diventeranno JSON).
        ATTENZIONE: la parola vera la mandiamo solo a partita finita,
        altrimenti chiunque potrebbe leggerla dagli strumenti sviluppatore del browser."""
        return {
            "masked": self.masked_word(),
            "errors": self.errors,
            "max_errors": MAX_ERRORS,
            "guessed_letters": self.guessed_letters,
            "status": self.status,
            "art": HANGMAN_ART[self.errors],
            "word": self.word if self.status != "playing" else None,
        }
