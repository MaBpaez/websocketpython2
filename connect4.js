const PLAYER1 = 'red';
const PLAYER2 = 'yellow';

function createBoard(board) {
  // Añade stylesheet.
  const linkElement = document.createElement('link');
  linkElement.href = import.meta.url.replace('.js', '.css');
  linkElement.rel = 'stylesheet';
  document.head.append(linkElement);

  // Genera el tablero de juego (board).
  for (let column = 0; column < 7; column++) {
    const columnElement = document.createElement('div');
    columnElement.className = 'column';
    columnElement.dataset.column = column;

    for (let row = 0; row < 6; row++) {
      const cellElement = document.createElement('div');
      cellElement.className = 'cell empty';
      cellElement.dataset.column = column;
      columnElement.append(cellElement);
    }

    board.append(columnElement);
  }
}

function playMove(board, player, column, row) {
  // Verifica los valores de los argumentos
  if (player !== PLAYER1 && player !== PLAYER2) {
    throw new Error(`el jugador debe ser ${PLAYER1} o ${PLAYER2}.`);
  }

  const columnElement = board.querySelectorAll('.column')[column];
  if (columnElement === undefined) {
    throw new RangeError('la columna debe estar entre 0 y 6.');
  }

  const cellElement = columnElement.querySelectorAll('.cell')[row];
  if (cellElement === undefined) {
    throw new RangeError('la fila debe estar entre 0 y 5.');
  }

  // Coloca el verificador en la casilla
  if (!cellElement.classList.replace('empty', player)) {
    throw new Error('la casilla debe estar vacía.');
  }
}

export { PLAYER1, PLAYER2, createBoard, playMove };
