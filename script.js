// Il front end: gira nel BROWSER, non sul server.
// Non conosce la parola segreta: chiede tutto al back end Python tramite fetch()
// e si limita a mostrare quello che riceve.

// Stato lato browser
let gameId = null;       // id della partita, ce lo da' il server
let lastMasked = "";     // parola mostrata prima: serve per animare solo le lettere nuove
let lastErrors = 0;      // errori prima: serve per far tremare la card quando sbagli
let gameOver = false;

// Riferimenti agli elementi HTML (li cerchiamo per id)
const card = document.getElementById("card");
const wordEl = document.getElementById("word");
const errorsEl = document.getElementById("errors");
const barFill = document.getElementById("bar-fill");
const messageEl = document.getElementById("message");
const keyboardEl = document.getElementById("keyboard");
const form = document.getElementById("guess-form");
const input = document.getElementById("guess-input");
const newGameBtn = document.getElementById("new-game");
const hangmanParts = document.querySelectorAll("#hangman .part");

// Creiamo i 26 tasti della tastiera una volta sola
for (const letter of "abcdefghijklmnopqrstuvwxyz") {
    const key = document.createElement("button");
    key.className = "key";
    key.textContent = letter;
    key.dataset.letter = letter;          // diventa l'attributo HTML data-letter="a"
    key.addEventListener("click", () => sendGuess(letter));
    keyboardEl.appendChild(key);
}

// Manda una richiesta POST al server e restituisce la risposta JSON.
// "async/await" serve perche' la risposta non arriva subito: aspettiamo il server.
async function post(url, data) {
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data), // oggetto JS -> testo JSON
        });
        return await response.json(); // testo JSON -> oggetto JS
    } catch (err) {
        // Succede se la pagina non e' servita da Flask (es. Live Server o doppio click
        // sul file): non c'e' nessun Python che risponde a /api/...
        console.error(err);
        return { error: "Cannot reach the Python server. Run 'python app.py' and open http://127.0.0.1:5000" };
    }
}

// Aggiorna TUTTA la pagina con i dati ricevuti dal server
function render(data) {
    if (data.error) {
        messageEl.textContent = data.error;
        messageEl.className = "message lost";
        return;
    }

    gameOver = data.status !== "playing";

    // 1. Le caselle della parola
    wordEl.innerHTML = "";
    for (let i = 0; i < data.masked.length; i++) {
        const tile = document.createElement("span");
        tile.className = "tile";
        const letter = data.masked[i];
        if (letter !== "_") {
            tile.textContent = letter;
            tile.classList.add("revealed");
            if (lastMasked[i] !== letter) tile.classList.add("new"); // appena scoperta
        } else if (gameOver) {
            tile.textContent = data.word[i];   // a partita persa mostriamo le lettere mancanti
            tile.classList.add("missed", "new");
        }
        wordEl.appendChild(tile);
    }
    lastMasked = data.masked;

    // 2. L'impiccato: visibili solo i pezzi con data-step <= errori
    hangmanParts.forEach(part => {
        part.classList.toggle("visible", Number(part.dataset.step) <= data.errors);
    });
    card.classList.toggle("lost-game", data.status === "lost");

    // 3. Contatore e barra degli errori
    errorsEl.textContent = `Mistakes ${data.errors} / ${data.max_errors}`;
    barFill.style.width = (data.errors / data.max_errors * 100) + "%";

    // Se gli errori sono aumentati, la card trema
    if (data.errors > lastErrors) {
        card.classList.remove("shake");
        void card.offsetWidth;            // trucco per far ripartire l'animazione CSS
        card.classList.add("shake");
    }
    lastErrors = data.errors;

    // 4. Messaggio
    messageEl.textContent = data.message;
    messageEl.className = "message " + (gameOver ? data.status : "");

    // 5. Tastiera: colora i tasti gia' usati
    for (const key of keyboardEl.children) {
        const letter = key.dataset.letter;
        const tried = data.guessed_letters.includes(letter);
        key.classList.toggle("correct", tried && data.masked.includes(letter));
        key.classList.toggle("wrong", tried && !data.masked.includes(letter));
        key.disabled = tried || gameOver;
    }

    // 6. Form e bottone "New game"
    input.disabled = gameOver;
    form.querySelector("button").disabled = gameOver;
    newGameBtn.classList.toggle("highlight", gameOver);
}

async function sendGuess(guess) {
    if (gameOver || !gameId) return;
    const data = await post("/api/guess", { game_id: gameId, guess: guess });
    render(data);
}

async function newGame() {
    lastMasked = "";
    lastErrors = 0;
    const data = await post("/api/new-game", {});
    gameId = data.game_id;
    render(data);
}

// Form della parola intera
form.addEventListener("submit", (event) => {
    event.preventDefault(); // evita che il browser ricarichi la pagina (comportamento di default dei form)
    sendGuess(input.value);
    input.value = "";
});

// Tastiera fisica: premere una lettera = cliccare il tasto
// (tranne quando stai scrivendo nel campo della parola intera)
document.addEventListener("keydown", (event) => {
    if (event.target === input) return;
    if (event.ctrlKey || event.metaKey || event.altKey) return; // non rubare Ctrl+R, Ctrl+C...
    if (/^[a-z]$/i.test(event.key)) {
        const key = keyboardEl.querySelector(`[data-letter="${event.key.toLowerCase()}"]`);
        if (!key.disabled) sendGuess(event.key);
    }
});

newGameBtn.addEventListener("click", newGame);

// Appena la pagina si carica, iniziamo una partita
newGame();
