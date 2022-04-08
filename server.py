import socket
import threading
import datetime
import copy
from logger import logger
import colorama
from colorama import Fore

colorama.init() #initialize colorma module for used him to change color in tag case

host = socket.gethostbyname(socket.gethostname()) #ip (private ip address) address 
port = 55555 #dynamic port
addr = (host, port) #addr is host:port -> 125.34.22.1:56753
format = 'ascii' #format to decode and encode date

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create server(socket) with AF_INET(IPV4 type) and SOCK_STREAM(TCP protocol)
server.bind(addr) #associate server-socket at addr(host, port)

clients = [] #list of clients connect 
names = [] #list of names of the clients connect
usersBan = [] #list of users is banned from the admin
usersFreeze = [] #list of users freeze from the admin

#create client-server architecture
#the server send at all of the client the message of one client 
def sendAll(msg):
    for client in clients:
        client.send(msg.encode(format))

#gestion of message traffic inbound or outbound
def msgGestion(client, name):
    while True:
        try:
            msg = client.recv(2048).decode(format) #recv message (real message)

            #check if the user wanted message is freeze or not
            if msg[0:msg.index(':')] in usersFreeze:
                client.send('You are freeze'.encode(format))

            #check if tag in messagecls
            msgLists = msg[len(name)+2:].split(' ')

            for word in msgLists:
                if word.startswith('@'):
                    idx = msgLists.index(word)

                    if msgLists[idx][1:] in names:
                        msg = f'{name}:' + ' ' + Fore.BLUE + f'{msgLists[idx]}' + ' ' + Fore.WHITE + f'{" ".join(msgLists[1:])}'
                    else:
                        msg = msg 
        
            #check message
            if msg[len(name)+2:].startswith('/kick'):
                if name == 'admin':
                    nameToKick = msg[len(name)+2+6:]

                    kickUser(nameToKick, 'kick')
                else:
                    client.send('You cannot utilized "/kick" command, only admin do'.encode(format))
            elif msg[len(name)+2:].startswith('/ban'):
                if name == 'admin':
                    nameToBan = msg[len(name)+2+5:]

                    kickUser(nameToBan, 'ban')

                    usersBan.append(nameToBan)
                else:
                    client.send('You cannot utilized "/ban" command, only admin do'.encode(format))
            elif msg[len(name)+2:].startswith('/freeze'):
                if name == 'admin':
                    lists = msg[len(name)+2+8:].split(' ')

                    usersFreeze.append(lists[0])

                    freezeUser(lists[0], lists[1], 'freeze')
                else:
                    client.send('You cannot utilized "/freeze" command, only admin do'.encode(format))
        
            #check if message is not a special-instructions (kick, ban, freeze)
            if msg[len(name)+2:].startswith('/kick') or msg[len(name)+2:].startswith('/ban') or msg[len(name)+2:].startswith('/freeze') or msg[0:msg.index(':')] in usersFreeze:
                pass #not send 
            else:
                sendAll(msg) #send message at all users 
        except:
            #protocol for left users from the chat

            if client in clients:
                idx = clients.index(client)

                clients.remove(client)

                sendAll(f'{names[idx]} left the chat')

                names.remove(names[idx])

                client.close()

                break
    
    print('[CONNECTION CLOSE] connection is closed')
    logger.info('[CONNECTION CLOSE] connection is closed')
    print(f'[COUNT CONNECTIONS] connections are {len(clients)}')

#kick user from the chat
def kickUser(nameToBan, type):
    idx = names.index(nameToBan)

    clientProv = clients[idx]

    clients.remove(clients[idx])

    sendAll(f'{nameToBan} is {type} by admin')

    names.remove(nameToBan)

    clientProv.close()

#freeze user for tot time
def freezeUser(nameToFreeze, timeToFreeze, type):
    sendAll(f'{nameToFreeze} is {type} by admin for {timeToFreeze[0]}{timeToFreeze[1]}')

    dateNow = datetime.datetime.now().strftime('%H:%M:%S')
    date = copy.copy(dateNow)

    quantity, type = timeToFreeze[0], timeToFreeze[1]
    
    if type == 's':
        while dateNow[6:] != str(int(date[6:]) + int(quantity)):
            dateNow = datetime.datetime.now().strftime('%H:%M:%S')

        usersFreeze.remove(nameToFreeze)
        sendAll(f'{nameToFreeze} has been unlocked')
    elif type == 'm':
        while dateNow[3:5] != str(int(date[3:5]) + int(quantity)):
            dateNow = datetime.datetime.now().strftime('%H:%M:%S')

        usersFreeze.remove(nameToFreeze)
        sendAll(f'{nameToFreeze} has been unlocked')
    elif type == 'h':
        while dateNow[0:2] != str(int(date[0:2]) + int(quantity)):
            dateNow = datetime.datetime.now().strftime('%H:%M:%S')

        usersFreeze.remove(nameToFreeze)
        sendAll(f'{nameToFreeze} has been unlocked')
    
#initzialization of server (the basic configuration)
def init():
    server.listen() #server is listening

    print(f'[LISTENING] server is listening at {addr}...')
    logger.info(f'[LISTENING] server is listening at {addr}...')

    listen = True

    while listen: #until the server listens it continues
        client, addrClient = server.accept() #server accept new connections

        cont = True #boolean used for check if send message is ok

        print(f'[NEW CONNECTION ACCEPT] {client} is accept at {addr}')
        logger.info(f'[NEW CONNECTION ACCEPT] {client} is accept at {addr}')

        client.send('NAME'.encode(format)) #send identificative 'NAME' 

        name = client.recv(2048).decode(format) #receve name

        #append client and name-client in respective lists
        clients.append(client)
        names.append(name)

        #check if name user is admin
        if name == 'admin':
            client.send('PASSADMIN'.encode(format))

            pswAdmin = client.recv(2048).decode(format)

            #check if client password is correct 
            if pswAdmin != 'passadmin':
                cont = False

                clients.remove(client)
                names.remove(name)

                client.close()
        
        #check if name is banned or no
        if name in usersBan:
            cont = False

            clients.remove(client)
            names.remove(name)

            client.close()
        
        #if lenght of clients is greater than 0 cls
        if len(clients) > 0 and cont:
            print(f'[NEW CONNECTION] {client} connect at {addr}')
            logger.info(f'[NEW CONNECTION] {client} connect at {addr}')

            sendAll(f'{name} join in the chat')

            #creare thread and start him
            thread = threading.Thread(target=msgGestion, args=(client, name))
            thread.start()

            print(f'[COUNT CONNECTIONS] connections are {len(clients)}')
            logger.info(f'[COUNT CONNECTIONS] connections are {len(clients)}')
    
    logger.critical(f'[SERVER NOT FOUND] server is closed')

print('[START] server is start')
logger.info('[START] server is start')
init()
