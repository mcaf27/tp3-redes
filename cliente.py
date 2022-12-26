import socket, json
from sys import argv, stdin
from select import select

OK = 0b0100111101001011
ERRO = 0b0100010101010010

OI = 0b0100111101001001
FLW = 0b0100011001001100
MSG = 0b0100110101010011

SERVER_ID = 65535

ID = argv[1]
PORT = argv[2]

class Client:
  def __init__(this):
    this.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    this._id = int(ID)
    this.seq_num = 0

  def message(this, msg_type, dest_id, text=None):
    msg_content = { 'MSG_TYPE': msg_type, 'ORIG_ID': this._id, 'DEST_ID': dest_id, 'SEQ_NUM': this.seq_num, 'MSG_TEXT': text }
    return json.dumps(msg_content).encode('ascii')

  def connect_to_server(this, port, host='127.0.0.1'):
    msg = this.message(OI, SERVER_ID)
    this.socket.connect((host, int(port)))
    this.socket.send(msg)

    data = this.socket.recv(1024)
    msg_type = json.loads(data).get('MSG_TYPE')

    if msg_type == OK:
      print('Conexão com o servidor realizada com sucesso')
    elif msg_type == ERRO:
      print('Erro ao conectar com o servidor')

    this.seq_num += 1

  def disconnect(this):
    msg = this.message(FLW, SERVER_ID)
    this.socket.send(msg)

    data = this.socket.recv(1024)
    msg_type = json.loads(data).get('MSG_TYPE')

    if msg_type == OK:
      this.socket.close()
      return True

    this.seq_num += 1
    
    return False

  def send_message_to(this, dest, text):

    dest_id = dest if dest != 'broadcast' else format(0, '016b')

    msg_content = { 'MSG_TYPE': MSG, 'ORIG_ID': this._id, 'DEST_ID': dest_id, 'SEQ_NUM': this.seq_num, 'MSG_LENGTH': format(len(text.encode('ascii')), '032b'), 'MSG_TEXT': text }
    msg = json.dumps(msg_content).encode('ascii')

    this.socket.send(msg)

    this.seq_num += 1

    # esperar confirmação?

    data = this.socket.recv(1024)
    data = json.loads(data)
    msg_type = data.get('MSG_TYPE')
    
    if msg_type == OK:
      pass

  def open(this):

    inputs = [this.socket.fileno(), stdin.fileno()]
    outputs = []

    while True:
      readable, writable, exceptional = select(inputs, outputs, inputs)

      for item in readable:
        if item == this.socket.fileno():
          
          data = this.socket.recv(1024)
          print('dados recebidos', data)
          data = json.loads(data)

          msg_type = data.get('MSG_TYPE')

          if msg_type == MSG:
            orig_id = data.get('ORIG_ID')
            text = data.get('MSG_TEXT')
            
            print(f'Mensagem de {orig_id}: {text}')

            ok_msg = this.message(OK, SERVER_ID)
            print('enviando msg de ok', ok_msg)
            this.socket.send(ok_msg)

        elif item == stdin.fileno():
          in_ = input()

          stdinputs = in_.split(' ')

          msg_type = stdinputs[0]

          if msg_type == 'M':
            dest = stdinputs[1]
            text = ' '.join(stdinputs[2:])

            this.send_message_to(dest, text)
          
          elif msg_type == 'S':
            disc = this.disconnect()
            if disc:
              break

client = Client()
client.connect_to_server(PORT)
client.open()
# client.disconnect()