from const import *
import socket, ssl, threading
from group import Group

clients, nicknames = [], []
rooms, client_room, users = {}, {}, {}

def server_input():
    while True:
        try:
            msg = input()
            broadcast(f"{MAGENTA}[Servidor]:{DEFAULT} {msg}\n".encode())
        except:
            break

def broadcast(msg, sender_client=None, room_name=None):
    target = rooms[room_name].participants if room_name and room_name in rooms else clients
    for cli in target:
        if cli == sender_client: continue
        try:
            cli.send(msg)
        except:
            cli.close()
            remove_client(cli)

def remove_client(cli):
    if cli in clients:
        idx = clients.index(cli)
        nickname = nicknames[idx]
        clients.pop(idx); nicknames.pop(idx)
        if cli in client_room:
            r = client_room.pop(cli)
            rooms[r].remove_participant(cli)
            if not rooms[r].participants: rooms.pop(r)
            broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} saiu da sala {r}.\n".encode(), room_name=r)
        print(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} desconectou.")
        broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} desconectou.\n".encode())
        cli.close()

def handle_client(cli):
    try:
        # -------- login loop --------
        authed = False
        while not authed:
            try:
                raw = cli.recv(BYTES).decode().strip()
            except (ConnectionResetError, ssl.SSLError):
                return
            if not raw: return
            if raw.lower().startswith('/login '):
                parts = raw.split(' ', 2)
                if len(parts) < 3:
                    cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Formato: /login <user> <senha>\n".encode()); continue
                user, pwd = parts[1], parts[2]
                if user in users and users[user] != pwd:
                    cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Senha incorreta.\n".encode()); continue
                users.setdefault(user, pwd)
                nicknames.append(user); clients.append(cli)
                authed, nickname = True, user
                cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Autenticado.\n".encode())
                broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {user} entrou no chat.\n".encode(), sender_client=cli)
            else:
                cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Faça login primeiro: /login <user> <senha>\n".encode())

        cli.send("Comandos:\n/criar <sala> [senha]\n/entrar <sala> [senha]\n/sair\n/lista\n".encode())

        # -------- loop de mensagens --------
        while True:
            try:
                msg = cli.recv(BYTES)
            except (ConnectionResetError, ssl.SSLError):
                break
            if not msg: break
            decoded = msg.decode().strip()

            if decoded.startswith('/'):
                if decoded.lower().startswith('/criar '):
                    rn, pw = (decoded.split(' ', 2) + [None, None])[1:3]
                    if rn in rooms:
                        cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Sala já existe.\n".encode())
                    else:
                        rooms[rn] = Group(rn, pw)
                        rooms[rn].add_participant(cli); client_room[cli] = rn
                        cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Sala {rn} criada.\n".encode())
                        broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} criou a sala {rn}.\n".encode(), sender_client=cli, room_name=rn)

                elif decoded.lower().startswith('/entrar '):
                    rn, pw = (decoded.split(' ', 2) + [None, None])[1:3]
                    if rn not in rooms:
                        cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Sala inexistente.\n".encode())
                    elif not rooms[rn].check_access(pw):
                        cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Senha incorreta.\n".encode())
                    else:
                        if cli in client_room:
                            old = client_room[cli]
                            rooms[old].remove_participant(cli)
                            broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} saiu da sala.\n".encode(), room_name=old)
                        rooms[rn].add_participant(cli); client_room[cli] = rn
                        cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Você entrou em {rn}.\n".encode())
                        broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} entrou.\n".encode(), sender_client=cli, room_name=rn)

                elif decoded.lower() == '/sair':
                    if cli in client_room:
                        r = client_room.pop(cli)
                        rooms[r].remove_participant(cli)
                        broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} saiu da sala.\n".encode(), room_name=r)
                        cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Você saiu de {r}.\n".encode())
                        if not rooms[r].participants: rooms.pop(r)
                    else:
                        cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Você não está em sala.\n".encode())

                elif decoded.lower() == '/lista':
                    txt = "Sem salas ativas." if not rooms else "Salas:\n" + "\n".join(rooms)
                    cli.send(f"{MAGENTA}[Servidor]{DEFAULT} {txt}\n".encode())

            else:
                if cli in client_room:
                    r = client_room[cli]
                    broadcast(f"[{r}] {nickname}: {decoded}\n".encode(), sender_client=cli, room_name=r)
                else:
                    cli.send(f"{MAGENTA}[Servidor]{DEFAULT} Entre em uma sala.\n".encode())
    finally:
        remove_client(cli)

def start_Servidor():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT)); srv.listen()

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERTFILE, KEYFILE)

    print(f"{MAGENTA}[Servidor]{DEFAULT} TLS ativo em {HOST}:{PORT}")
    threading.Thread(target=server_input, daemon=True).start()

    try:
        while True:
            cli, _ = srv.accept()
            try:
                cli_ssl = ctx.wrap_socket(cli, server_side=True)
            except (ssl.SSLError, OSError):
                cli.close(); continue
            threading.Thread(target=handle_client, args=(cli_ssl,), daemon=True).start()
    except KeyboardInterrupt:
        print(f"\n{MAGENTA}[Servidor]{DEFAULT} Encerrando...")
    finally:
        for c in clients: c.close()
        srv.close()

if __name__ == "__main__":
    start_Servidor()
