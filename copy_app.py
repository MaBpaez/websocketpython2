#!/usr/bin/env python

import asyncio, websockets, json, itertools
from connect4 import PLAYER1, PLAYER2, Connect4


# Opción 1
# async def handler(websocket):
#     while True:
#         message = await websocket.recv()
#         print(message)


# Opción 2
# async def handler(websocket):
#     while True:
#         try:
#             message = await websocket.recv()
#         except websockets.ConnectionClosedOK:
#             break
#         print(message)


# Opción 3
# async def handler(websocket):
#     async for message in websocket:
#         print(message)


# Opción 4 (Enviar mensajes desde el servidor)
# async def handler(websocket):
#     for player, column, row in [
#         (PLAYER1, 3, 0),
#         (PLAYER2, 3, 1),
#         (PLAYER1, 4, 0),
#         (PLAYER2, 4, 1),
#         (PLAYER1, 2, 0),
#         (PLAYER2, 1, 0),
#         (PLAYER1, 5, 0),
#     ]:
#         event = {
#             "type": "play",
#             "player": player,
#             "column": column,
#             "row": row,
#         }

#         await websocket.send(json.dumps(event))
#         await asyncio.sleep(0.5)

#     event = {
#         "type": "win",
#         "player": PLAYER1,
#     }

#     await websocket.send(json.dumps(event))


async def handler(websocket):
    # Initialize a Connect Four game.
    game = Connect4()

    # Players take alternate turns, using the same browser.
    turns = itertools.cycle([PLAYER1, PLAYER2])
    player = next(turns)

    async for message in websocket:
        # Parse a "play" event from the UI.
        # We receive a str (a JSON string) and convert it into a python dictionary
        event = json.loads(message)
        assert event["type"] == "play"
        column = event["column"]

        try:
            # Play the move.
            row = game.play(player, column)
        except RuntimeError as exc:
            # Send an "error" event if the move was illegal.
            event = {"type": "error", "message": str(exc)}

            await websocket.send(json.dumps(event))
            continue

        # Send a "play" event to update the UI.
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        await websocket.send(json.dumps(event))

        # If move is winning, send a "win" event.
        if game.winner is not None:
            event = {"type": "win", "player": game.winner}
            await websocket.send(json.dumps(event))

        # Alternate turns.
        player = next(turns)


async def main():
    """
    handler es una corrutina que gestiona una conexión. Cuando un cliente se conecta,
    websockets llama handler con la conexión como argumento. Cuando handler termina,
    websockets cierra la conexión.

    El segundo argumento define las interfaces de red donde se puede acceder al servidor.
    Aquí, el servidor escucha en todas las interfaces, para que otros dispositivos en la
    misma red local puedan conectarse.

    El tercer argumento es el puerto en el que escucha el servidor.

    La invocación serve() como administrador de contexto asíncrono, en un bloque
    async with, garantiza que el servidor se apague correctamente al finalizar el
    programa.

    Para cada conexión, la corrutina handler() ejecuta un bucle infinito que recibe
    mensajes del navegador y los imprime.
    """

    async with websockets.serve(handler, "", 8001):
        print("Servidor Iniciado")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
