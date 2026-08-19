import os
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit


app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)


@app.route("/")
def home():

    return jsonify({
        "ok": True,
        "app": "LivePad Relay",
        "version": "0.1"
    })


@socketio.on("connect")
def handle_connect():

    print("Cliente conectado")

    emit(
        "relay_ready",
        {
            "ok": True,
            "message": "Conectado a LivePad Relay"
        }
    )


@socketio.on("disconnect")
def handle_disconnect():

    print("Cliente desconectado")


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