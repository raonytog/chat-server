from const import *
import socket
import threading

clients = []
nicknames = []

def server_input():
    """ Envia uma mensagem do servidor para todos os clientes """
    while True:
        try:
            msg = input()
            broadcast(f"[Servidor]: {msg}\n".encode())

        except:
            break


def broadcast(msg, sender=None):
    """ Envia uma mensagem para todos os clientes, exceto o remetente (se especificado). """
    for client in clients:
        if client != sender: # transmite a todos, menos a quem enviou a msg (obviamente)
            try:
                client.send(msg)
                
            except:
                client.close()
                if client in clients:
                    index = clients.index(client)
                    clients.remove(client)
                    nicknames.pop(index)

def handle_client(client):
    """ Lida com todas as mensagens de um cliente. """
    try:
        # tenta, primeiro, ler o nickname do usuario e o adiciona as respectivas listas
        nickname = client.recv(BYTES).decode().strip()
        if not nickname:
            client.close()
            return
        nicknames.append(nickname)
        clients.append(client)

        # transmite os comandos disponiveis aos clientes e informa que o usuario entrou no servidor
        print(f"[SERVER] {nickname} entrou no chat.")
        broadcast(f"[SERVER] {nickname} entrou no chat.".encode())
        client.send("Comandos disponíveis:\n\t1. /criar <nome_sala>\n\t2. /entrar <nome_sala>\n\t3. /sair\n\t4. /lista\n".encode())

        while True:
            try:
                # recebe a mensagem do client e verifica oq ele tentou enviar
                msg = client.recv(BYTES)
                if not msg:
                    break
                decoded = msg.decode().strip()

                # pronto
                if decoded.lower() == '/lista':
                    client.send(f"[SERVER] Usuários conectados:\n{nicknames}\n".encode())
                    
                # nao pronto
                elif decoded.lower() == '/entrar':
                    client.send(f"[SERVER] {nickname} entrou na conversa\n".encode())
                    
                # nao pronto
                elif decoded.lower() == '/cria':
                    client.send(f"[SERVER] sala <nome_sala> criada por {nickname}\n".encode())
                    
                # pronto
                elif decoded.lower() == '/sair':
                    client.send(f"[SERVER] {nickname} saiu da sala <nome_sala>\n".encode())
                    client.close()
                
                # pronto
                #envia a mensagem de fato
                else:
                    print(f"{nickname}: {decoded}")
                    broadcast(f"{nickname}: {decoded}\n".encode(), sender=client)

            except:
                break

    finally:
        if client in clients:
            index = clients.index(client)
            left_nick = nicknames[index]
            print(f"{left_nick} saiu do chat.")
            clients.remove(client)
            nicknames.remove(left_nick)
            broadcast(f"[SERVER] {left_nick} saiu do chat.\n".encode())
            client.close()

def start_server():
    # estabelece o servidor e garante que o endereco estara livre em breve
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVIDOR] Servidor iniciado em {HOST}:{PORT}")

    # servidor transmite mensagens para os clientes
    input_thread = threading.Thread(target=server_input, daemon=True)
    input_thread.start()

    try:
        while True:
            client, _ = server.accept()
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
            
    except KeyboardInterrupt:
        print("[SERVIDOR] Encerrando servidor...")
        
    finally:
        for c in clients:
            c.close()
        server.close()
        print("[SERVIDOR] Finalizado com sucesso.")


if __name__ == '__main__':
    start_server()