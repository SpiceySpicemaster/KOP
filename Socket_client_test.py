#!/usr/bin/python3
import random
from useful import ASCIIchars
from Top_sneaky_v4m import create_key,encrypt_and_send,decrypt_and_recieve,recv_msg,send_msg
from socket import *
from time import sleep

ip = 'localhost'
port = 1200
session_key = None
#s.connect((ip,port))

def generate_key(seed): #Client side is a bit different,it doesn't need a name.
    key, duals = create_key(ASCIIchars(), seed)
    c = open('cli_KEY.txt', 'w')
    for i in key.keys():
        c.write(i)
    c.write('THISHEREISTHESEPERATORMYLADY')
    for i in key.values():
        c.write(' ')
        c.write(i)
    c.write('THISHEREISTHESEPERATORMYLADY')
    for i in duals:
        c.write(i + ' ')
    c.close()

try:
    while True:
        #s.connect((input('Host IP: '),int(input('Host open port: '))))

        cmd = input('Send a command: ')
        s = socket()
        s.connect((ip,port))

        if session_key == None:
            send_msg(s,'new session')
        else:
            send_msg(s,'ok')

        greeting_message = recv_msg(s)

        if greeting_message == 'new session':
            print('Establishing new session...')
            b = random.randint(100, 1000)

            g = int(recv_msg(s))
            p = int(recv_msg(s))
            A = int(recv_msg(s))
            B = (g ** b) % p
            send_msg(s,str(B))
            session_key = (A**b) % p
            #print(g, p , A, session_key,sep='\n')
            generate_key(session_key)


        if cmd == '':
            cmd = 'A'

        sleep(0.5)
        encrypt_and_send(cmd,'srv',s)

        a = decrypt_and_recieve('srv',s)
        if a != "ok":
            print(a)
        elif cmd == 'add_usr' or cmd == 'login':
            print(decrypt_and_recieve('srv',s))
            encrypt_and_send(input(),'srv',s)
            print(decrypt_and_recieve('srv',s))
            encrypt_and_send(input(),'srv',s)
            print(decrypt_and_recieve('srv',s))

        elif cmd == 'eval':
            encrypt_and_send('Input python code: ','srv',s)

        elif cmd == 'give_admin':
            print(decrypt_and_recieve('srv',s))
            encrypt_and_send(input(),'srv',s)
            print(decrypt_and_recieve('srv',s))

        elif cmd == 'logout' or cmd == 'show_all_users' or cmd == 'show_online_users':
            print(decrypt_and_recieve('srv',s))

        elif cmd == 'msg':
            print(decrypt_and_recieve('srv',s))
            encrypt_and_send(input(),'srv',s)
            re = decrypt_and_recieve('srv',s)
            print(re)
            if re == "Message: ":
                encrypt_and_send(input(),'srv',s)
            else:
                print(re)
        elif cmd == 'help':
            print(decrypt_and_recieve('srv',s))

        else:
            print(decrypt_and_recieve('srv',s))

        print('----------------------------------------------------------')
        s.close()

except ConnectionResetError:
    print('Connection timed out.')
