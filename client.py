import socket
import threading

host = '192.168.178.79' #ip address (private ip address) to connect
port = 55555 #port to connect
addr = (host, port) #addr is host:port -> 125.34.22.1:56753
format = 'ascii' #format to decode and encode date

name = input('Enter name: ') #insert name to send

#check if user is the admin
if name == 'admin':
    pwdAdmin = input('Enter password: ')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create client(socket) with AF_INET(IPV4 type) and SOCK_STREAM(TCP protocol)
client.connect(addr) #connect client-socket at server-socket

#gestion of message traffic inbound or outbound
def msgGestion():
    while True:
        genMsg = client.recv(2048).decode(format) #receive general message (identificative and real message)

        #check different case of general message
        if genMsg == 'NAME':
            client.send(name.encode(format))
        elif genMsg == 'PASSADMIN':
            client.send(pwdAdmin.encode(format))
        else:  
            print(genMsg)

#send written message
def msgSend():
    while True:
        msg = f'{name}: {input(": ")}'

        client.send(msg.encode(format)) #send real message

#create thread
thread1 = threading.Thread(target=msgGestion)
thread2 = threading.Thread(target=msgSend)

#start thread
thread1.start()
thread2.start()