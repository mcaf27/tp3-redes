import socket, json
from struct import pack, unpack

OK = 0b0100111101001011
ERRO = 0b0100010101010010
OI = 0b0100111101001001
FLW = 0b0100011001001100
MSG = 0b0100110101010011

class Server:
  def __init__(this, port, host='127.0.0.1'):

    this.clients = [] # verificar se o cliente está no socket certo... ??

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind((host, int(port)))

    s.listen()

    conn = s.accept()[0]

    with conn:
      while True:
        data = conn.recv(1024)
        if not data:
          break

        msg = json.loads(data.decode('ascii'))

        msg_type = msg.get('MSG_TYPE')
        
        if msg_type == OI:

          id = msg.get('ORIG_ID')

          this.clients.append(id) # associar clientes a sockets ??

    s.close()

server = Server(8001)