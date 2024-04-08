# websocketpython2
En esta segunda parte , conectáremos un segundo navegador; podemos jugar desde diferentes navegadores en una red local.

En la primera parte, abrimos una conexión WebSocket desde un navegador a un servidor e intercambiamos eventos para realizar movimientos. El estado del juego se almacenó en una instancia de la clase Connect4, a la que se hace referencia como una variable local en la rutina del controlador de conexión.

Ahora abriremos dos conexiones WebSocket desde dos navegadores separados, uno para cada jugador, al mismo servidor para poder jugar el mismo juego. Esto requiere mover el estado del juego a un lugar donde ambas conexiones puedan acceder a él.