
# Actividad no. 2-1

**Sockets y multihilos**

La Batalla Naval es un juego en línea multijugador. Se dispone de un arsenal amplio en el campo de batalla: barcos, aviones, bombarderos, minas, defensa antiaérea, radares y muchas cosas más. Coloca los barcos de diferentes tamaños en el campo de batalla, los aviones y las minas, y asalta el campo del enemigo; lanza los aviones para los bombardeos y trata de hundir los barcos de tu oponente.

Haga su proyecto en dos etapas:

## ETAPA 1.

Elabore una versión 1:1 del juego. Usa varios sockets. Luego descubre cómo cambiar la mecánica del juego para que puedan jugarlo más de dos personas.

## ETAPA 2.

Ahora diseña tu juego bajo los siguientes criterios de diseño:

1. Cree un servidor que escuche a los jugadores que quieran suscribirse a una partida activa. (Esto requerirá multihilos). El servicio deberá suscribir a los jugadores y asignarles un turno.

    1. Crea un hilo para escuchar y aceptar jugadores entrantes.

    2. Crea otro hilo para el juego en sí.

2. El punto 1.1 requiere que escuches las conexiones entrantes, las aceptes y pases las conexiones establecidas mediante un socket al hilo del juego.

3. El punto 1.2 requiere que tu juego pase por las conexiones (sockets) para hablar con ellos y mantener la mecánica del juego activa.

4. Refinado: Asegúrese de que el servicio limpie las conexiones cuando se apague. También, que cada vez que se cierre el servicio, sus conexiones se cierren adecuadamente. 

En cada etapa del desarrollo presente el caso de uso y el diagrama de interacciones.
Entregar:
1- Informe con el paso a paso del experimento.
2- Código disponible en plataformas colaborativas.
3- Video presentando el código y la ejecución de cada etapa. Máx. 12 minutos.