import socket

HOST = '127.0.0.1'  # endereço do servidor
PORT = 12345        # mesma porta do servidor

Nome_usuario = input("Informe o seu nome de usuário: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_cliente:
    socket_cliente.connect((HOST, PORT))                                    # conecta o cliente ao servidor
    socket_cliente.sendall(Nome_usuario.encode())                         # envia mensagem ao servidor
    data = socket_cliente.recv(1024)                                        # guarda a resposta do servidor em data

print(f"Resposta do servidor: {data.decode()}")