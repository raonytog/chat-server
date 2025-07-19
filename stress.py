# stress.py
import socket
import threading
import time
import sys
import random
from const import *

# Usamos um Lock para garantir que a criação da sala seja feita por apenas um bot
room_creation_lock = threading.Lock()
rooms_created = set()

def client_receiver(sock, stop_event):
    """Uma thread simples para cada cliente apenas para esvazgar o buffer de recebimento."""
    while not stop_event.is_set():
        try:
            sock.settimeout(1.0)  # Evita bloqueio infinito
            msg = sock.recv(BYTES)
            if not msg:
                break
        except socket.timeout:
            continue
        except:
            break

def run_stress_client(client_id, num_rooms, messages_per_bot):
    """
    Simula o comportamento de um cliente:
    1. Conecta ao servidor.
    2. Entra ou cria uma sala.
    3. Envia várias mensagens.
    4. Sai e desconecta.
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        # 1. Enviar nickname
        nickname = f"Bot_{client_id}"
        client_socket.send(nickname.encode())
        time.sleep(0.05) # Pequena pausa para o servidor processar

        # Thread para receber mensagens e evitar bloqueio
        stop_event = threading.Event()
        receiver_thread = threading.Thread(target=client_receiver, args=(client_socket, stop_event))
        receiver_thread.start()

        # 2. Determinar e entrar/criar a sala
        room_name = f"Sala_Estresse_{client_id % num_rooms}"
        
        with room_creation_lock:
            if room_name not in rooms_created:
                command = f"/criar {room_name}"
                rooms_created.add(room_name)
            else:
                command = f"/entrar {room_name}"
        
        client_socket.send(command.encode())
        time.sleep(0.1)

        # 3. Enviar múltiplas mensagens na sala
        for i in range(messages_per_bot):
            message = f"Olá da sala {room_name}! Mensagem {i+1}."
            client_socket.send(message.encode())
            time.sleep(random.uniform(0.1, 0.5)) # Simula um usuário digitando

        # 4. Sair da sala e desconectar
        client_socket.send("/sair".encode())
        time.sleep(0.1)
        
        print(f"[{nickname}] Teste concluído com sucesso.")

    except ConnectionRefusedError:
        print(f"[{nickname}] Falha ao conectar: Conexão recusada.")
    except Exception as e:
        print(f"[{nickname}] Erro: {e}")
    finally:
        if 'stop_event' in locals():
            stop_event.set()
        if 'receiver_thread' in locals():
            receiver_thread.join()
        if 'client_socket' in locals():
            client_socket.close()


def main():
    # Pega os argumentos da linha de comando ou usa valores padrão.
    num_clients = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 100
    num_rooms = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
    messages_per_bot = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 5

    print(f"Iniciando teste com {num_clients} clientes, em {num_rooms} salas, enviando {messages_per_bot} mensagens cada...")

    threads = []
    for i in range(num_clients):
        # Adiciona um pequeno delay para não sobrecarregar a criação de sockets
        time.sleep(0.01)
        thread = threading.Thread(target=run_stress_client, args=(i, num_rooms, messages_per_bot))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Teste de estresse finalizado.")

if __name__ == '__main__':
    main()