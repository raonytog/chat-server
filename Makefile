all:
	clear
	gnome-terminal &
	python3 server.py

tln:
	telnet 127.0.0.1 65432