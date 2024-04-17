#!/usr/bin/env python

import asyncio, json, secrets, websockets
from connect4 import PLAYER1, PLAYER2, Connect4


JOIN = {}
WATCH = {}


async def error(websocket, message):
    """
    Enviar un mensaje de error.

    """

    event = {
        "type": "error",
        "message": message,
    }

    await websocket.send(json.dumps(event))


async def replay(websocket, game):
    """
    Enviar movimientos anteriores.

    """

    # Haga una copia para evitar una excepción si game.moves(es una lista) cambia
    # mientras la iteración está en progreso. Si se juega un movimiento mientras se
    # ejecuta la repetición, los movimientos se enviarán desordenados, pero cada
    # movimiento se enviará una vez y, finalmente, la interfaz de usuario será consistente.

    for player, column, row in game.moves.copy():
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        await websocket.send(json.dumps(event))


async def play(websocket, game, player, connected):
    """
    Recibe y procesa los movimientos de un jugador.

    """

    async for message in websocket:
        # Analizar un evento "play" desde la interfaz de usuario.
        event = json.loads(message)
        assert event["type"] == "play"
        column = event["column"]

        try:
            # Juega el movimiento.
            row = game.play(player, column)

        except RuntimeError as exc:
            # Envía un evento "error" si el movimiento fue erróneo.
            await error(websocket, str(exc))
            continue

        # Envía un evento "play" para actualizar la interfaz de usuario.
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        websockets.broadcast(connected, json.dumps(event))

        # Si el movimiento es ganador, envía un evento "win".
        if game.winner is not None:
            event = {
                "type": "win",
                "player": game.winner,
            }
            websockets.broadcast(connected, json.dumps(event))


async def start(websocket):
    """
    Maneja la conexión del primer jugador: comienza un nuevo juego

    """

    # Inicializar un juego Connect Four, el conjunto de conexiones WebSocket que
    # reciben movimientos de este juego y tokens de acceso secreto

    game = Connect4()
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, connected

    watch_key = secrets.token_urlsafe(12)
    WATCH[watch_key] = game, connected

    try:
        # Envía los tokens de acceso secreto al navegador del primer jugador, donde
        # se utilizarán para crear enlaces de "join" y "watch".
        event = {
            "type": "init",
            "join": join_key,
            "watch": watch_key,
        }

        await websocket.send(json.dumps(event))
        # Recibe y procesa los movimientos del primer jugador.
        await play(websocket, game, PLAYER1, connected)

    finally:
        del JOIN[join_key]
        del WATCH[watch_key]


async def join(websocket, join_key):
    """
    Manejar una conexión del segundo jugador: unirse a un juego existente

    """

    # Encuentra el juego Connect Four
    try:
        game, connected = JOIN[join_key]  # valor es una tupla.

    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Registro de conexiones para recibir movimientos de este juego.
    connected.add(websocket)

    try:
        # Envía el primer movimiento, en caso de que el primer jugador ya haya jugado.
        await replay(websocket, game)
        # Recibe y procesa los movimientos del segundo jugador.
        await play(websocket, game, PLAYER2, connected)

    finally:
        connected.remove(websocket)


async def watch(websocket, watch_key):
    """
    Maneja una conexión de un espectador: observa un juego existente.

    """
    # Encuentra el juego Connect Four.
    try:
        game, connected = WATCH[watch_key]

    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Registro de conexiones para recibir movimientos de este juego.
    connected.add(websocket)

    try:
        # Envía los movimientos previos en caso de que el juego haya comenzado.
        await replay(websocket, game)
        # Mantiene la conexión abierta pero no recibe ningún mensaje.
        await websocket.wait_closed()

    finally:
        connected.remove(websocket)


async def handler(websocket):
    """
    Maneja una conexión y despáchala de acuerdo a quién se está conectando.

    """

    # Recibir y analizar el evento “init” de la interfaz de usuario.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # Segundo jugador se une al juego.
        await join(websocket, event["join"])
    elif "watch" in event:
        # Un espectador observa un juego existente.
        await watch(websocket, event["watch"])
    else:
        # El primer jugador comienza un nuevo juego.
        await start(websocket)


async def main():
    async with websockets.serve(handler, "", 8001):
        print("Servidor Iniciado")
        await asyncio.Future()  # el servidor se está ejecutando siempre.


if __name__ == "__main__":
    asyncio.run(main())
