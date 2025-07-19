from const import *
import socket
import threading
from group import Group

clients = []
nicknames = []
rooms = {}  # {room_name: Group object}
client_room = {} # {cliente: room_name}

def server_input():
    """ 
        Envia uma mensagem do servidor para todos os clientes, independente da sala em que esteja
    """
    while True:
        try:
            msg = input()
            broadcast(f"{MAGENTA}[Servidor]:{DEFAULT} {msg}\n".encode())
        except:
            break

def broadcast(msg, sender_client=None, room_name=None):
    """ 
        Envia uma mensagem para todos os clientes em uma sala específica, exceto o remetente. 
    """
    
    # verifica se a sala existe e esta no dicionario de salas
    if room_name and room_name in rooms:
        
        # obtem o objeto Group e envia a mensagem para todos os participantes da sala, exceto
        # o participante que enviou a mensagem
        room = rooms[room_name]
        for client in room.participants:
            if client != sender_client:
                try:
                    client.send(msg)
                except:
                    client.close()
                    remove_client(client)
    
    # else:
    #     for client in clients:
    #          if client != sender_client:
    #             try:
    #                 client.send(msg)
    #             except:
    #                 client.close()
    #                 remove_client(client)

def remove_client(client):
    """ Remove um cliente do servidor e de qualquer sala em que esteja. """
    # remove ele se ele existe
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        nickname = nicknames.pop(index)
        
        # se ele pertencer a uma sala, tira ele da sala
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
    """ Lida com todas as mensagens de um cliente. """
    try:
        # recebe, antes de tudo, o nickanme do participante
        nickname = client.recv(BYTES).decode().strip()
        if not nickname:
            client.close()
            return
        nicknames.append(nickname)
        clients.append(client)

        print(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} entrou no chat.")
        client.send("Bem-vindo ao chat!\n".encode())
        client.send("Comandos disponíveis:\n\t1. /criar <nome_sala>\n\t2. /entrar <nome_sala>\n\t3. /sair\n\t4. /lista\n".encode())

        while True:
            try:
                # recebe a msg do cliente e interpreta se for um comando ou uma mensagem normal
                msg = client.recv(BYTES)
                if not msg:
                    break
                decoded = msg.decode().strip()
                if decoded.startswith('/'):
                    
                    # cria uma sala
                    if decoded.lower().startswith('/criar '):
                        room_name = decoded.split(' ', 1)[1]
                        if room_name in rooms:
                            client.send(f"{MAGENTA}[Servidor]{DEFAULT} A sala '{room_name}' já existe.\n".encode())
                        else:
                            new_room = Group(room_name)
                            rooms[room_name] = new_room
                            new_room.add_participant(client)
                            client_room[client] = room_name
                            client.send(f"{MAGENTA}[Servidor]{DEFAULT} Sala '{room_name}' criada e você entrou nela.\n".encode())
                            broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} criou e entrou na sala '{room_name}'.\n".encode(), sender_client=client, room_name=room_name)

                    # entra em uma sala
                    elif decoded.lower().startswith('/entrar '):
                        room_name = decoded.split(' ', 1)[1]
                        if room_name not in rooms:
                            client.send(f"{MAGENTA}[Servidor]{DEFAULT} A sala '{room_name}' não existe.\n".encode())
                        else:
                            if client in client_room:
                                old_room_name = client_room[client]
                                rooms[old_room_name].remove_participant(client)
                                broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} saiu da sala {old_room_name}.\n".encode(), room_name=old_room_name)

                            rooms[room_name].add_participant(client)
                            client_room[client] = room_name
                            client.send(f"{MAGENTA}[Servidor]{DEFAULT} Você entrou na sala '{room_name}'.\n".encode())
                            broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} entrou na sala.\n".encode(), sender_client=client, room_name=room_name)

                    # sair da sala
                    elif decoded.lower() == '/sair':
                        if client in client_room:
                            room_name = client_room[client]
                            rooms[room_name].remove_participant(client)
                            broadcast(f"{MAGENTA}[Servidor]{DEFAULT} {nickname} saiu da sala.\n".encode(), room_name=room_name)
                            client.send(f"{MAGENTA}[Servidor]{DEFAULT} Você saiu da sala '{room_name}'.\n".encode())

                            if not rooms[room_name].participants:
                                del rooms[room_name]
                            
                            del client_room[client]
                        else:
                            client.send(f"{MAGENTA}[Servidor]{DEFAULT} Você não está em nenhuma sala.\n".encode())

                    # lista as salas
                    elif decoded.lower() == '/lista':
                        if not rooms:
                            client.send(f"{MAGENTA}[Servidor]{DEFAULT} Não há salas ativas.\n".encode())
                        else:
                            room_list = "\n".join(rooms.keys())
                            client.send(f"{MAGENTA}[Servidor]{DEFAULT} Salas disponíveis:\n{room_list}\n".encode())
                    
                else:
                    print(f"[{room_name}] {nickname}: {decoded}")

                    if client in client_room:
                        room_name = client_room[client]
                        broadcast(f"[{room_name}] {nickname}: {decoded}\n".encode(), sender_client=client, room_name=room_name)
                    else:
                    
                        client.send(f"{MAGENTA}[Servidor]{DEFAULT} Você precisa entrar em uma sala para conversar. Use /entrar <nome_sala> ou /criar <nome_sala>.\n".encode())

            except:
                break

    finally:
        remove_client(client)

def start_Servidor():
    Servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    Servidor.bind((HOST, PORT))
    Servidor.listen()
    print(f"{MAGENTA}[Servidor]{DEFAULT} Servidor iniciado em {HOST}:{PORT}")

    input_thread = threading.Thread(target=server_input, daemon=True)
    input_thread.start()

    try:
        while True:
            client, _ = Servidor.accept()
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
            
    except KeyboardInterrupt:
        print(f"\n{MAGENTA}[Servidor]{DEFAULT} Encerrando servidor...")

    finally:
        for c in clients:
            c.close()
        Servidor.close()
        print(f"{MAGENTA}[Servidor]{DEFAULT} Finalizado com sucesso.")

if __name__ == '__main__':
    start_Servidor()