from const import *
import socket
import threading

def receive_messages(sock, stop_event):
    """Recebe mensagens do servidor enquanto a conexão estiver ativa."""
    while not stop_event.is_set():
        try:
            msg = sock.recv(BYTES).decode().rstrip()
            if not msg:
                print("Servidor encerrou a conexão")
                stop_event.set()
                break
            print(msg)
        except:
            break

def send_messages(sock, nickname, stop_event):
    """Envia mensagens digitadas pelo usuário para o servidor."""
    try:
        sock.send(nickname.encode())
    except:
        print("Nickname não enviado.")
        stop_event.set()
        return

    while not stop_event.is_set():
        try:
            msg = input('')
            if msg.lower() == '/sair':
                stop_event.set()
                sock.close()
                break
            sock.send(msg.encode())
        except:
            print("Falha ao enviar a mensagem")
            stop_event.set()
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Falha ao conectar com o servidor.")
        return

    nickname = input("Nickname: ")
    stop_event = threading.Event()

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, stop_event), daemon=True)
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(client_socket, nickname, stop_event))
    send_thread.start()
    send_thread.join()
    
    stop_event.set()
    print(f"{nickname} foi desconectado.")

if __name__ == '__main__':
    start_client()