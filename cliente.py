import socket
import threading
import re

HOST = '127.0.0.1'
PORT = 12345
rodando = True

"""Thread para receber mensagens do servidor/usuários"""

def receber_mensagens(socket_cliente):
    global rodando

    while rodando:
        mensagem_recebida = socket_cliente.recv(1024)
        if not mensagem_recebida:
            print("\n❌ Conexão perdida com o servidor.")
            rodando = False
            break

        mensagem_recebida = mensagem_recebida.decode()
        if mensagem_recebida.strip():  # ignora o eco que o servidor envia: " "
            print(f"{mensagem_recebida}")


def nome_usuario_valido(nome):
    # Aceita apenas letras, números e underline, entre 2 e 15 caracteres
    return re.match(r'^[A-Za-z0-9_]{2,15}$', nome) is not None


def verificar_nome_usuario(nome_usuario):
    while True:
        # Verifica e envia o nome de usuário para o servidor

        if not nome_usuario_valido(nome_usuario):
            print("\n❌ Nome inválido! Use apenas letras, números e underline (2-15 caracteres).\n")

        else:
            # Envia o nome de usuário para o servidor e recebe a confimação
            socket_cliente.sendall(nome_usuario.encode())
            resposta_servidor = socket_cliente.recv(1024)
            resposta_servidor = resposta_servidor.decode()

            if resposta_servidor == 'nome_usuario is False':
                print("\n⛔ Nome de usuário não disponível")

            else:
                print("\n✅ Nome válido!")
                print(f"\n{"─" * 67}")
                print(f"Resposta do servidor: {resposta_servidor}")
                break

        # solicita novamente até ser válido
        nome_usuario = input("Por favor, informe o seu nome de usuário: (2-15 caracteres): ")


"""Programa principal que inicia o cliente."""

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
    try:
        # conecta o cliente ao servidor
        socket_cliente.connect((HOST, PORT))

        # Recebe boas vindas do servidor
        mensagem_servidor = socket_cliente.recv(1024)
        print(mensagem_servidor.decode())

        nome_usuario = input("Por favor, informe o seu nome de usuário: (2-15 caracteres): ")

        # chama função que valida o nome de usuário
        verificar_nome_usuario(nome_usuario)

        # Inicia a thread para receber mensagens
        thread_recebimento = threading.Thread(target=receber_mensagens, args=(socket_cliente,))
        thread_recebimento.daemon = True  # Permite que o programa principal saia mesmo se a thread estiver rodando
        thread_recebimento.start()

        # Mensagem inicial do chat, agora no lugar certo
        print("\n" + "═" * 50)
        print("💬  Chat iniciado!")
        print("═" * 50)
        print("📋  COMANDOS DISPONÍVEIS:")
        print("   🔹  /entrar <nome_do_grupo>   → Entrar em um grupo")
        print("   🔹  /listar                   → Listar grupos ativos")
        print("   🔹  /criar <nome_do_grupo>    → Criar um novo grupo")
        print("   🔹  /sair ou /exit            → Desconectar do chat")
        print("═" * 50 + "\n")
        print("> ", end="")  # Prompt para o usuário digitar

        # --- Lógica para Comandos ---
        while rodando:       # Loop de envio de mensagens
            mensagem = input()
            if not rodando:  # Verifica se a thread de recebimento encerrou a conexão
                break

            if mensagem.lower().startswith('/criar '):
                partes = mensagem.split(' ', 1)

                if len(partes) > 1:
                    nome_do_grupo = partes[1].strip()

                    if nome_do_grupo:
                        # Envia a string formatada do comando para o servidor
                        socket_cliente.sendall(f"/criar:{nome_do_grupo}".encode())
                    else:
                        print("❌ Por favor, forneça um nome para o grupo. Ex: /criar MeuNovoGrupo")

                else:
                    print("❌ Comando inválido. Use: /criar <nome_do_grupo>")

            elif mensagem.lower() == '/listar':
                # Envia a string formatada do comando para o servidor
                socket_cliente.sendall("/listar".encode())

            elif mensagem.lower() in ["/exit", "/sair", "/quit", "/disconnect"]:
                print('\n\n📴 Você se desconectou!\n\n')
                rodando = False
                socket_cliente.sendall(mensagem.encode()) # Informa o servidor sobre a saída
                break

            elif mensagem.lower().startswith('/entrar '):
                partes = mensagem.split(' ', 1)

                if len(partes) > 1:
                    nome_do_grupo = partes[1].strip()

                    if nome_do_grupo:
                        # Envia a string formatada do comando para o servidor
                        socket_cliente.sendall(f"/entrar:{nome_do_grupo}".encode())
                    else:
                        print("\n❌ Por favor, forneça um nome para o grupo. Ex: /entrar <nome_do_grupo>\n")

                else:
                    print("\n❌ Comando inválido. Use: /entrar <nome_do_grupo>\n")

            else:
                # Envia a mensagem normal
                socket_cliente.sendall(mensagem.encode())
            


    except ConnectionRefusedError:
        print(f"❌ Não foi possível conectar ao servidor em {HOST}:{PORT}. Verifique se o servidor está rodando.")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")
    finally:
        rodando = True