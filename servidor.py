# https://pymotw.com/2/select/

import json, select, sys
from socket import socket, AF_INET, SOCK_STREAM

OK = 0b0100111101001011
ERRO = 0b0100010101010010
OI = 0b0100111101001001
FLW = 0b0100011001001100
MSG = 0b0100110101010011

SERVER_ID = 65535

class Server:
  def __init__(this, port, host='127.0.0.1'):

    s = socket(AF_INET, SOCK_STREAM)

    this.sckt = s

    this.sckt.bind((host, int(port)))

    this.sckt.listen()

  def message(this, msg_type, dest_id, seq_num, text=None, orig_id=SERVER_ID):
    msg_content = { 'MSG_TYPE': msg_type, 'ORIG_ID': orig_id, 'DEST_ID': dest_id, 'SEQ_NUM': seq_num, 'MSG_TEXT': text }
    return json.dumps(msg_content).encode('ascii')

  def sendOK(this, dest_id, seq_num):
    msg = this.message(OK, dest_id, seq_num)
    this.sckt.send(msg)
  
  def sendERRO(this, dest_id, seq_num):
    msg = this.message(ERRO, dest_id, seq_num)
    this.sckt.send(msg)
    


server = Server(sys.argv[1])
server_socket = server.sckt

inputs = [server_socket]
client_ids = [None]
client_seq_nums = [None]
outputs = []

while inputs:
  try:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    for s in readable:

      if s is server_socket:
        client_conn, client_addr = s.accept()
        print('nova conexão com', client_addr)
        inputs.append(client_conn)

      else:
        data = s.recv(1024)

        if data:
          msg = json.loads(data)

          msg_type = msg.get('MSG_TYPE')
          
          if msg_type == OI:

            id_ = msg.get('ORIG_ID')
            seq_num = msg.get('SEQ_NUM')
            client_ids.append(id_)
            client_seq_nums.append(seq_num)

            ok_msg = server.message(OK, id_, seq_num)
            s.send(ok_msg)

            if s not in outputs:
              outputs.append(s)

          elif msg_type == MSG:
            seq_num = msg.get('SEQ_NUM')
            orig_id = msg.get('ORIG_ID')
            dest_id = msg.get('DEST_ID')
            text = msg.get('MSG_TEXT')

            # broadcast
            if int(dest_id) == 0:
              ok_msg = server.message(OK, orig_id, seq_num)
              s.send(ok_msg)

              for dest_index, client_id in enumerate(client_ids):
                if client_id != orig_id and client_id is not None:
                  
                  txt_msg = server.message(MSG, client_id, client_seq_nums[int(dest_index)] + 1, text, orig_id=orig_id)
                  inputs[int(dest_index)].send(txt_msg)

                  ack = s.recv(1024)
                  ack = json.loads(ack)
                  ack_type = ack.get('MSG_TYPE')

                  if ack_type == OK:
                    print(f'Mensagem enviada com sucesso para {client_id}')
                    continue
                    # ack_type nunca será ERRO

            if int(dest_id) in client_ids:
              ok_msg = server.message(OK, orig_id, seq_num)
              s.send(ok_msg)

              dest_index = client_ids.index(int(dest_id))
              # client_seq_nums[int(dest_index)] += 1
              txt_msg = server.message(MSG, dest_id, client_seq_nums[int(dest_index)] + 1, text, orig_id=orig_id)

              dest_socket = inputs[int(dest_index)]
              
              dest_socket.send(txt_msg)

              # AQUI
              print('recebendo msg de ok...')
              ack = dest_socket.recv(1024)
              print(ack)
              ack = json.loads(ack.decode('ascii'))
              ack_type = ack.get('MSG_TYPE')

              if ack_type == OK:
                print(f'Mensagem enviada com sucesso para {client_id}')
                continue
                # ack_type nunca será ERRO
              
            else:
              err_msg = server.message(ERRO, orig_id, seq_num)
              s.send(err_msg)

          elif msg_type == FLW:

            if s in outputs:
              outputs.remove(s)
            if s in inputs:
              inputs.remove(s)
              id_ = msg.get('ORIG_ID')
              index = client_ids.index(id_)
              client_ids.remove(id_)
              del client_seq_nums[index]

        else: # == flw
          if s in outputs:
            outputs.remove(s)
          inputs.remove(s)
          s.close()

    # for s in writable:
    #   print('writable?')

    for s in exceptional:
      print('excep')
      if s in outputs:
        outputs.remove(s)
      inputs.remove(s)
      s.close()


  except:
    for s in inputs:
      inputs.remove(s)
      s.close()
    server_socket.close()