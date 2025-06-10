"""
===============================================================================
SISTEMA DE CHAT TCP - SERVIDOR
===============================================================================
Descrição: Servidor TCP que gerencia múltiplos clientes para o serviço de chat de texto
Autores: Gabriel Pinheiro, Renan Hurtado
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


def validar_nome_usuario(socket_cliente, endereco_cliente):
    """Valida o nome de usuário recebido do cliente."""
    try:
        while True:
            nome_usuario_data = socket_cliente.recv(1024)
            nome_usuario = nome_usuario_data.decode().strip()

            with clientes_lock:
                if clientes_conectados:
                    nome_existe = False

                    for cliente in clientes_conectados:
                        usuario_conectado = cliente['nome_usuario']

                        if nome_usuario == usuario_conectado:
                            """ Nome já existe, envia mensagem de erro ao cliente"""
                            mensagem_resposta = "nome_usuario is False"
                            socket_cliente.sendall(mensagem_resposta.encode())
                            nome_existe = True
                            break

                    # Se o nome não existe, envia confirmação de sucesso 
                    if not nome_existe:
                        print(f"{endereco_cliente}: ✔ Nome de usuário disponível")
                        mensagem_confirmacao = f"Olá {nome_usuario}, seu usuário foi criado com sucesso! ☕"
                        socket_cliente.sendall(mensagem_confirmacao.encode())
                        return nome_usuario # Nome válido, retorna

                else:
                    # Primeiro usuário, então o nome está disponível
                    print(f"{endereco_cliente}: ✔ Nome de usuário disponível")
                    mensagem_confirmacao = f"Olá {nome_usuario}, seu usuário foi criado com sucesso! ☕"
                    socket_cliente.sendall(mensagem_confirmacao.encode())
                    return nome_usuario # Nome válido, retorna

    except Exception as e:
        print(f"❌ Ocorreu um erro ao tentar validar o nome de usuário do cliente {endereco_cliente}: {e}")
        return None


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
    # }


def envia_mensagem_grupo(nome_grupo, nome_usuario, mensagem, socket_remetente):
    """Envia uma mensagem para todos os participantes de um grupo"""
    mensagem = f"[{nome_grupo}] {nome_usuario}: {mensagem}"

    for grupo in grupos_ativos:
        if grupo['nome_grupo'] == nome_grupo:

            for participante in grupo['participantes']:
                nome_usuario, socket_participante = participante

                # Não envia a mensagem de volta para o remetente
                if socket_participante != socket_remetente:
                    socket_participante.sendall(mensagem.encode())


def entrar_grupo(nome_grupo, socket_cliente, nome_usuario):
    """Adiciona um cliente a um grupo existente."""

    with grupos_lock:
        for grupo in grupos_ativos:
            if grupo['nome_grupo'] == nome_grupo:

                # Adiciona o usuário ao grupo
                grupo['participantes'].append((nome_usuario, socket_cliente))
                socket_cliente.sendall(f"\n✅ Você entrou no grupo '{nome_grupo}'.\n".encode())
                return

        # Se o grupo não existir
        socket_cliente.sendall(f"\n❌ O grupo '{nome_grupo}' não existe.\n".encode())


def remover_cliente_grupo(nome_grupo, socket_cliente, nome_usuario):
    """Remove um cliente de um grupo existente."""

    print(f"Removendo {nome_usuario} do grupo {nome_grupo}")
    with grupos_lock:
        for grupo in grupos_ativos:
            if grupo['nome_grupo'] == nome_grupo:
                # Remove o usuário do grupo, se existir
                try:
                    grupo['participantes'].remove((nome_usuario, socket_cliente))
                except ValueError:
                    print(f"Participante ({nome_usuario}) já não está no grupo {nome_grupo}.")
                # Remove o grupo se não houver mais participantes
                if not grupo['participantes']:
                    grupos_ativos.remove(grupo)
                    print(f"O grupo {nome_grupo} foi removido pois ficou vazio.")
                break


def consultar_grupos_ativos():
    """Exibe a lista formatada de todos os grupos ativos no servidor e retorna a string para o cliente."""
    print(f"\n{"─"*23} GRUPOS ATIVOS {"─"*23}\n")

    with grupos_lock:
        if not grupos_ativos:
            print("❌ Nenhum grupo ativo no momento.\n")
            return "❌ Nenhum grupo ativo no momento.\n"
        else:
            grupos_formatados = f'{"\n#":<4} {"NOME DO GRUPO":<30} {"PARTICIPANTES"}\n'
            grupos_formatados += '='*67 + '\n'
            for indice, grupo in enumerate(grupos_ativos, 1):
                # Pega apenas os nomes dos usuários dos participantes
                participantes_nomes = [p[0] for p in grupo['participantes']]
                grupos_formatados += f"{indice:<4} {grupo['nome_grupo']:<30} {', '.join(participantes_nomes)}\n"
            print(grupos_formatados)
            return grupos_formatados
    print("\n" + "─" * 67 + "\n")


def gerenciar_cliente(socket_cliente, endereco_cliente):
    """Gerencia a comunicação com um cliente específico em thread separada."""

    try:
        with socket_cliente:
            print("\n" + "─" * 67)
            print(f"🔗 Nova conexão: {endereco_cliente}")

            # envia mensagem de boas vindas
            mensagem_boas_vindas = f"\nOlá, seja bem vindo! "
            socket_cliente.sendall(mensagem_boas_vindas.encode())

            # Chama a nova função para validar o nome de usuário
            nome_usuario = validar_nome_usuario(socket_cliente, endereco_cliente)
            if nome_usuario is None:  # Se a validação falhou ou o cliente desconectou
                return  # Encerra a thread do cliente

            # cria o registro dicionário do cliente
            with clientes_lock:
                cliente_info = {
                    "socket": socket_cliente,
                    "endereco": endereco_cliente,
                    "nome_usuario": nome_usuario,
                    "grupo_atual": None
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

                # ---Lógica para Comandos---
                nome_novo_grupo = None

                if mensagem_recebida.startswith('/criar:'):
                    partes = mensagem_recebida.split(':', 1)

                    if len(partes) > 1:
                        nome_novo_grupo = partes[1].strip()

                        if not nome_novo_grupo:
                            socket_cliente.sendall("❌ Nome do grupo inválido.".encode())

                        elif nome_novo_grupo in [grupo['nome_grupo'] for grupo in grupos_ativos]:
                            socket_cliente.sendall(f"\n❌ O grupo '{nome_novo_grupo}' já existe.\n".encode())

                        else:
                            if cliente_info["grupo_atual"] != None:
                                grupo_atual = cliente_info["grupo_atual"]
                                remover_cliente_grupo(grupo_atual, socket_cliente, nome_usuario)

                            # Adiciona o criador ao grupo
                            criar_grupo(nome_novo_grupo, [(nome_usuario, socket_cliente)])
                            socket_cliente.sendall(f"\n✅  Grupo '{nome_novo_grupo}' criado com sucesso e você foi adicionado.\n".encode())
                            cliente_info["grupo_atual"] = nome_novo_grupo  # Atualiza o grupo atual

                    else:
                        socket_cliente.sendall("❌ Comando de grupo inválido. Use /criar:NomeDoGrupo".encode())
                    # continue # Pula o resto do loop para evitar eco

                elif mensagem_recebida == '/listar':
                    lista_grupos = consultar_grupos_ativos()
                    socket_cliente.sendall(lista_grupos.encode())

                elif mensagem_recebida.startswith('/entrar:'):
                    partes = mensagem_recebida.split(':', 1)

                    if len(partes) > 1:
                        nome_novo_grupo = partes[1].strip()


                        if cliente_info["grupo_atual"] != None:
                            grupo_atual = cliente_info["grupo_atual"]
                            remover_cliente_grupo(grupo_atual, socket_cliente, nome_usuario)


                        entrar_grupo(nome_novo_grupo, socket_cliente, nome_usuario)
                        cliente_info["grupo_atual"] = nome_novo_grupo  # Atualiza o grupo atual
                # --- Fim da Nova Lógica ---

                # verifica comandos de desconexão
                data_comando = mensagem_recebida.lower().strip()

                if data_comando in ['/exit', '/sair', '/quit', '/disconnect']:
                    grupo_para_remover = cliente_info["grupo_atual"]
                    # remover_cliente_grupo(grupo_para_remover, socket_cliente, nome_usuario)
                    # remover_cliente(cliente_info)
                    return
                
                # verifica se a mensagem é um comando de grupo ou uma mensagem normal
                # Se não for um comando, envia a mensagem para o grupo atual
                if not mensagem_recebida.startswith('/'):
                    grupo_atual = cliente_info.get("grupo_atual")
                    if grupo_atual:
                        envia_mensagem_grupo(grupo_atual, nome_usuario, mensagem_recebida, socket_cliente)
                    else:
                        socket_cliente.sendall("\n❌  Você precisa entrar em um grupo para enviar mensagens.\n".encode())    


                # Envia resposta constante (eco)
                data_resposta = " "
                socket_cliente.sendall(data_resposta.encode())

                # verifica hotkey para consultar clientes
                if keyboard.is_pressed('ctrl+shift+b'):
                    consultar_clientes_conectados()
                elif keyboard.is_pressed('ctrl+shift+g'):
                    consultar_grupos_ativos()


    except ConnectionResetError:
        print(f"🔁  Conexão resetada por {cliente_info["nome_usuario"]}")
    except socket.error as e:
        print(f"❌  Erro no socket do cliente {cliente_info["nome_usuario"]}: {e}")
    except Exception as e:
        print(f"❌  Erro inesperado com {cliente_info["nome_usuario"]}: {e}")
    finally:
           grupo_para_remover = cliente_info["grupo_atual"]
           if grupo_para_remover is not None:
                # Se o cliente estava em um grupo, remove ele do grupo
                remover_cliente_grupo(grupo_para_remover, socket_cliente, nome_usuario)
           remover_cliente(cliente_info)


"""Configuração Hotkeys"""
keyboard.add_hotkey('ctrl+shift+b', consultar_clientes_conectados)
keyboard.add_hotkey('ctrl+shift+g', consultar_grupos_ativos)


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
        print(f" 1 - Consultar clientes conectados (Ctrl+Shift+B)")
        print(f" 2 - Mostrar grupos ativos (Ctrl+Shift+G)")
        print(f" 3 - Encerrar o servidor (Ctrl+C)")
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