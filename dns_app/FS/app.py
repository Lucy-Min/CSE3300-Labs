
from flask import Flask, request
import socket

app = Flask(__name__)


def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@app.route("/register", methods=["PUT"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return "Invalid JSON", 400

    required = ["hostname", "ip", "as_ip", "as_port"]
    if any(not data.get(key) for key in required):
        return "Missing parameters", 400

    try:
        as_port = int(data["as_port"])
        message = (
            "TYPE=A\n"
            f"NAME={data['hostname']} VALUE={data['ip']} TTL=10\n"
        )

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(5)
            sock.sendto(
                message.encode(),
                (data["as_ip"], as_port)
            )
            response, _ = sock.recvfrom(1024)

        if response.decode().strip() != "Registered":
            return "Registration failed", 502

        return "Registered successfully", 201

    except (ValueError, OSError, socket.timeout):
        return "Registration failed", 502


@app.route("/fibonacci", methods=["GET"])
def get_fibonacci():
    number = request.args.get("number")

    try:
        n = int(number)
        if n < 0:
            return "Invalid number", 400
    except (ValueError, TypeError):
        return "Invalid number", 400

    return str(fibonacci(n)), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
