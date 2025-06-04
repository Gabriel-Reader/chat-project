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
    #print("\n" + "─" * 67)
    print(f"✅ Cliente adicionado: {cliente_info['nome_usuario']} {cliente_info['endereco']}")
    print(f"📊 Total de clientes conectados: {len(clientes_conectados)}")
    print("─" * 67 + "\n")


def remover_cliente(cliente_info):
    with clientes_lock:
        if cliente_info in clientes_conectados:
            print(f"O usuário {cliente_info['nome_usuario']} se desconectou.")
            clientes_conectados.remove(cliente_info)


def consultar_clientes_conectados():
    print("\n─────────────────────── CLIENTES CONECTADOS ───────────────────────\n")
    with clientes_lock:
        if not clientes_conectados:
            print("❌ Nenhum cliente conectado.\n")
        else:
            print(f'{'#':<4} {'USUÁRIO':<20} {'ENDEREÇO':<45}')
            print('='*44)
            for indice,cliente in enumerate(clientes_conectados, 1):
                endereco_str = f'{cliente['endereco'][0]}:{cliente['endereco'][1]}'
                print(f"{indice:<4} {cliente['nome_usuario']:<20} 📫  {endereco_str:<2}")
        print("\n" + "─" * 67 + "\n")


def gerenciar_cliente(socket_cliente, endereco_cliente):
    try:
        with socket_cliente:
            # O 'with' habilita o socket do cliente dentro do bloco
            # quando o bloco terminar, o socket é fechado

            print("\n" + "─" * 67)
            print(f"Nova conexão: {endereco_cliente}")

            # envia a solicitação do nome de usuário ao cliente
            pedir_nome_usuario = f"\nOlá, seja bem vindo! "
            socket_cliente.sendall(pedir_nome_usuario.encode())

            # recebe o nome de usuário do cliente
            nome_usuario_data = socket_cliente.recv(1024)

            # guarda o nome de usuário fornecido pelo cliente
            nome_usuario = nome_usuario_data.decode().strip()

            # Envia confirmação de boas-vindas
            mensagem_boas_vindas = f"Olá {nome_usuario}, seu usuário foi criado com sucesso! ☕"
            socket_cliente.sendall(mensagem_boas_vindas.encode())

            # cria o registro dicionário do cliente
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
                    remover_cliente(cliente_info)
                    break
                print(f"Recebido de {nome_usuario}: {data.decode()}")

                # verificaa se o cliente se desconectou
                if data.decode().lower().strip() in ['/exit', '/sair', '/quit', '/disconnect']:
                    print(f"O cliente: {nome_usuario} se desconectou.")
                    remover_cliente(cliente_info)
                    return  # Sai da função
                    # socket_cliente.shutdown(socket.SHUT_RDWR)
                    # socket_cliente.close()

                data_resposta = f"Eco: {data.decode()}"
                socket_cliente.sendall(data_resposta.encode())

                # verifica se uma combinação de tecla foi pressionada
                if keyboard.is_pressed('ctrl+shift+b'):
                    consultar_clientes_conectados()


    except ConnectionResetError:
        print(f"🔁  Conexão resetada por {cliente_info["nome_usuario"]}")
    except socket.error as e:
        print(f"❌  Erro no socket do cliente {cliente_info["nome_usuario"]}: {e}")
    except Exception as e:
        print(f"❌  Erro inesperado com {cliente_info["nome_usuario"]}: {e}")
    finally:
           remover_cliente(cliente_info)

# hotkeys usadas para o servidor
keyboard.add_hotkey('ctrl+shift+b', consultar_clientes_conectados)




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
        print(f"═════════════════════ Menu ══════════════════════")
        print(f"  Ctrl+Shift+B: Consultar clientes conectados")
        print(f"  Ctrl+C no terminal: Encerrar o servidor")


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
                continue


except KeyboardInterrupt:
    print("\n⚠️  Servidor interrompido pelo terminal (Ctrl+C)")
    sys.exit()
except Exception as e:
    print(f" ❌ Erro no servidor: {e}")
finally:
    # O socket_servidor é fechado automaticamente ao sair do bloco 'with'
    print("\n\n============ Servidor encerrado ============\n\n")
