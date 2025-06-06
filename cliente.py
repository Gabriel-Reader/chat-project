import socket

HOST = '127.0.0.1'  # endereço do servidor
PORT = 12345        # mesma porta do servidor

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
    # conecta o cliente ao servidor
    socket_cliente.connect((HOST, PORT))

    # Recebe a solicitação do nome de usuário do servidor
    mensagem_servidor = socket_cliente.recv(1024)
    print(mensagem_servidor.decode())

    while True:
        nome_usuario = input("Por favor, informe o seu nome de usuário:  (2-15 caracteres): ")
        if len(nome_usuario) > 15:
            print("❌ Nome muito longo! Máximo 15 caracteres.")
        elif len(nome_usuario) <2:
            print("❌ Nome muito curto! Minimo 2 caracteres.")
        else:
            # Envia o nome de usuário para o servidor e recebe a confimação
            socket_cliente.sendall(nome_usuario.encode())
            resposta_servidor = socket_cliente.recv(1024)
            resposta_servidor = resposta_servidor.decode()

            if resposta_servidor == 'nome_usuario is False':
                print("\n⛔ Nome de usuário não disponível\n")
            else:
                print("\n✅ Nome válido!")
                print(f"\n{"─" * 67}")
                print(f"Resposta do servidor: {resposta_servidor}")
                break


    while True:
        mensagem = input("Digite sua mensagem: ")
        if mensagem.lower() == "/exit" or mensagem.lower() == "/sair":
            print('\n\n📴  Você se desconectou!\n\n')
            break
        socket_cliente.sendall(mensagem.encode())
        data = socket_cliente.recv(1024)