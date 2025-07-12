from const import HOST, PORT, BYTES
import socket
import threading



def handle_client(connection, address):
    """_summary_
    
    Args:
        connection (_type_): socket connection
        address (_type_): client address 
    """
    
    print(f'Conectado a {address}')
    
    with connection:
        while True:
            # recebe os dados do cliente
            data = connection.recv(BYTES)
            if not data: break
            
            # decodifica a mensagem recebida
            message = data.decode()
            print(f'Message received {address}: {message}')
            
            # se a mensagem for 'fechar connection', encerra a connection
            if message.lower() == 'fechar connection':
                print(f' Finishing connection from {address}')
                break

            connection.sendall(data) 

    print(f'Connection lost {address}')

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f'Server in {HOST}:{PORT}')
        
        while True:
            connection, address = s.accept()
            thread = threading.Thread(target=handle_client, args=(connection, address))
            thread.start()
            print(f'Online threads: {threading.active_count() - 1}')
    
if __name__ == '__main__':
    start_server()

