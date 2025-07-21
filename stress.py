import socket, ssl, threading, time
from const import HOST, PORT, BYTES

NUM_USERS = 1000
USERS_PER_ROOM = 20

def client_simulation(user_id):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        sock.connect((HOST, PORT))
        ssl_sock = context.wrap_socket(sock, server_hostname=HOST)

        # Login
        ssl_sock.send(f"/login user{user_id} senha{user_id}\n".encode())
        time.sleep(0.01)

        # Determina a sala com base no índice do usuário
        room_id = user_id // USERS_PER_ROOM + 1
        room_name = f"sala{room_id}"

        # Cria a sala se for o primeiro da faixa
        if user_id % USERS_PER_ROOM == 0:
            ssl_sock.send(f"/criar {room_name}\n".encode())
            print(f"[user{user_id}] Criou a sala: {room_name}")
        else:
            time.sleep(0.02)
            ssl_sock.send(f"/entrar {room_name}\n".encode())
            print(f"[user{user_id}] Entrou na sala: {room_name}")

        time.sleep(0.03)

        # Envia mensagem
        msg = f"Olá de user{user_id} na {room_name}!"
        ssl_sock.send(f"{msg}\n".encode())
        print(f"[user{user_id}] Enviou mensagem: {msg}")

        time.sleep(0.05)

        ssl_sock.close()
        print(f"[user{user_id}] Desconectado.")
    except Exception as e:
        print(f"[Erro] user{user_id}: {e}")

# Criando e iniciando threads
threads = []

for i in range(NUM_USERS):
    t = threading.Thread(target=client_simulation, args=(i,))
    threads.append(t)
    t.start()
    time.sleep(0.005)  # espaçamento mínimo para aliviar carga de conexão

# Espera todas as threads finalizarem
for t in threads:
    t.join()

print("Teste de estresse com 1000 usuários concluído.")
