const ws = new WebSocket(url='ws://localhost:8000/ws')
const EMPTY_STATE = ""
let iPlayer
let secondPlayer
let gameID
let canMove = false
let gameState

ws.onopen = function (event) {
    console.log(event)
    send({"action": "new"})
}

ws.onmessage = function (event) {
    let data = JSON.parse(event.data)
    console.log(data)

    switch (data.action) {
        case "new":
            gameList(data.games, true)
            break
        case "create":
            gameList(data.games, true)
            break
        case "join":
            startGame(data.action, data.player, data.other_player, data.is_player_move, data.message)
            break
        case "move":
            movePlayer(data.cell, data.is_player_move, data.state, data.message)
            break
        case "close":
            gameList(data.games, true)
            break
        case "finish":
            finishGame(data.message)
            break
        default:
            break
    }
}

function makeId(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    for (let i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}

function send(data) {
    ws.send(JSON.stringify(data))
}

function generateNewGameState() {
    gameState = Array(9).fill(EMPTY_STATE);
    console.log(gameState)
}

function createNewGame(event) {
    iPlayer = "X"
    // set game id for client, who created the game
    gameID = makeId(10)
    generateNewGameState()
    showGameField("Waiting for another player...")
    send({"action": "create", "game_id": gameID})
}

function joinGame(event) {
    let btn = event.target
    // set game id for the client, who joined the game
    gameID = btn.id
    // generate game state for the client, who joined the game
    generateNewGameState()
    send({"action": "join", "game_id": btn.id})
}

function startGame(action, player, other_player, isPlayerMove, message) {
    // when second player joined the game, we need to send a message to each WebSocket to specify players states
    iPlayer = player
    secondPlayer = other_player
    canMove = isPlayerMove
    showGameField(message)
}

function showGameField(status_message) {
    document.querySelectorAll('.cell').forEach(cell => cell.innerHTML = "")
    document.getElementById("game").className = "game-off"
    document.getElementById("tic-tac-toe").className = "game-on"
    let playerState = document.getElementById("player")
    playerState.className = "game-on"
    playerState.innerHTML = `You are player ${iPlayer}`
    document.querySelector('.game-status').innerHTML = status_message
}

function showGamesList() {
    document.getElementById("game").className = "game-on"
    document.getElementById("tic-tac-toe").className = "game-off"
    let playerState = document.getElementById("player")
    playerState.className = "game-off"
    playerState.innerHTML = ""
}


function appendGame(gameList, gameNumber, gameID) {
    let li = document.createElement('li')
    let text = document.createTextNode(`${gameNumber}`)
    let button = document.createElement('button')
    button.id = `${gameID}`
    button.innerHTML = "Join"
    button.addEventListener("click", joinGame)
    li.appendChild(text)
    li.appendChild(button)
    gameList.appendChild(li)
}

function gameList(games, reset = false) {
    showGamesList()

    let gameList = document.getElementById("gameList")

    if (reset){
        gameList.innerHTML = ""
    }

    games.forEach(function (item, index) {
        appendGame(gameList, index + 1, item);
    })
}

function clickCell(event) {
    const cell = event.target
    const cellIndex = parseInt(cell.getAttribute("data-cell-index"))

    // if other player's turn to move or cell was already picked
    if (!canMove || gameState[cellIndex] !== EMPTY_STATE) {
        return
    }

    console.log(gameState)
    gameState[cellIndex] = iPlayer
    cell.innerHTML = iPlayer

    send({"action": "move", "cell": cellIndex, "state": iPlayer, "game_id": gameID})
}

function movePlayer(cellIndex, isPlayerMove, state, message) {
    let cellClicked = document.querySelector(`[data-cell-index="${cellIndex}"]`)
    document.querySelector('.game-status').innerHTML = message

    gameState[cellIndex] = state
    cellClicked.innerHTML = state
    canMove = isPlayerMove
}

function closeGame(event) {
    send({"action": "close", "game_id": gameID, "state": iPlayer})
}

function finishGame(message) {
    canMove = false
    document.querySelector('.game-status').innerHTML = message
}

document.getElementById("create-game").addEventListener("click", createNewGame)

document.querySelectorAll('.cell').forEach(cell => cell.addEventListener('click', clickCell))

document.getElementById("close-game").addEventListener("click", closeGame)
