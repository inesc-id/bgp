
import os, re, socket, threading, struct, sys, string
from ctypes import *
from urllib import urlopen
from subprocess import call
import os.path
import time
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

hopCount = 0
hostname = "h3-2"

def read_file(filename):

    f = open(filename,'r')
    data  = f.read() 
    return data

def create_file(filename, data): 
    
    f = open(filename,'w')

    f.write(data)
    f.close()
    return

def recv_data(sock): 
    
    a = sock.recv(4)
    data_len = struct.unpack('!I',a)[0]
    data = sock.recv(data_len)
    
    return data

def send_data(sock,data): 
    
    data_len = struct.pack('!I',len(data))
    sock.send(data_len)
    sock.send(data)

    return

def send_file_contents(file_name,usersock,userinfo): #DOWNLOAD
    # This was so insecure. The client could have requested the private key or whatever file!
    # data = read_file(file_name)

    data = read_file("%s-pub.key" % (hostname))

    send_data(usersock,data)

    return 0

def receive_file_contents(file_name,usersock):#UPLOAD

    data = recv_data(usersock)
    create_file(file_name,data)

    return 0

def handle_connection(usersock,userinfo):
    global hopCount
    
    the_order = recv_data(usersock).upper()           

    if(the_order == "GETPUB"):
        send_file_contents(recv_data(usersock),usersock,userinfo)

    nonce = recv_data(usersock)
    print "Got nonce", nonce

    pri = open("%s-pri.key" % (hostname),"r")
    key = RSA.importKey(pri)
    hash = SHA256.new(nonce).digest()

    signature = key.sign(hash, '')
    signature = str(signature)

    send_data(usersock,signature)

    return

def getIP(hostname):
    AS, idx = hostname.replace('h', '').split('-')
    AS = int(AS)
    if AS == 4:
        AS = 3
    ip = '%s.0.%s.1' % (10+AS, idx)
    return ip

# Arg 1 : my IP -> ip to bind the local socket
# Arg 2 : my port -> port to bind the local socket
def main():

    global hopCount
    global hostname

    print "Getting ready for Cryptographic ping ..."

    hostname = sys.argv[1]
    my_ip = getIP(hostname)
    my_port = int(sys.argv[2])

    if(not(os.path.isfile("%s-pub.key" % (hostname)))):

        random_generator = Random.new().read
        key = RSA.generate(1024,random_generator)

        privateHandle = open("%s-pri.key" % (hostname),'wb')
        privateHandle.write(key.exportKey())

        public_key = key.publickey()
        pubHandle = open("%s-pub.key" % (hostname), 'wb')
        pubHandle.write(public_key.exportKey())

        pubHandle.close()
        privateHandle.close()

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    print "Binding at " + my_ip + ":" + str(my_port)
    sock.bind((my_ip,my_port))

    print "I'm listening now ..."

    while(1):
        sock.listen(0)
        conn, addr = sock.accept()
        print "New Client: " + str(addr)

        threading.Thread(None,handle_connection,None,(conn,addr)).start()

    return

main()
