import socket
import threading
import sys

HOST = '127.0.0.1'  # localhost
PORT = 12345  # porta

"""
lock= threading.Lock()          # cria uma chave
lock_lista_clientes.acquire()   # cliente solicita a chave
lock_lista_clientes.release()   # cliente libera a chave
"""

clientes_lock = threading.Lock()
clientes_conectados = []

def adicionar_cliente(cliente_info):
        clientes_conectados.append(cliente_info)
        print(f"✅ Cliente adicionado: {cliente_info['nome_usuario']} {cliente_info['endereco']}")
        print(f"📊 Total de clientes conectados: {len(clientes_conectados)}")


def gerenciar_cliente(socket_cliente, endereco_cliente):
    with socket_cliente:
        # O 'with' habilita o socket do cliente dentro do bloco
        # quando o bloco terminar, o socket é fechado

        print(f"Conectado por {endereco_cliente}")

        # envia a solicitação do nome de usuário ao cliente
        pedir_nome_usuario = f"Olá, seja bem vindo! Por favor, informe o seu nome de usuário: "
        socket_cliente.sendall(pedir_nome_usuario.encode())

        # recebe o nome de usuário do cliente
        nome_usuario_data = socket_cliente.recv(1024)
        if not nome_usuario_data:
            print(f'O cliente {endereco_cliente} desconectou-se')
            return

        nome_usuario = nome_usuario_data.decode().strip()
        print(f'O nome de usuário recebido do cliente foi: {nome_usuario}')

        # Envia confirmação de boas-vindas
        mensagem_boas_vindas = f"Olá {nome_usuario}, bem-vindo ao servidor!"
        socket_cliente.sendall(mensagem_boas_vindas.encode())


        with clientes_lock:
            cliente_info = {
                "socket": socket_cliente,
                "endereco": endereco_cliente,
                "nome_usuario": nome_usuario
            }

        adicionar_cliente(cliente_info)


        while True:
            data = socket_cliente.recv(1024)
            if not data:
                break
            print(f"Recebido de {endereco_cliente}: {data.decode()}")
            data_resposta = f"Olá {data.decode().strip()}, bem vindo!"
            nome_usuario = data.decode().strip()
            socket_cliente.sendall(data_resposta.encode())



# programa principal
try:
    # O uso do 'with' garante que socket_servidor.close() seja chamado no final
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_servidor:
        socket_servidor.bind((HOST, PORT))
        socket_servidor.listen()
        # timeout para o socket do servidor ---
        socket_servidor.settimeout(1.0)
        print(f"✔ Servidor TCP iniciado em {HOST}:{PORT}...")


        while True:  # O loop principal do servidor
            try:
                socket_cliente, endereco_cliente = socket_servidor.accept()  # aceita a conexão do cliente

                # criar e iniciar a thread do cliente
                thread = threading.Thread(target=gerenciar_cliente, args=(socket_cliente, endereco_cliente))
                thread.start()

            except socket.timeout:
                # O 'continue' faz o loop 'while True' rodar novamente,
                # permitindo que o Python processe o sinal de KeyboardInterrupt (Ctrl+C).
                continue


except KeyboardInterrupt:
    print("\n⚠️ Servidor interrompido pelo terminal (Ctrl+C)")
    sys.exit()
except Exception as e:
    print(f" ❌ Erro no servidor: {e}")
finally:
    # O socket_servidor é fechado automaticamente ao sair do bloco 'with'
    print("\n\n============ Servidor encerrado ============\n\n")