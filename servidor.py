"""
===============================================================================
SISTEMA DE CHAT TCP - SERVIDOR
===============================================================================
Descrição: Servidor TCP que gerencia múltiplos clientes para o serviço de chat de texto
Autor: Gabriel Pinheiro, Renan Hurtado
Data: 2025-06-11
Versão: 1.2.0
"""

import socket
import threading
import sys
import keyboard

HOST = '127.0.0.1'  # localhost
PORT = 12345        # porta

clientes_lock = threading.Lock()
clientes_conectados = []


def adicionar_cliente(cliente_info):
    clientes_conectados.append(cliente_info)
    print("\n───────────────────────────────────────────────────────────────────")
    print(f"✅ Cliente adicionado: {cliente_info['nome_usuario']} {cliente_info['endereco']}")
    print(f"📊 Total de clientes conectados: {len(clientes_conectados)}")
    print("───────────────────────────────────────────────────────────────────\n")


def consultar_clientes_conectados():
    print("\n──────────────────────── CLIENTES CONECTADOS ───────────────────────\n")
    with clientes_lock:
        if not clientes_conectados:
            print("\nNenhum cliente conectado.\n")
        else:
            for cliente in clientes_conectados:
                print(f" {cliente['nome_usuario']:2} | 📫  {cliente['endereco']}")
            print("───────────────────────────────────────────────────────────────────\n")


def finalizar_servidor():
    print("Ctrl+Shift+S foi pressionado!")

keyboard.add_hotkey('ctrl+shift+b', consultar_clientes_conectados)

def gerenciar_cliente(socket_cliente, endereco_cliente):
    with socket_cliente:
        # O 'with' habilita o socket do cliente dentro do bloco
        # quando o bloco terminar, o socket é fechado

        print(f"Conectado por {endereco_cliente}")

        # envia a solicitação do nome de usuário ao cliente
        pedir_nome_usuario = f"\nOlá, seja bem vindo! Por favor, informe o seu nome de usuário: "
        socket_cliente.sendall(pedir_nome_usuario.encode())

        # recebe o nome de usuário do cliente
        nome_usuario_data = socket_cliente.recv(1024)
        if nome_usuario_data == '' or nome_usuario_data is None: # TODO: Não está funcionando
            print(f'O cliente {endereco_cliente} desconectou-se')
            return

        nome_usuario = nome_usuario_data.decode().strip()
        #print(f'O nome de usuário recebido do cliente foi: {nome_usuario}')

        # Envia confirmação de boas-vindas
        mensagem_boas_vindas = f"Olá {nome_usuario}, seu usuário foi criado com sucesso! ☕"
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
            print(f"Recebido de {nome_usuario}: {data.decode()}")
            data_resposta = f"Olá {data.decode().strip()}, seja bem vindo!"
            socket_cliente.sendall(data_resposta.encode())

            # verifica se uma combinação de tecla foi pressionada
            if keyboard.is_pressed('ctrl+shift+s'):
                finalizar_servidor()
            elif keyboard.is_pressed('ctrl+shift+b'):
                consultar_clientes_conectados()

# ┌───────────────────────────────────────┐
# │ PROGRAMA PRINCIPAL                    │
# └───────────────────────────────────────┘
try:
    # O uso do 'with' garante que socket_servidor.close() seja chamado no final
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_servidor:
        socket_servidor.bind((HOST, PORT))
        socket_servidor.listen()
        # timeout para o socket do servidor ---
        socket_servidor.settimeout(0.1)
        print(f"✔ Servidor TCP iniciado em {HOST}:{PORT}...\n")


        while True:  # O loop principal do servidor
            try:
                socket_cliente, endereco_cliente = socket_servidor.accept()  # aceita a conexão do cliente

                # criar e iniciar a thread do cliente
                thread = threading.Thread(target=gerenciar_cliente, args=(socket_cliente, endereco_cliente))
                thread.daemon = True  # Thread será finalizada automaticamente
                thread.start()

            except socket.timeout:
                # O 'continue' faz o loop 'while True' rodar novamente,
                # permitindo que o Python processe o sinal de KeyboardInterrupt (Ctrl+C).
                opcao_selecionada = ''
                continue


except KeyboardInterrupt:
    print("\n⚠️  Servidor interrompido pelo terminal (Ctrl+C)")
    sys.exit()
except Exception as e:
    print(f" ❌ Erro no servidor: {e}")
finally:
    # O socket_servidor é fechado automaticamente ao sair do bloco 'with'
    print("\n\n============ Servidor encerrado ============\n\n")
