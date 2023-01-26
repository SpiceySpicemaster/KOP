def until(Type):
    c = 0
    if Type == 'int':
        while c != 1:
            c = 1
            try:
                d = int(input('Adjá egy számot!'))
            except:
                print('Szám kell!')
                c = 0
        return d
    elif Type == 'float':
        while c != 1:
            c = 1
            try:
                d = float(input('Adjá egy számot!'))
            except:
                print('Lebegőpontos szám kell!')
                c = 0
        return d
    elif Type == 'str':
        while c != 1:
            c = 1
            try:
                d = str(input('Adjá egy számot!'))
            except:
                print('Betű kell')
                c = 0
        return d
def ASCIIchars():
    file = open('ASCIIchars.txt')
    noice = []
    for i in file:
        i = i.strip()
        i = i.split(' ')
        i = i[4]
        noice.append(i)
    return noice
def dotdot(times,length):
    import time
    for i in range(times):
        time.sleep(length)
        print('.',end='')
