import socket
import threading
import json

PORT = 5555
HOST = '0.0.0.0' # Listen on all network interfaces
BUFFER = 4096

clients = []
clients_lock = threading.Lock()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    nickname = ""
    try:
        # First message expected is the nickname as a raw string
        nickname = conn.recv(BUFFER).decode('utf-8')
        if not nickname:
            raise Exception("Nickname not received")
        print(f"[{addr}] Nickname accepted: {nickname}")
        
        with clients_lock:
            clients.append(conn)

        while True:
            # Receive data up to BUFFER size
            data = conn.recv(BUFFER)
            if not data:
                break # Client disconnected
            
            # Print the received message to the server console for logging
            try:
                msg = json.loads(data.decode('utf-8'))
                print(f"[{addr}] {msg.get('sender', 'Unknown')}: {msg.get('text', '')}")
            except json.JSONDecodeError:
                print(f"[{addr}] Received malformed JSON")
            
            # Broadcast the received message to all connected clients
            broadcast(data)
            
    except Exception as e:
        print(f"[ERROR] {addr} handling error: {e}")
    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

def broadcast(message):
    """
    Sends a message to all connected clients.
    """
    with clients_lock:
        for client in clients:
            try:
                client.send(message)
            except Exception as e:
                print(f"[BROADCAST ERROR] Could not send to a client: {e}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow port reuse if server is restarted quickly
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server.bind((HOST, PORT))
    server.listen()
    print(f"[STARTING] Server is listening on {HOST}:{PORT}")
    
    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\n[STOPPING] Server is shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
