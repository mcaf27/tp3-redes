import socket, json
from struct import pack, unpack
from sys import argv

OK = 0b0100111101001011
ERRO = 0b0100010101010010
OI = 0b0100111101001001
FLW = 0b0100011001001100
MSG = 0b0100110101010011

SERVER_ID = 65535

class Client:
  def __init__(this):
    this.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    this._id = int(argv[1])

  def connect_to_server(this, port, host='127.0.0.1'):
    # enviar mensagem de OI

    msg_type = OI
    orig_id = this._id
    dest_id = SERVER_ID
    seq_num = 0b0000000000000000

    # msg = pack('<H', msg_type) + pack('<H', orig_id) + pack('<H', dest_id) + pack('<H', seq_num)
    # msg = pack('<4H', msg_type, orig_id, dest_id, seq_num)

    msg_content = { 'MSG_TYPE': msg_type, 'ORIG_ID': orig_id, 'DEST_ID': dest_id, 'SEQ_NUM': seq_num }

    msg = json.dumps(msg_content).encode('ascii')

    this.socket.connect((host, int(port)))

    this.socket.send(msg)


  def disconnect(this):
    # enviar mensagem de FLW
    this.socket.close()

  def send_message_to(this, dest, text):

    # enviar mensagem para dest

    pass

  def read(this):
    while True:
      in_ = input()
      inputs = in_.split(' ')
      msg_type = inputs[0]

      print('lido:', msg_type)

      if msg_type == 'M':
        dest = inputs[1]
        text = ' '.join(inputs[2:])

        this.send_message_to(dest, text)

      elif msg_type == 'S':
        this.disconnect()

client = Client()
client.connect_to_server(8001)
client.disconnect()