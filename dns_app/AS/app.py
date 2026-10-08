
import socket
import json
import os

PORT = 53533
DB_FILE = os.path.join(os.path.dirname(__file__), "records.json")


def load_records():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}


def save_records(records):
    with open(DB_FILE, "w") as f:
        json.dump(records, f)


def parse_message(message):
    fields = {}
    for part in message.replace("\n", " ").split():
        if "=" in part:
            key, value = part.split("=", 1)
            fields[key] = value
    return fields


def main():
    records = load_records()

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("0.0.0.0", PORT))

    print(f"AS running on UDP port {PORT}")

    while True:
        data, address = server.recvfrom(1024)
        fields = parse_message(data.decode())

        name = fields.get("NAME")
        record_type = fields.get("TYPE")

        if record_type != "A" or not name:
            response = "ERROR"
        elif "VALUE" in fields and "TTL" in fields:
            records[name] = {
                "VALUE": fields["VALUE"],
                "TTL": fields["TTL"]
            }
            save_records(records)
            response = "Registered"
        elif name in records:
            record = records[name]
            response = (
                f"TYPE=A\n"
                f"NAME={name} VALUE={record['VALUE']} "
                f"TTL={record['TTL']}\n"
            )
        else:
            response = "Not found"

        server.sendto(response.encode(), address)


if __name__ == "__main__":
    main()
