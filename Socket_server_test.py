#!/usr/bin/python3
import random
from useful import ASCIIchars
from Top_sneaky_v4m import create_key,encrypt_and_send,decrypt_and_recieve
from socket import *
from hashlib import *
from threading import *

haram_chars = [';','\n',',']
normal_commands = ['show_users','login','logout','add_usr','msg']
admin_commands = ['show_all_users','purge_all','terminate','eval']
logged_in = {}
session_keys = {} #Important, they don't expire! Might implement it later.

try:
    file = open('users.txt','a')
except:
    file = open('users.txt', 'w')
file.close()

try:
    file = open('admins.txt','a')
except:
    file = open('admins.txt', 'w')
file.close()


def generate_key(seed,name):
    key, duals = create_key(ASCIIchars(), seed)
    c = open(str(name)+'.txt', 'w')
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

def address_is_online(addr):
    for i in logged_in:
        if addr in logged_in[i]:
            return True
    return False

def giv_users():
    file = open('users.txt', 'r')
    users = {}
    for i in file:
        i.strip()
        i = i.split(';')
        users[i[0]] = i[1]
    file.close()
    return users

def return_user(addr):
    try:
        c = 0
        for i in list(logged_in.values()):
            if addr in i:
                break
            c += 1
        return list(logged_in.keys())[c]
    except IndexError or ValueError:
        return False

def is_admin(usr):
    if usr == False:
        return False
    file = open('admins.txt','r')
    admins = file.readline().strip().split(';')

    if usr in admins:
        return True
    else:
        return False


s = socket()

s.bind(('', 1200))

s.listen(30)

def main():
    global logged_in

    while True:
        c, addr = s.accept()

        port = addr[1]
        addr = addr[0]

        wrong = 0
        return_msg = ''
        print('Received connection from: '+str(addr))

        greeting_message = c.recv(512).decode()

        if addr not in session_keys.keys() or greeting_message == 'new session':
            print('New session')
            c.send('new session'.encode())

            g = 2
            p = random.randint(2 ** 2000, 2 ** 4000)
            a = random.randint(100, 1000)
            A = (g ** a) % p

            c.send(str(g).encode())
            c.send(str(p).encode())
            c.send(str(A).encode())
            B = int(c.recv(10000).decode())

            session_keys[addr] = (B**a) % p
            generate_key(session_keys[addr],addr)

        else:
            print('Session in progress')
            c.send('ok'.encode())

        cmd = decrypt_and_recieve(addr,c)
        print('Command recived: ',cmd)

        if is_admin(return_user(addr)) and cmd in admin_commands:
            encrypt_and_send('ok',addr,c)

            if cmd == 'purge_all':
                file = open('users.txt', 'w')
                file.close()
                encrypt_and_send('User files purged',addr,c)

            elif cmd == 'show_all_users':
                file = open('users.txt', 'r')
                users = {}
                for i in file:
                    i.strip()
                    i = i.split(';')
                    users[i[0]] = i[1]
                file.close()

                encrypt_and_send('\n'.join(list(users.keys())),addr,c)

            elif cmd == 'terminate':
                encrypt_and_send('Thread with ID ' + str(current_thread().name) + ' terminated.',addr,c)
                exit()

            elif cmd == 'eval':
                eval(decrypt_and_recieve(addr,c).encode())

        elif cmd in admin_commands:
            encrypt_and_send("You don't have administrative rights!",addr,c)

        else:
            encrypt_and_send('ok',addr,c)

            if cmd == 'show_users':
                encrypt_and_send('\n'.join(logged_in),addr,c)

            elif cmd == 'msg':
                users = giv_users()
                encrypt_and_send("Recipent's username: ",addr,c)
                usr = decrypt_and_recieve(addr,c)
                if usr in users:
                    if address_is_online(addr):
                        encrypt_and_send("Message: ",addr,c)
                        msg = decrypt_and_recieve(addr,c)
                        g = [return_user(addr),usr]
                        g.sort()
                        print(g)
                        try:
                            file = open(str(g[0])+';'+str(g[1])+'.txt', 'a')
                        except:
                            file = open(str(g[0])+';'+str(g[1])+'.txt', 'w')
                        file.write(msg)
                        file.close()
                    else:
                        encrypt_and_send("You are not logged in!",addr,c)
                else:
                    encrypt_and_send("Username does not exist!",addr,c)

            elif cmd == 'login':
                encrypt_and_send('Please enter your username:',addr,c)
                usr = decrypt_and_recieve(addr,c)

                encrypt_and_send('Please enter your password:',addr,c)
                pw = decrypt_and_recieve(addr,c)

                for i in haram_chars:
                    if i in pw:
                        wrong = 1

                if wrong == 0:
                    file = open('users.txt','r')
                    users = {}
                    for i in file:
                        i.strip()
                        i = i.split(';')
                        users[i[0]] = i[1]

                    if (usr not in list(users.keys())):
                        wrong = 1
                        return_msg = 'Username does not exist'

                    elif (str(sha256(str(pw).encode()).hexdigest()).strip() != users[usr].strip()):
                        wrong = 1
                        return_msg = 'Wrong password'

                    elif usr in logged_in:
                        wrong = 1
                        return_msg = 'User already logged in'

                    elif address_is_online(addr):
                        wrong = 1
                        return_msg = 'You are already logged in'


                if wrong == 1:
                    encrypt_and_send(return_msg,addr,c)
                else:
                    encrypt_and_send('Success!',addr,c)
                    try:
                        logged_in[usr].append(addr)
                    except KeyError:
                        logged_in[usr] = [addr]

            elif cmd == 'add_usr':
                encrypt_and_send('Please enter your username:',addr,c)
                usr = decrypt_and_recieve(addr,c)

                encrypt_and_send('Please enter your password:',addr,c)
                pw = decrypt_and_recieve(addr,c)

                for i in haram_chars:
                    if i in pw:
                        wrong = 1
                        return_msg = 'Password has invalid characters'

                if wrong == 0:
                    file = open('users.txt','r')
                    users = {}
                    for i in file:
                        i.strip()
                        i = i.split(';')
                        users[i[0]] = i[1]
                    if usr not in list(users.keys()):
                        file.close()
                        file = open('users.txt','a')
                        file.write(str(usr)+';'+str(sha256(str(pw).encode()).hexdigest())+'\n')
                        file.close()
                    else:
                        return_msg = 'Username already exists'
                        wrong = 1

                if wrong == 1:
                    encrypt_and_send(return_msg,addr,c)
                else:
                    encrypt_and_send('Success!',addr,c)

            elif cmd == 'logout':
                if address_is_online(addr):
                    del(logged_in[return_user(addr)])
                    encrypt_and_send('Logged out.',addr,c)
                else:
                    encrypt_and_send('You are not logged in.',addr,c)

            else:
                encrypt_and_send('Invalid command!',addr,c)


        c.close()

x = Thread(target=main,daemon=True,name='0').start()
x1 = Thread(target=main,daemon=True,name='1').start()
x2 = Thread(target=main,daemon=True,name='2').start()
x3 = Thread(target=main,daemon=True,name='3').start()
x4 = Thread(target=main,daemon=True,name='4').start()

while True:
    pass