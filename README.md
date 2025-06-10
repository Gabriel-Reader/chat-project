# Chat Project

Este é um sistema de chat TCP simples, desenvolvido para fins didáticos, com suporte a múltiplos clientes e grupos de conversa.

## Funcionalidades
- Cadastro de usuário com validação de nome (apenas letras, números e underline)
- Criação de grupos de chat
- Entrada e saída de grupos
- Listagem de grupos ativos e seus participantes
- Envio de mensagens para todos os membros do grupo
- Comandos para desconectar do chat
- Suporte a múltiplos clientes conectados simultaneamente

## Como usar

1. **Inicie o servidor:**
   ```bash
   python servidor.py
   ```
2. **Inicie um ou mais clientes em outros terminais:**
   ```bash
   python cliente.py
   ```
3. **No terminal do cliente:**
   - Informe um nome de usuário válido (2-15 caracteres, letras, números ou underline).
   - Use os comandos abaixo para interagir com o chat.

## Comandos do cliente
- `/criar <nome_do_grupo>` — Cria um novo grupo
- `/entrar <nome_do_grupo>` — Entra em um grupo existente
- `/listar` — Lista os grupos ativos e seus participantes
- `/sair` ou `/exit` — Desconecta do chat
- Basta digitar uma mensagem para enviá-la ao grupo em que está

## Exemplo de uso
```bash
$ python cliente.py
Por favor, informe o seu nome de usuário: usuario1
💬  Chat iniciado!
/comandos disponíveis...
> /criar grupo1
> /entrar grupo1
> Olá, grupo!
```

## Requisitos
- Python 3.x
- Biblioteca `keyboard` (para o servidor):
  ```bash
  pip install keyboard
  ```

## Observações
- O servidor deve ser iniciado antes dos clientes.
- Cada cliente pode participar de apenas um grupo por vez.
- O nome de usuário deve ser único entre os clientes conectados.
- O sistema foi desenvolvido para fins de estudo e pode ser expandido.

---
Autores: Gabriel Pinheiro, Renan Hurtado