import random
import time
import useful
from tkinter import *
from tkinter import filedialog
from decimal import *
getcontext().prec = 10000000000000000

# vx == Version X
# m == Modular version
# v3 feature - Seedable key generation, hopefully good (probs not tho lol)
# v4 reature - Special characters like \t \n ect. don't fuck up the program anymore
def recv_msg(c,debug=0):
    incoming = ''
    while len(incoming) < 32:
        incoming += c.recv(1).decode()
    if debug == 1:
        print('i:', incoming)
    if len(incoming) != 32:
        print('DATA SCATTERED OVER THE NETWORK, PLS FIX UR DAMN PROTOCOL TO ACCOUNT FOR DIS!!!!!1')
        raise ValueError

    padding = int(incoming, base=2)
    rcvd_msg = ''

    while padding != 0:
        tmp = c.recv(1).decode()
        padding -= 1
        rcvd_msg += tmp
    if debug == 1:
        print('r:', rcvd_msg)
    return rcvd_msg
def send_msg(c,msg,debug=0):
    padding = '0'*(32-len(bin(len(msg))[2:])) + bin(len(msg))[2:]
    msg = padding + msg
    if debug == 1:
        print('s:', msg)
    c.sendall(msg.encode())

def browseFiles():
    def gib():
        global filename
        filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("Text files","*.txt*"),("all files","*.*")))
        label_file_current.configure(text="Current file:"+filename)
    window = Tk()
    window.title('File Explorer')
    window.geometry("600x300")
    window.config(background = "white")
    label_file_explorer = Label(window,text = "File Explorer using Tkinter",width = 100, height = 4,fg = "blue")
    label_file_explorer.pack(pady = 10)
    label_file_current = Label(window,text = "Current file:",width = 100, height = 4,fg = "blue")
    label_file_current.pack(pady = 10)
    button_select = Button(window,text = "Select file",command = gib)
    button_select.pack(pady = 10)
    button_exit = Button(window,text = "Continue",command = window.destroy)
    button_exit.pack(pady = 10)
    window.mainloop()
    return filename

def create_key(chars,seed):
    getcontext().prec = 10000000000000000
    if seed == 0:
        seed = 1
    num = 13509273**100
    tmp_list = list(str(Decimal(num) * Decimal(seed)))
    x = ''
    c = 1
    l = 0
    com = 0
    duals = []
    key = {}
    chars.append(' ')
    chars.append('\t')
    chars.append('\n')
    chars.append('\r')

    if '.' in tmp_list:
        tmp_list.remove('.')
    if 'E' in tmp_list:
        tmp_list.remove('+')
        tmp_list.remove('E')

    for o in chars:
        if (o in key.keys()) == False:
            if seed == '':
                x += chars[random.randint(0, len(chars) - 1)]
            else:
                x += chars[com]
                l += 1
                com += int(tmp_list[l])
                com = com % 94

            while x in key.values():
                if seed == '':
                    x += chars[random.randint(0, len(chars) - 1)]
                else:
                    if x + chars[com] not in key.values():
                        x += chars[com]
                    l += 1
                    com += int(tmp_list[l])
                    com = com % 94

            key[o] = x
            x = ''
        if len(key[o]) == 2:
            duals.append(str(c))
        c += 1
    return [key,duals]

def encrypt_and_send(text,addr,recipent):
    decypher = {}
    if addr == 'srv':
        addr = 'cli_KEY'

    a = open(str(addr) + '.txt', 'r')
    i = a.read().split('THISHEREISTHESEPERATORMYLADY')
    E = list(i[0])
    F = (i[1].split(' '))
    while '' in F:
        F.remove('')
    cu = 0
    for o in F:
        decypher[E[cu]] = o
        cu += 1
    a.close()

    cu = 0
    text = list(text)
    duals = []
    ret = ''
    for i in text:
        dec = decypher[i]
        ret += dec
        if len(dec) == 2:
            duals.append(str(cu))
            cu += 1
        cu += 1

    #print(' '.join(text), end=' ')
    #print(ret,duals)

    send_msg(recipent, ' '.join(duals))
    send_msg(recipent, ret)

def decrypt_and_recieve(addr,sender):
    duals = recv_msg(sender)
    rcv = recv_msg(sender)

    if addr == 'srv':
        addr = 'cli_KEY'

    rcv = list(rcv)
    decypher = {}

    a = open(str(addr) + '.txt', 'r')
    i = a.read().split('THISHEREISTHESEPERATORMYLADY')
    E = list(i[0])
    F = (i[1].split(' '))
    while '' in F:
        F.remove('')
    cu = 0
    for o in F:
        decypher[o] = E[cu]
        cu += 1
    a.close()

    tmp = []
    for i in duals.split(' '):
        try:
            tmp.append(int(i))
        except ValueError:
            pass
    duals = tmp

    cu = 0
    dec = ''

    while cu < len(rcv):
        if cu in duals:
            dec += decypher[rcv[cu]+rcv[cu+1]]
            cu += 1
        else:
            dec += decypher[rcv[cu]]
        cu += 1

    return dec


def main():
    mode = 0
    while mode != '3':
        mode = input('Encrypt or Decrypt? 1=Encrypt 2=Decrypt 3=Stop ')
        if mode == '1':
            seed = input('Do you want to seed your key? (Leave empty for random generation or input any positive number): ')
            if seed != '':
                seed = float(seed)

            chars = useful.ASCIIchars()
            newlines = []
            temp = ''

            print('Válaszd ki a lazárni való szövegfájlt!')
            a = open(browseFiles())
            print('Encrypting in progress [',end='')
            key, duals = create_key(chars, seed)

            for i in a:
                print('|',end='')
                time.sleep(0.05)
                i = i.strip()
                i = list(i)

                for o in i:
                    temp += key[o]
                newlines.append(temp)
                temp = ''
            print(']\nDone!')
            a.close()

            b = open('ENCRYPTED.txt','w')
            for i in newlines:
                i += '\n'
                b.write(i)
            b.close()

            c = open('KEY.txt','w')
            for i in key.keys():
                c.write(i)
            c.write('THISHEREISTHESEPERATORMYLADY')
            for i in key.values():
                c.write(' ')
                c.write(i)
            c.write('THISHEREISTHESEPERATORMYLADY')
            for i in duals:
                c.write(i+' ')
            c.close()

        elif mode == '2':
            print('Kulcsfájlt kérek!')
            a = open(browseFiles())
            print('Reading key',end='')
            for i in a:
                i = i.split('THISHEREISTHESEPERATORMYLADY')
                E = list(i[0])
                F = (i[1].split(' '))
                duals = i[2].split()
            useful.dotdot(4,0.5)
            print('\nDone!')
            print('Cleaning key',end='')
            useful.dotdot(4,0.5)
            while '' in F:
                F.remove('')
            print('\nDone!')
            c = 0
            decypher = {}
            print('Compileing translation table',end='')
            for o in F:
                decypher[o] = E[c]
                c += 1
            useful.dotdot(4,0.5)
            print('\nDone!')
            a.close()

            print('Válaszd ki a kulcshoz tartozó lezárt fájlt!')
            b = open(browseFiles(),'r')
            newlines = []
            c = 1
            ZA_WARUDO = 0
            wrrry = 0
            print('Decryption in progress [',end='')
            for i in b:
                print('|',end='')
                i = i.strip()
                i = list(i)
                temp = ''
                c2 = 0
                for o in i:
                    if ZA_WARUDO != 1:
                        if str(c-wrrry) in duals:
                            temp += decypher.get(str(o)+str(i[c2+1]))
                            ZA_WARUDO = 1
                        else:
                            try:
                                temp += decypher.get(o)
                            except:
                                lol = 1
                    else:
                        ZA_WARUDO = 0
                        wrrry += 1
                    c += 1
                    c2 += 1
                newlines.append(temp)
            print(']\nDone!')
            b.close()

            c = open('DECRYPTED.txt','w')
            print('Creating DECRYPTED.txt',end='')
            for i in newlines:
                print('.',end='')
                time.sleep(0.2)
                c.write(i)
                c.write('\n')
            print('\nDone!')
            c.close()
        elif mode == '3':
            print('Stopping',end='')
            useful.dotdot(4,0.5)
        else:
            print('1-est,2-est vagy 3-ast kell írni!')

