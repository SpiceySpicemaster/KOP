#!/usr/bin/python3
import random
from useful import ASCIIchars
from Top_sneaky_v4m import create_key,encrypt_and_send,decrypt_and_recieve,recv_msg,send_msg
from socket import *
from hashlib import *
from threading import *

haram_chars = [';','\n',',']
normal_commands = ['help','show_online_users','login','logout','add_usr','msg']
admin_commands = ['show_all_users','purge_all','terminate','eval','give_admin']
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
    # If there are no admins yet it always returns True!

    file = open('admins.txt','r')
    admins = file.readline().strip().split(';')
    file.close()
    if len(admins) == 1:
        return True
    elif usr == False:
        return False
    elif usr in admins:
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

        greeting_message = recv_msg(c)

        if addr not in session_keys.keys() or greeting_message == 'new session':
            print('New session')
            send_msg(c,'new session')

            g = 2
            p = random.randint(2 ** 2000, 2 ** 4000)
            a = random.randint(100, 1000)
            A = (g ** a) % p

            send_msg(c,str(g))
            send_msg(c,str(p))
            send_msg(c,str(A))
            B = int(recv_msg(c))


            session_keys[addr] = (B**a) % p
            #print(g, p , B, session_keys[addr],sep='\n')
            generate_key(session_keys[addr],addr)

        else:
            print('Session in progress')
            send_msg(c,'ok')

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

            elif cmd == 'give_admin':
                encrypt_and_send('Username of the account: ',addr,c)
                usr = decrypt_and_recieve(addr,c)

                file = open('admins.txt', 'r')
                admins = file.readline().strip().split(';')
                file.close()

                if (usr in giv_users() and is_admin(usr) == False) or (len(admins) == 1):
                    a = open('admins.txt','a')
                    a.write(';'+usr)
                    a.close()
                    encrypt_and_send('Success!',addr,c)
                elif usr not in giv_users():
                    encrypt_and_send('Username not found!', addr, c)
                elif usr in giv_users() and is_admin(usr) == True:
                    encrypt_and_send('User is already an Admin!', addr, c)
                else:
                    encrypt_and_send('!fallback_error_msg! how did you even get here?', addr, c)


        elif cmd in admin_commands:
            encrypt_and_send("You don't have administrative rights!",addr,c)

        else:
            encrypt_and_send('ok',addr,c)

            if cmd == 'show_online_users':
                encrypt_and_send('\n'.join(logged_in),addr,c)

            elif cmd == 'help':
                encrypt_and_send(' Normal user command: '+' '.join(normal_commands)+'\n Admin commands: '+
                ' '.join(admin_commands)+' \n You do not give arguments right away, just type the command in, and then'
                ' the program will prompt you for them!\n If there are no admin accounts yet, the system will'
                ' consider anybody an admin!',addr,c)

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
                if address_is_online(addr):
                    wrong = 1
                    return_msg = 'You are already logged in'

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
                encrypt_and_send('Invalid command! Type "help" to get help!',addr,c)

        c.close()

x = Thread(target=main,daemon=True,name='0').start()
x1 = Thread(target=main,daemon=True,name='1').start()
x2 = Thread(target=main,daemon=True,name='2').start()
x3 = Thread(target=main,daemon=True,name='3').start()
x4 = Thread(target=main,daemon=True,name='4').start()

while True:
    pass