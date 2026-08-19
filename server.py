import os

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit


APP_NAME = "LivePad Relay"
APP_VERSION = "0.4"


# =========================================================
# APP
# =========================================================

app = Flask(__name__)


# =========================================================
# CORS
# =========================================================

@app.after_request
def add_cors_headers(response):

    response.headers[
        "Access-Control-Allow-Origin"
    ] = "*"

    response.headers[
        "Access-Control-Allow-Headers"
    ] = "Content-Type"

    response.headers[
        "Access-Control-Allow-Methods"
    ] = "GET, OPTIONS"

    return response


# =========================================================
# SOCKET.IO
# =========================================================

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="gevent"
)


# =========================================================
# COMPANIONS
# =========================================================

# pairing_code -> socket id
companions = {}

# socket id -> pairing_code
socket_companions = {}


# =========================================================
# HTTP
# =========================================================

@app.route("/")
def home():

    return jsonify({
        "ok": True,
        "app": APP_NAME,
        "version": APP_VERSION,
        "companions_online":
            len(companions)
    })


@app.route(
    "/api/companion/<pairing_code>/status"
)
def companion_status(
    pairing_code
):

    pairing_code = (
        str(pairing_code)
        .strip()
        .upper()
    )


    socket_id = companions.get(
        pairing_code
    )


    return jsonify({
        "ok": True,
        "pairing_code":
            pairing_code,
        "online":
            socket_id is not None
    })


# =========================================================
# SOCKET EVENTS
# =========================================================

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
            "version":
                APP_VERSION
        }
    )


@socketio.on(
    "companion_register"
)
def handle_companion_register(
    data
):

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

        current_socket = (
            companions.get(
                pairing_code
            )
        )


        if (
            current_socket
            ==
            socket_id
        ):

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


# =========================================================
# MAIN
# =========================================================

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