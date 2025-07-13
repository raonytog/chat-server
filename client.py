from const import *
import socket
import select
import threading

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    
if __name__ == '__main__':
    start_client()