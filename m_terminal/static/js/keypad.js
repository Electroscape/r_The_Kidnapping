var passwords = [];
var allEntered = [];

/* Checks to see if the entered password is the correct length
 * and if each button pushed matches the password
 */
function isCorrect(id) {
    let password = passwords[id];
    let entered = allEntered[id];

    let correctPass = true;
    if (password.length !== entered.length) {
        correctPass = false;
    }

    for (let i = 0; i < password.length; i++) {
        if (entered[i] !== password[i]) {
            correctPass = false;
        }
    }

    if (!correctPass) {
        keypadClear(id);
    }
    return correctPass;
}

function keypadClear(id) {
    // Gets the element IDs of the screen, hash button, and asterisk button
    const screen = document.getElementById('screen' + id);
    // Resets the screen to blank, and resets the entered array to empty
    screen.textContent = '';
    screen.classList.remove('failed');
    screen.classList.remove('success');
    allEntered[id].length = 0;
}
