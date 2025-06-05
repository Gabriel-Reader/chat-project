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
import keyboard

HOST = '127.0.0.1'
PORT = 12345

clientes_lock = threading.Lock()
clientes_conectados = []

grupos_ativos = []
grupos_lock = threading.Lock()


def adicionar_cliente(cliente_info):
    """Adiciona um novo cliente à lista de conectados."""
    clientes_conectados.append(cliente_info)

    print(f"✅ Cliente adicionado: {cliente_info['nome_usuario']} {cliente_info['endereco']}")
    print(f"📊 Total de clientes conectados: {len(clientes_conectados)}")
    print("─" * 67 + "\n")


def remover_cliente(cliente_info):
    """Remove um cliente da lista de conectados."""
    with clientes_lock:
        usuario = cliente_info['nome_usuario']
        if cliente_info in clientes_conectados:
            print(f"📴 O usuário {usuario} se desconectou.")
            clientes_conectados.remove(cliente_info)


def consultar_clientes_conectados():
    """Exibe a lista formatada de todos os clientes conectados."""
    print(f"\n{"─"*23} CLIENTES CONECTADOS {"─"*23}\n")

    with clientes_lock:
        if not clientes_conectados:
            print("❌ Nenhum cliente conectado.\n")
        else:
            # Cabeçalho da tabela
            print(f'{'#':<4} {'USUÁRIO':<20} {'ENDEREÇO':<45}')
            print('='*44)

            # Lista os clientes
            for indice,cliente in enumerate(clientes_conectados, 1):
                endereco_str = f'{cliente['endereco'][0]}:{cliente['endereco'][1]}'
                print(f"{indice:<4} {cliente['nome_usuario']:<20} 📫  {endereco_str:<2}")

        print("\n" + "─" * 67 + "\n")


def criar_grupo(nome_grupo, participantes):
    """Cria um novo grupo com uma lista de clientes participantes"""
    with grupos_lock:
        grupo = {
            "nome_grupo": nome_grupo,
            "participantes": participantes
        }

        grupos_ativos.append(grupo)
        print(f"O grupo {grupo['nome_grupo']} foi criado com sucesso!")

    # grupos_ativos [ {
    #     'nome_grupo': 'Equipe de Desenvolvimento',
    #     'participantes': [
    #         ('Gabriel', '124.12.12.0:21323'),
    #         ('Renan', '192.168.1.100:50000'),
    #         ('Ana', '10.0.0.5:12345')
    #     ]
    # }
    #]



def gerenciar_cliente(socket_cliente, endereco_cliente):
    """Gerencia a comunicação com um cliente específico em thread separada."""

    try:
        with socket_cliente:
            print("\n" + "─" * 67)
            print(f"🔗 Nova conexão: {endereco_cliente}")

            # envia mensagem de boas vindas
            mensagem_boas_vindas = f"\nOlá, seja bem vindo! "
            socket_cliente.sendall(mensagem_boas_vindas.encode())

            # recebe o nome de usuário do cliente
            nome_usuario_data = socket_cliente.recv(1024)
            nome_usuario = nome_usuario_data.decode().strip()

            # confirma criação do usuário
            mensagem_confirmacao = f"Olá {nome_usuario}, seu usuário foi criado com sucesso! ☕"
            socket_cliente.sendall(mensagem_confirmacao.encode())

            # cria o registro dicionário do cliente
            with clientes_lock:
                cliente_info = {
                    "socket": socket_cliente,
                    "endereco": endereco_cliente,
                    "nome_usuario": nome_usuario
                }
                adicionar_cliente(cliente_info)


            while True:
                # Recebe dados do cliente
                data = socket_cliente.recv(1024)

                # verifica se o cliente se desconectou
                if not data:
                    remover_cliente(cliente_info)
                    break

                mensagem_recebida = data.decode()
                print(f"Recebido de {nome_usuario}: {mensagem_recebida}")

                # verifica comandos de desconexão
                data_comando = data.decode().lower().strip()

                if data_comando in ['/exit', '/sair', '/quit', '/disconnect']:
                    print(f"O cliente: {nome_usuario} se desconectou.")
                    remover_cliente(cliente_info)
                    return

                # Envia resposta (eco)
                data_resposta = f"Eco: {mensagem_recebida}"
                socket_cliente.sendall(data_resposta.encode())

                # verifica hotkey para consultar clientes
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


"""Configuração Hotkeys"""
keyboard.add_hotkey('ctrl+shift+b', consultar_clientes_conectados)



"""Programa principal que inicia e gerencia o servidor."""

try:
    # O uso do 'with' garante que socket_servidor.close() seja chamado no final
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_servidor:

        socket_servidor.bind((HOST, PORT))
        socket_servidor.listen()
        socket_servidor.settimeout(0.1)  # Timeout para verificar hotkeys

        """ interface do servidor """
        print(f"✔ Servidor TCP iniciado em {HOST}:{PORT}...\n")
        print(f"🔷════════════════════ Menu ═════════════════════🔷")
        print(f" 1 - Consultar clientes conectados (Ctrl+Shift+B:)")
        print(f" 2 - Encerrar o servidor (Ctrl+C)")
        print(f"🔷═══════════════════════════════════════════════🔷")


        """O loop principal do servidor"""
        while True:
            try:
                # aceita a conexão do cliente
                socket_cliente, endereco_cliente = socket_servidor.accept()

                # cria e inicia a thread do cliente
                thread = threading.Thread(
                    target=gerenciar_cliente, args=(socket_cliente, endereco_cliente)
                )
                thread.daemon = True
                thread.start()

            except socket.timeout:
                # timeout necessário para o servidor verificar teclas de atalhos
                continue


except KeyboardInterrupt:
    print("\n⚠️  Servidor interrompido pelo terminal (Ctrl+C)")
except Exception as e:
    print(f" ❌ Erro no servidor: {e}")
finally:
    print("\n\n============ SERVIDOR ENCERRADO ============\n\n")


# socket_cliente.shutdown(socket.SHUT_RDWR)
# socket_cliente.close()