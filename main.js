import { createBoard, playMove } from './connect4.js';

function initGame(websocket) {
  websocket.addEventListener('open', () => {
    // Send an "init" event according to who is connecting.
    const params = new URLSearchParams(window.location.search);
    let event = { type: 'init' };
    if (params.has('join')) {
      // Second player joins an existing game.
      event.join = params.get('join');
    } else if (params.has('watch')) {
      // Spectator watches an existing game.
      event.watch = params.get('watch');
    } else {
      // First player starts a new game.
    }
    websocket.send(JSON.stringify(event));
  });
}

function showMessage(message) {
  window.setTimeout(() => window.alert(message), 50);
}

function receiveMoves(board, websocket) {
  websocket.addEventListener('message', ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case 'init':
        // Crea los enlaces para invitar a un segundo jugador y a un espectador
        document.querySelector('.join').href = '?join=' + event.join;
        document.querySelector('.watch').href = '?watch=' + event.watch;
        break;
      case 'play':
        // Actualiza la interfaz de usuario con el movimiento
        playMove(board, event.player, event.column, event.row);
        break;
      case 'win':
        showMessage(`Jugador ${event.player} gana!`);
        // No se esperan más mensajes; cierra la conexión WebSocket.
        websocket.close(1000);
        break;
      case 'error':
        showMessage(event.message);
        break;
      default:
        throw new Error(`Tipo de evento no soportado: ${event.type}.`);
    }
  });
}

function sendMoves(board, websocket) {
  // No enviar movimientos para un espectador que esta observando el juego.
  const params = new URLSearchParams(window.location.search);
  if (params.has('watch')) {
    return;
  }

  // Al hacer clic en una columna, envía un evento de ‘play’ para un movimiento en esa columna.
  board.addEventListener('click', ({ target }) => {
    const column = target.dataset.column;
    // Ignora los clicks fuera de una columna.
    if (column === undefined) {
      return;
    }
    const event = {
      type: 'play',
      column: parseInt(column, 10),
    };
    websocket.send(JSON.stringify(event));
  });
}

window.addEventListener('DOMContentLoaded', () => {
  // Inicializa la interfaz de usuario UI.
  const board = document.querySelector('.board');
  createBoard(board);
  // Abre la conexión WebSocket y registra los manejadores de eventos (handlers).
  const websocket = new WebSocket('ws://localhost:8001/');
  initGame(websocket);
  receiveMoves(board, websocket);
  sendMoves(board, websocket);
});
