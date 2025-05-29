import socket
import threading

HOST = '127.0.0.1'  # localhost
PORT = 12345        # porta

def gerenciar_cliente(socket_cliente, endereco_cliente):
    with socket_cliente:                                   # Habilita o socket do cliente dentro do bloco, quando o bloco terminar, o socket é fechado
        print(f"Conectado por {endereco_cliente}")
        while True:
            data = socket_cliente.recv(1024)
            if not data:
                break
            print(f"Recebido de {endereco_cliente}: {data.decode()}")
            data_resposta = f"Olá {data.decode()}, bem vindo!"
            socket_cliente.sendall(data_resposta.encode())

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_servidor:
        socket_servidor.bind((HOST, PORT))
        socket_servidor.listen()
        print(f"Servidor TCP escutando em {HOST}:{PORT}...")

        while True:
            socket_cliente, endereco_cliente = socket_servidor.accept()
            # Cria uma nova thread para cada cliente
            thread = threading.Thread(target=gerenciar_cliente, args=(socket_cliente, endereco_cliente))
            thread.start()

            if input("Deseja encerrar o servidor? (s/n): ").lower() == 's':
                break


except KeyboardInterrupt:
    print("\nServidor interrompido pelo usuário (Ctrl+C)")
except Exception as e:
    print(f"Erro no servidor: {e}")
finally:
    print("Servidor encerrado")
