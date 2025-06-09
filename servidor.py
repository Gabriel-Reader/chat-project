"""
===============================================================================
SISTEMA DE CHAT TCP - SERVIDOR
===============================================================================
Descrição: Servidor TCP que gerencia múltiplos clientes para o serviço de chat de texto
Autores: Gabriel Pinheiro, Renan Hurtado
"""

#TODO: Criei um teste com um grupo pré criado, todos os clientes que se conectarem no servidor
# vão entrar no grupo, se quiser testar, descomente as linhas 171 a 180 e a 201.
# conecte um cliente, escolha um nome e mande uma mensagem, pode ser mais de 1

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
    # TODO: "participantes" é uma tupla que contém o nome de usuário e o socket do cliente

    with grupos_lock:
        grupo = {
            "nome_grupo": nome_grupo,
            "participantes": participantes
        }

        grupos_ativos.append(grupo)
        print(f"O grupo {grupo['nome_grupo']} foi criado com sucesso!")

    # grupos_ativos [
    # {
    #     'nome_grupo': 'Equipe de Desenvolvimento',
    #     'participantes': [
    #         (nome_usuario, socket_cliente),
    #         ('Renan', '<socket.socket (...))>',
    #         ('AnaBea', '<socket.socket (...))>')
    #                       ]
    # },
    # {
    #     'nome_grupo': 'Equipe de Vendas',
    #     'participantes': [
    #         (nome_usuario, socket_cliente),
    #         ('Marta', '<socket.socket (...))>'),
    #         ('Carlos', '<socket.socket (...))>')
    #                       ]
    # }
    #]

def envia_mensagem_grupo(nome_grupo, nome_usuario, mensagem):
    """Envia uma mensagem para todos os participantes de um grupo"""
    mensagem = f"[{nome_grupo}] {nome_usuario}: {mensagem}"

    for grupo in grupos_ativos:
        if grupo['nome_grupo'] == nome_grupo:

            for participante in grupo['participantes']:
                nome_usuario, socket_cliente = participante
                socket_cliente.sendall(mensagem.encode())
                # print(mensagem


def gerenciar_cliente(socket_cliente, endereco_cliente):
    """Gerencia a comunicação com um cliente específico em thread separada."""

    try:
        with socket_cliente:
            print("\n" + "─" * 67)
            print(f"🔗 Nova conexão: {endereco_cliente}")

            # envia mensagem de boas vindas
            mensagem_boas_vindas = f"\nOlá, seja bem vindo! "
            socket_cliente.sendall(mensagem_boas_vindas.encode())

            #Controla a execução do while
            bool_usuario_invalido = True

            while bool_usuario_invalido:
                #recebe o nome de usuário do cliente
                nome_usuario_data = socket_cliente.recv(1024)
                nome_usuario = nome_usuario_data.decode().strip()

                if clientes_conectados:
                    nome_existe = False

                    for cliente in clientes_conectados:
                        usuario_conectado = f'{cliente['nome_usuario']}'

                        if nome_usuario == usuario_conectado:
                            # print(f"\n{endereco_cliente}: O nome de usuário fornecido não estava disponível")

                            mensagem_resposta = f"nome_usuario is False"
                            socket_cliente.sendall(mensagem_resposta.encode())
                            nome_existe = True
                            break

                    if not nome_existe:
                        print(f"{endereco_cliente}: ✔ Nome de usuário disponível\n")

                        mensagem_confirmacao = f"Olá {nome_usuario}, seu usuário foi criado com sucesso! ☕"
                        socket_cliente.sendall(mensagem_confirmacao.encode())
                        bool_usuario_invalido = False
                        break

                else:
                    #Primeiro usuário, então o nome está disponível
                    print(f"{endereco_cliente}: ✔ Nome de usuário disponível")

                    mensagem_confirmacao = f"Olá {nome_usuario}, seu usuário foi criado com sucesso! ☕"
                    socket_cliente.sendall(mensagem_confirmacao.encode())
                    bool_usuario_invalido = False
                    break

            # cria o registro dicionário do cliente
            with clientes_lock:
                cliente_info = {
                    "socket": socket_cliente,
                    "endereco": endereco_cliente,
                    "nome_usuario": nome_usuario
                }
                adicionar_cliente(cliente_info)

            """
            grupo = {
                    'nome_grupo': 'equipe',
                    'participantes': [
                        (nome_usuario, socket_cliente)
                    ]
                }

            grupos_ativos.append(grupo)
            """

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
                    remover_cliente(cliente_info)
                    return

                # envia_mensagem_grupo("equipe", nome_usuario, "Olá grupo")

                # Envia resposta constante (eco)
                data_resposta = " "
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
                thread.daemon = True # Permite que o programa principal saia mesmo se a thread estiver rodando
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
