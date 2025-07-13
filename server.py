from const import *
import socket
import select
import threading

def finish_chat(msg):
    return msg.strip().lower() == 'end'

def is_server(notified_socket, server_socket):
    return notified_socket == server_socket

def is_client(notified_socket, server_socket):
    return not is_server(notified_socket, server_socket)
    
def max_client_reached(clients):
    return len(clients) >= MAX_CLIENTS

def receive_msg(client_socket, client_address):
    while True:
        msg = client_socket.recv(BYTES)
        if not msg:
            print(f'Conexão encerrada por {client_address}')
            break

        msg_decoded = msg.decode()
        print(f'(s) Cliente {client_address[1]}: {msg_decoded}', end='')
        if finish_chat(msg_decoded):
            print(f'Encerrando conexão com {client_address[0]}:{client_address[1]}.')
            break
        
    client_socket.close()
    
def send_msg(client_socket, client_address, receiver_thread):
    while True:
        msg = input('Servidor: ')
        client_socket.sendall(msg.encode())
        if finish_chat(msg):
            print(f'Encerrando conexão com {client_address[0]}:{client_address[1]}.')
            break
        
    receiver_thread.join()
    client_socket.close()

def handle_client(client_socket, client_address):    
    receiver_thread = threading.Thread(target=receive_msg, args=(client_socket, client_address))
    receiver_thread.start()
    
    send_msg(client_socket, client_address, receiver_thread)
    
# Função principal para iniciar o servidor
def start_server():
    # esse bloco inicia o socket do servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f'Servidor iniciado e escutando em {HOST}:{PORT}')
    
    read_sockets = []
    sockets = []
    threads = []
    clients = {}

    sockets.append(server_socket)
    while True:
        read_sockets, _, _ = select.select(sockets, [], [])
        
        for notified_socket in read_sockets:
            if is_client(notified_socket, server_socket):
                msg = notified_socket.recv(1024)
                msg_decoded = msg.decode()
                print(f'{msg_decoded}', end='')
                
            if is_server(notified_socket, server_socket) and max_client_reached(clients):
                print('Número máximo de clientes alcançado!')
                
            else: # é servidor e tem menos clientes doq o maximo
                client_socket, client_address = server_socket.accept()
                sockets.append(client_socket)
                clients[client_socket] = client_address
                
                client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                client_thread.start()
                threads.append(client_thread)

if __name__ == '__main__':
    start_server()