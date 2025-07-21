from const import *
import socket
import ssl
import threading

def receive_messages(sock, stop_event):
    while not stop_event.is_set():
        try:
            msg = sock.recv(BYTES).decode().rstrip()
            if not msg:
                stop_event.set()
                break
            print(msg)
        except:
            break

def send_messages(sock, stop_event):
    while not stop_event.is_set():
        try:
            msg = input()
            if msg.lower() == '/sair':
                stop_event.set()
                sock.close()
                break
            sock.send(msg.encode())
        except:
            stop_event.set()
            break

def start_client():
    plain = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    try:
        plain.connect((HOST, PORT))
        client_socket = context.wrap_socket(plain, server_hostname=HOST)
    except:
        print("Falha na conexão.")
        return

    user = input("Usuário: ")
    pwd = input("Senha : ")
    client_socket.send(f"/login {user} {pwd}".encode())

    stop_event = threading.Event()
    threading.Thread(target=receive_messages, args=(client_socket, stop_event), daemon=True).start()
    send_messages(client_socket, stop_event)
    stop_event.set()
    print("Desconectado.")

if __name__ == '__main__':
    start_client()
