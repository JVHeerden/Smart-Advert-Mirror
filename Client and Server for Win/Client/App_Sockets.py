import socket

def SendMessage(port, msg):
    s = socket.socket()  # Create a socket object
    host = socket.gethostname()  # Get local machine name
    print('[INFO] Waiting For Client....')
    s.connect((host, port))
    print('[Alert] Got connection From Client')
    print('[INFO] Sending Message: ', msg)
    s.send(str.encode(msg))
    s.close()

def ReceiveMessage(port):
    s = socket.socket()             # Create a socket object
    host = socket.gethostname()     # Get local machine name
    s.bind((host, port))            # Bind to the port
    s.listen(5)                     # Now wait for Client Connection.

    print('[INFO] Waiting For Message From Server')
    conn, addr = s.accept()         # Establish connection with Client.
    print('[Alert] Connected To Server On: ', addr)

    data = conn.recv(4096)
    msg = data.decode('utf-8')
    print('[INFO] Message Received: ', msg)
    s.close()
    print('[ALERT] Connection Closed')
    return msg