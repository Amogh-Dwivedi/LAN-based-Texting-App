import socket
import threading
import json
import sqlite3
from datetime import datetime

PORT = 5555
BUFFER = 4096


def init_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            sender    TEXT,
            text      TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message(sender, text, timestamp):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (sender, text, timestamp) VALUES (?, ?, ?)",
        (sender, text, timestamp)
    )
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT sender, text, timestamp FROM messages ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"sender": r[0], "text": r[1], "timestamp": r[2]} for r in rows]


class ChatClient:
    def __init__(self):
        self.sock = None
        self.nickname = ""
        self.server_ip = ""
        self.connected = False
        self.on_message_received = None
        init_db()

    def connect(self, server_ip, nickname):
        self.nickname = nickname
        self.server_ip = server_ip
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((server_ip, PORT))
            self.connected = True
            self.sock.send(nickname.encode("utf-8"))
            listener = threading.Thread(target=self._listen, daemon=True)
            listener.start()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            return False

    def _listen(self):
        while self.connected:
            try:
                raw = self.sock.recv(BUFFER)
                if not raw:
                    self.connected = False
                    break
                msg = json.loads(raw.decode("utf-8"))
                save_message(msg["sender"], msg["text"], msg["timestamp"])
                if self.on_message_received:
                    self.on_message_received(msg)
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(f"Listen error: {e}")
                self.connected = False
                break

    def send(self, text):
        if not self.connected or not text.strip():
            return False
        msg = {
            "sender": self.nickname,
            "text": text.strip(),
            "timestamp": datetime.now().strftime("%H:%M")
        }
        try:
            self.sock.send(json.dumps(msg).encode("utf-8"))
            return True
        except Exception as e:
            print(f"Send error: {e}")
            self.connected = False
            return False

    def disconnect(self):
        self.connected = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass


if __name__ == "__main__":
    ip = input("Server IP: ").strip()
    name = input("Nickname: ").strip()

    client = ChatClient()

    def print_message(msg):
        print(f"\n[{msg['timestamp']}] {msg['sender']}: {msg['text']}")

    client.on_message_received = print_message

    if client.connect(ip, name):
        print("Connected! Type 'quit' to exit.\n")
        while True:
            text = input()
            if text.lower() == "quit":
                break
            client.send(text)
        client.disconnect()
    else:
        print("Failed to connect.")