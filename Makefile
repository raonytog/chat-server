# parâmetros do teste de estresse
MAX_USERS     := 1000
MAX_ROOMS     := 50
MAX_MESSAGES  := 10

.PHONY: sv cl stress tln

# servidor
sv:
	@clear
	python3 server.py

# cliente
cl:
	@clear
	python3 client.py

# stress
stress:
	@clear
	python3 stress.py $(MAX_USERS) $(MAX_ROOMS) $(MAX_MESSAGES)

# telnet
tln:
	telnet 127.0.0.1 65432
