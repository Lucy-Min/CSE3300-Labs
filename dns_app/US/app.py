
from flask import Flask, request
import socket
import requests

app = Flask(__name__)


@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Missing parameters", 400

    try:
        n = int(number)
        if n < 0:
            return "Invalid number", 400

        message = f"TYPE=A\nNAME={hostname}\n"

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(5)
            sock.sendto(message.encode(), (as_ip, int(as_port)))
            response, _ = sock.recvfrom(1024)

        fields = {}
        for part in response.decode().split():
            if "=" in part:
                key, value = part.split("=", 1)
                fields[key] = value

        fs_ip = fields.get("VALUE")
        if not fs_ip:
            return "Hostname not found", 404

        result = requests.get(
            f"http://{fs_ip}:{int(fs_port)}/fibonacci",
            params={"number": n},
            timeout=5
        )

        return result.text, result.status_code

    except ValueError:
        return "Invalid parameters", 400
    except (OSError, requests.RequestException):
        return "Server communication failed", 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
