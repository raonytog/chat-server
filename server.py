from const import *
import socket
import ssl
import threading
from group import Group

clients = []
nicknames = []
rooms = {}
client_room = {}
users = {}

def server_input():
    while True:
        try:
            msg = input()
            broadcast(f"{MAGENTA}[Servidor]:{DEFAULT} {msg}\n".encode())
        except:
            break

def broadcast(msg, sender_client=None, room_name=None):
    if room_name and room_name in rooms:
        room = rooms[room_name]
        for client in room.participants:
            if client != sender_client:
                try:
                    client.send(msg)
                except:
                    client.close()
                    remove_client(client)
    else:
        for client in clients:
            if client != sender_client:
                try:
                    client.send(msg)
                except:
                    client.close()
                    remove_client(client)

def remove_client(client):
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        nickname = nicknames.pop(index)
        if client in client_room:
            room_name = client_room[client]
            rooms[room_name].remove_participant(client)
            if not rooms[room_name].participants:
                del rooms[room_name]
            del client_room[client]
            broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} saiu da sala {room_name}.\n".encode(), room_name=room_name)
        print(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} desconectou.")
        broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} desconectou.\n".encode())
        client.close()

def handle_client(client):
    try:
        authed = False
        while not authed:
            raw = client.recv(BYTES).decode().strip()
            if not raw:
                client.close()
                return
            if raw.lower().startswith('/login '):
                parts = raw.split(' ', 2)
                if len(parts) < 3:
                    client.send(f"{MAGENTA}[Servidor]{DEFAULT} Formato: /login <user> <senha>\n".encode())
                    continue
                username, password = parts[1], parts[2]
                if username in users:
                    if users[username] != password:
                        client.send(f"{MAGENTA}[Servidor]{DEFAULT} Senha incorreta.\n".encode())
                        continue
                else:
                    users[username] = password
                nicknames.append(username)
                clients.append(client)
                client.send(f"{MAGENTA}[Servidor]{DEFAULT} Autenticado.\n".encode())
                broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {username} entrou no chat.\n".encode(), sender_client=client)
                authed = True
                nickname = username
            else:
                client.send(f"{MAGENTA}[Servidor]{DEFAULT} Faça login primeiro: /login <user> <senha>\n".encode())

        client.send("Comandos:\n/criar <sala> [senha]\n/entrar <sala> [senha]\n/sair\n/lista\n".encode())

        while True:
            msg = client.recv(BYTES)
            if not msg:
                break
            decoded = msg.decode().strip()
            if decoded.startswith('/'):
                if decoded.lower().startswith('/criar '):
                    parts = decoded.split(' ', 2)
                    room_name = parts[1]
                    password = parts[2] if len(parts) == 3 else None
                    if room_name in rooms:
                        client.send(f"{MAGENTA}[Servidor]{DEFAULT} Sala já existe.\n".encode())
                    else:
                        new_room = Group(room_name, password)
                        rooms[room_name] = new_room
                        new_room.add_participant(client)
                        client_room[client] = room_name
                        client.send(f"{MAGENTA}[Servidor]{DEFAULT} Sala {room_name} criada.\n".encode())
                        broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} criou a sala {room_name}.\n".encode(), sender_client=client, room_name=room_name)

                elif decoded.lower().startswith('/entrar '):
                    parts = decoded.split(' ', 2)
                    room_name = parts[1]
                    password = parts[2] if len(parts) == 3 else None
                    if room_name not in rooms:
                        client.send(f"{MAGENTA}[Servidor]{DEFAULT} Sala inexistente.\n".encode())
                    elif not rooms[room_name].check_access(password):
                        client.send(f"{MAGENTA}[Servidor]{DEFAULT} Senha incorreta.\n".encode())
                    else:
                        if client in client_room:
                            old_room = client_room[client]
                            rooms[old_room].remove_participant(client)
                            broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} saiu da sala.\n".encode(), room_name=old_room)
                        rooms[room_name].add_participant(client)
                        client_room[client] = room_name
                        client.send(f"{MAGENTA}[Servidor]{DEFAULT} Você entrou em {room_name}.\n".encode())
                        broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} entrou.\n".encode(), sender_client=client, room_name=room_name)

                elif decoded.lower() == '/sair':
                    if client in client_room:
                        room = client_room[client]
                        rooms[room].remove_participant(client)
                        broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} saiu da sala.\n".encode(), room_name=room)
                        client.send(f"{MAGENTA}[Servidor]{DEFAULT} Você saiu de {room}.\n".encode())
                        if not rooms[room].participants:
                            del rooms[room]
                        del client_room[client]
                    else:
                        client.send(f"{MAGENTA}[Servidor]{DEFAULT} Você não está em sala.\n".encode())

                elif decoded.lower() == '/lista':
                    if not rooms:
                        client.send(f"{MAGENTA}[Servidor]{DEFAULT} Sem salas ativas.\n".encode())
                    else:
                        lista = "\n".join(rooms.keys())
                        client.send(f"{MAGENTA}[Servidor]{DEFAULT} Salas:\n{lista}\n".encode())

            else:
                if client in client_room:
                    room = client_room[client]
                    broadcast(f"[{room}] {nickname}: {decoded}\n".encode(), sender_client=client, room_name=room)
                else:
                    client.send(f"{MAGENTA}[Servidor]{DEFAULT} Entre em uma sala.\n".encode())
    finally:
        remove_client(client)

def start_Servidor():
    Servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    Servidor.bind((HOST, PORT))
    Servidor.listen()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERTFILE, KEYFILE)
    print(f"{MAGENTA}[Servidor]{DEFAULT} TLS ativo em {HOST}:{PORT}")
    threading.Thread(target=server_input, daemon=True).start()
    try:
        while True:
            client, _ = Servidor.accept()
            client_ssl = context.wrap_socket(client, server_side=True)
            threading.Thread(target=handle_client, args=(client_ssl,)).start()
    except KeyboardInterrupt:
        print(f"\n{MAGENTA}[Servidor]{DEFAULT} Encerrando...")
    finally:
        for c in clients:
            c.close()
        Servidor.close()

if __name__ == '__main__':
    start_Servidor()
