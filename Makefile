MAX_USER = 1000
MAX_ROOMS = 50
MAX_MESSAGES = 10

# servidor
sv:
	clear
	python3 server.py

# client
cl:
	clear
	python3 client.py

# stress
st: 
	clear
	python3 stress.py ${MAX_USER} ${MAX_ROOMS} ${MAX_MESSAGES}

# telnet
tln:
	telnet 127.0.0.1 65432
	
