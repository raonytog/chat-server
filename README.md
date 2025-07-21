# Chat‑Server

Este repositório contém uma aplicação de bate‑papo simples para a disciplina de Redes (Trabalho 2). O sistema permite vários clientes trocarem mensagens em salas distintas sobre conexões TCP protegidas por TLS.

## Tecnologias utilizadas
1. Python 3
2. Makefile (atalhos para execução)

## Como executar

### Pré‑requisitos
1. Python 3 instalado
2. Bibliotecas padrão **threading**, **socket**, **ssl** (já inclusas em CPython)
3. Certificados `cert.pem` e `key.pem` válidos na raiz do projeto (podem ser gerados com `make cert`)

### Instruções
```bash
# Terminal 1 – servidor
make sv

# Terminal 2 ou + – cliente(s)
make cl
```
Após iniciar o cliente, informe **usuário** e **senha**. É possível criar ou entrar em salas e conversar.

## Como testar carga
```bash
make stress
```
O alvo executa um script que abre diversos clientes de forma automatizada para verificar estabilidade.

## Funcionalidades implementadas
* ✅ Mensagens entregues apenas para usuários da **mesma sala** e para o servidor
* ✅ Criação de salas públicas ou privadas (com senha)
* ✅ Listagem de salas ativas
* ✅ Troca de sala ou saída voluntária
* ✅ Encerramento gracioso da aplicação
* ✅ Conexão segura via TLS + autenticação simples (`/login <user> <senha>`)
* ✅ Suporte a múltiplas salas simultâneas

## Possíveis melhorias
* Interface gráfica
* Históricos persistentes em arquivo ou banco
---

## Descrição das Funções
A seguir, um panorama de cada função/ferramenta presente no código‑fonte:

### `server.py`
| Função                                                     | Responsabilidade                                                                                                                                                 | Passos principais                                                         |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **`server_input()`**                                       | Permite que o operador digite mensagens no terminal do servidor; as mensagens são enviadas para todos os clientes como avisos do sistema.                        | • Aguarda `input()`                                                       |
| • Chama `broadcast()` com a mensagem                       |                                                                                                                                                                  |                                                                           |
| **`broadcast(msg, sender_client=None, room_name=None)`**   | Encaminha `msg` para todos os sockets‑alvo. Se `room_name` for especificado, envia somente aos participantes daquela sala. Ignora o remetente (`sender_client`). | • Define alvo (`rooms[room_name].participants` ou lista global `clients`) |
| • Tenta `send()` em cada socket                            |                                                                                                                                                                  |                                                                           |
| • Em caso de erro, fecha socket e invoca `remove_client()` |                                                                                                                                                                  |                                                                           |
| **`remove_client(cli)`**                                   | Limpa todo o estado associado a `cli` quando ocorre desconexão.                                                                                                  | • Remove de `clients`/`nicknames`                                         |
| • Remove da sala atual (`client_room`)                     |                                                                                                                                                                  |                                                                           |
| • Exclui a sala se ficou vazia                             |                                                                                                                                                                  |                                                                           |
| • Anuncia saída aos demais                                 |                                                                                                                                                                  |                                                                           |
| **`handle_client(cli)`**                                   | Loop principal por cliente: autentica, interpreta comandos e repassa mensagens.                                                                                  | **Fases**:                                                                |

1. *Login* – exige `/login <user> <senha>`
2. Envia menu de comandos
3. Processa `/criar`, `/entrar`, `/sair`, `/lista`
4. Encaminha texto livre como chat da sala |
   \| **`start_Servidor()`** | Inicializa o socket TCP, aplica TLS, lança a thread de console e aceita conexões. | • Configura `socket` e `SSLContext`
   • `listen()` em `(HOST, PORT)`
   • Para cada nova conexão cria thread `handle_client`
   • Fecha tudo em `KeyboardInterrupt` |

### `client.py`
| Função                                   | Responsabilidade                                                                                                  |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **`receive_messages(sock, stop_event)`** | Thread que recebe mensagens do servidor e imprime até que `stop_event` seja acionado ou a conexão seja encerrada. |
| **`send_messages(sock, stop_event)`**    | Captura *input* do usuário, envia ao servidor e encerra quando digitar `/sair`.                                   |
| **`start_client()`**                     | Cria conexão TLS, envia comando de login, inicia as threads de envio/recepção e gerencia o encerramento limpo.    |

### `group.py`
| Função                                | Responsabilidade                                                          |
| ------------------------------------- | ------------------------------------------------------------------------- |
| **`__init__(name, password=None)`**   | Instancia uma nova sala (`Group`) com nome e senha opcionais.             |
| **`add_participant(participant)`**    | Adiciona o socket de um cliente à lista `participants`.                   |
| **`remove_participant(participant)`** | Remove o socket da sala se presente.                                      |
| **`check_access(password)`**          | Retorna `True` se a sala não possuir senha ou se `password` corresponder. |

### `const.py`
Arquivo de *constantes* globais utilizadas em servidor e cliente:

| Constante                     | Significado                                           |
| ----------------------------- | ----------------------------------------------------- |
| `HOST`, `PORT`                | Endereço IP e porta do servidor                       |
| `BYTES`                       | Tamanho máximo do *buffer* de recepção                |
| `CERTFILE`, `KEYFILE`         | Caminhos para o certificado e chave TLS               |
| `DEFAULT`, `VERDE`, `AZUL`, … | Sequências ANSI para colorir as mensagens no terminal |
---

💬 **Fluxo de execução simplificado**
1. O servidor (`server.py`) inicia, ativa TLS e aguarda conexões.
2. Cada cliente (`client.py`) estabelece handshake TLS, faz login e cria duas threads (envio/recepção).
3. Mensagens são roteadas pelo servidor somente entre participantes da mesma sala.
4. Ao sair (`/sair` ou fechar terminal), o cliente envia sinal, o servidor limpa o estado e notifica os demais.
---
