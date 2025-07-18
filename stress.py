# stress_test_client.py
import socket
import threading
import time
import sys
from const import *

def connect_client(client_id):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        nickname = f"Bot_{client_id}"
        client_socket.send(nickname.encode())
        time.sleep(0.1)
        client_socket.send(f"Olá, sou o cliente {client_id}!".encode())
        print(f"[Cliente {client_id}] Conectado e mensagem enviada com sucesso.")

        while True:
            try:
                msg = client_socket.recv(BYTES)
                if not msg:
                    break
            except:
                break

    except ConnectionRefusedError:
        print(f"[Cliente {client_id}] Falha ao conectar: Conexão recusada.")
    except Exception as e:
        print(f"[Cliente {client_id}] Erro: {e}")
    finally:
        client_socket.close()


def main():
    # Pega o número de clientes do primeiro argumento da linha de comando.
    # Se não for fornecido, o padrão é 100.
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        NUM_CLIENTS = int(sys.argv[1])
    else:
        NUM_CLIENTS = 100  # Valor padrão

    threads = []
    print(f"Iniciando teste com {NUM_CLIENTS} clientes...")

    for i in range(NUM_CLIENTS):
        time.sleep(0.01)
        thread = threading.Thread(target=connect_client, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Teste finalizado.")

if __name__ == '__main__':
    main()