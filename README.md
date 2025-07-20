# Chat-Server
Este repositório é destinado para a disciplina de redes, para o trabalho 2. O objetivo é criar um simples sistema de bate-papo utilizando conexões TCP para entrega das mensagens para diversos clientes.

## Tecnologias utilizadas
1. Python3
2. Makefile

## Como executar 
### Requisitos:
1. Possuir a python3 instalado
2. Bibliotecas de threading, socket, time e sys instaladas

### Instruções de execução
Digitar no terminal:
```bash
 make sv
``` 
Abrir um novo terminal ou mais no mesmo diretório e fornecer o comando:
```bash
make cl
```
Em cada terminal será possível fornecer o nome de usuário e sua senha.<br>
Ao logar, pode-se criar uma sala ou entrar em uma existente.<br>
Por fim, converse!

## Como testar
```bash
make stress
```

## Funcionalidades implementadas
[x] Mensagens entregues apenas para os usuários da mesma sala e o servidor.
[x] Criar salas.
[x] Listagem de salas.
[x] Trocar/Sair da sala: Trocar de sala basta entrar em outra que o servidor já expulsa o usuário da sala atual. Para sair da sala, basta parar a aplicação. 
[x] Sair da aplicação.
[x] Autenticação SSL.
[x] Salas pública e salas privadas.
[x] Suporte a múltiplas salas.

## Possíveis melhorias 
1. Interface gráfica



