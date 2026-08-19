import os

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit


APP_NAME = "LivePad Relay"
APP_VERSION = "0.2"


app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="gevent"
)


# pairing_code -> socket id
companions = {}

# socket id -> pairing_code
socket_companions = {}


@app.route("/")
def home():

    return jsonify({
        "ok": True,
        "app": APP_NAME,
        "version": APP_VERSION,
        "companions_online": len(companions)
    })


@socketio.on("connect")
def handle_connect():

    print(
        "[RELAY] Cliente conectado:",
        request.sid
    )

    emit(
        "relay_ready",
        {
            "ok": True,
            "version": APP_VERSION
        }
    )


@socketio.on("companion_register")
def handle_companion_register(data):

    data = data or {}

    pairing_code = str(
        data.get(
            "pairing_code",
            ""
        )
    ).strip().upper()


    if not pairing_code:

        emit(
            "companion_registered",
            {
                "ok": False,
                "error":
                    "pairing_code requerido"
            }
        )

        return


    # Si ya había otro socket usando
    # ese código, reemplazamos la sesión.
    old_socket = companions.get(
        pairing_code
    )

    if old_socket:

        socket_companions.pop(
            old_socket,
            None
        )


    companions[
        pairing_code
    ] = request.sid

    socket_companions[
        request.sid
    ] = pairing_code


    print(
        "[RELAY] Companion online:",
        pairing_code
    )


    emit(
        "companion_registered",
        {
            "ok": True,
            "pairing_code":
                pairing_code
        }
    )


@socketio.on("disconnect")
def handle_disconnect():

    socket_id = request.sid

    pairing_code = (
        socket_companions.pop(
            socket_id,
            None
        )
    )


    if pairing_code:

        current_socket = companions.get(
            pairing_code
        )

        if current_socket == socket_id:

            companions.pop(
                pairing_code,
                None
            )


        print(
            "[RELAY] Companion offline:",
            pairing_code
        )

    else:

        print(
            "[RELAY] Cliente desconectado:",
            socket_id
        )


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    socketio.run(
        app,
        host="0.0.0.0",
        port=port
    )