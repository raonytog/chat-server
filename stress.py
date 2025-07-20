import socket
import ssl
import threading
import time
import sys
import random
from const import *

room_creation_lock = threading.Lock()
rooms_created = set()

def client_receiver(sock, stop_event):
    while not stop_event.is_set():
        try:
            sock.settimeout(1.0)
            if not sock.recv(BYTES):
                break
        except:
            continue

def run_stress_client(client_id, num_rooms, messages_per_bot):
    try:
        base = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        base.connect((HOST, PORT))
        client_socket = context.wrap_socket(base, server_hostname=HOST)

        nickname = f"Bot_{client_id}"
        client_socket.send(f"/login {nickname} pwd".encode())
        time.sleep(0.05)

        stop_event = threading.Event()
        threading.Thread(target=client_receiver, args=(client_socket, stop_event)).start()

        room_name = f"Sala_Estresse_{client_id % num_rooms}"
        with room_creation_lock:
            if room_name not in rooms_created:
                cmd = f"/criar {room_name} priv"
                rooms_created.add(room_name)
            else:
                cmd = f"/entrar {room_name} priv"
        client_socket.send(cmd.encode())
        time.sleep(0.1)

        for i in range(messages_per_bot):
            msg = f"Olá da {room_name} {i+1}"
            client_socket.send(msg.encode())
            time.sleep(random.uniform(0.1, 0.5))

        client_socket.send("/sair".encode())
        time.sleep(0.1)
        print(f"[{nickname}] ok")
    except:
        print(f"[{nickname}] erro")
    finally:
        stop_event.set()
        client_socket.close()

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    r = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    m = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    threads = []
    for i in range(n):
        time.sleep(0.01)
        t = threading.Thread(target=run_stress_client, args=(i, r, m))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

if __name__ == '__main__':
    main()
