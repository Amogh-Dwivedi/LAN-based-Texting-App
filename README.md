# LAN Texting App

A localized chat application built with Python sockets and a modern Discord-inspired UI using `customtkinter`. It features multi-client real-time messaging and SQLite-based persistent chat history.

## Features
* **Modern Dark UI**: A sleek, Discord-styled interface.
* **Real-time Messaging**: Socket-based multi-threaded server for instant message broadcasting.
* **Persistent Chat History**: Local `chat_history.db` SQLite database to retain previous conversations across sessions.
* **Profile Avatars**: Dynamic avatar fetching with built-in fallback mechanisms for user profiles.

## Prerequisites
Ensure you have Python 3 installed along with the following dependencies:

```bash
pip install customtkinter Pillow requests matplotlib
```
-----------------------------------------------------------------------------------------------------------------------------------------------------------

## Project Structure
* server.py: The multi-threaded socket server that handles client connections, accepts nicknames, and broadcasts JSON messages to all connected clients.

* client.py: The backend client logic handling the socket connection, message packaging/parsing, and SQLite database saving/retrieval.

* GUI.py: The main frontend executable utilizing CustomTkinter to render the UI, manage the client instance, and display the chat flow.

## How to Run
Start the Server: Open a terminal and run the server to listen for incoming connections.
```Bash
python server.py
```

Start the Client GUI: In a separate terminal (or multiple terminals for multiple clients), launch the user interface.
```Bash
python GUI.py
```

Enter your nickname when prompted and start chatting! (Note: The GUI is currently hardcoded to connect to localhost 127.0.0.1. To use this across a real LAN, update the IP address inside the prompt_login method in GUI.py to the server machine's actual local IP address.)
