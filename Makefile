sv:
	clear
	python3 server.py

cl:
	clear
	python3 client.py

MAX_USER = 1030
stress:
	clear
	python3 stress.py ${MAX_USER}

tln:
	telnet 127.0.0.1 65432
	
