all:
	gnome-terminal &
	python3 server.py

telnet:
	telnet 127.0.0.1 65432