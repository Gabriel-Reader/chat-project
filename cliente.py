import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

# var para controlar a thread de recebimento
rodando = True

"""Thread para receber mensagens do servidor"""

def receber_mensagens(socket_cliente):
    global rodando

    while rodando:
        mensagem_recebida = socket_cliente.recv(1024)
        if not mensagem_recebida:
            print("\n❌ Conexão perdida com o servidor.")
            rodando = False
            break

        mensagem_recebida = mensagem_recebida.decode()
        if mensagem_recebida.strip(): # ignora o eco que o servidor envia: " "
            print(f"{mensagem_recebida}")


def verificar_nome_usuario(nome_usuario):
    while True:
        # Verifica e envia o nome de usuário para o servidor

        if len(nome_usuario) > 15:
            print("❌ Nome muito longo! Máximo 15 caracteres.")

        elif len(nome_usuario) < 2:
            print("❌ Nome muito curto! Minimo 2 caracteres.")

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

        print("\n💬  Chat iniciado! Digite (/sair ou /exit) para desconectar.\n")

        while rodando:
            mensagem = input()
            if not rodando:  # Verifica se a thread de recebimento encerrou a conexão
                break
            if mensagem.lower() in ["/exit", "/sair"]:
                print('\n\n📴  Você se desconectou!\n\n')
                rodando = False
                socket_cliente.sendall(mensagem.encode())  # Informa o servidor sobre a saída
                break

            socket_cliente.sendall(mensagem.encode())


    except ConnectionRefusedError:
        print(f"❌ Não foi possível conectar ao servidor em {HOST}:{PORT}. Verifique se o servidor está rodando.")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")
    finally:
        rodando = True
        print("Encerrando cliente...")
        socket_cliente.close()
