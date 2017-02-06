import socket

def SendMessage(port, msg):
    s = socket.socket()  # Create a socket object
    host = socket.gethostname()  # Get local machine name
    print('[INFO] Waiting For Client....')
    #s.connect(('192.168.1.104', port))
    s.connect(('169.254.61.173', port))
    #"DESKTOP-AK7MCHR"
    #s.connect(("DESKTOP-AK7MCHR", port))
    print('[Alert] Got connection From Client')
    print('[INFO] Sending Message: ', msg)
    s.send(str.encode(msg))
    s.close()

def ReceiveMessage(port):
    s = socket.socket()             # Create a socket object
    host = socket.gethostname()     # Get local machine name
    #s.bind((host, port))            # Bind to the port
    s.bind(('0.0.0.0', port))
    s.listen(0)                     # Now wait for Client Connection.

    print('[INFO] Waiting For Message From Server')
    print('I am Here')
    conn, addr = s.accept()         # Establish connection with Client.
    print('Nope, I am here.')
    print('[Alert] Connected To Server On: ', addr)

    data = conn.recv(4096)
    msg = data.decode('utf-8')
    print('[INFO] Message Received: ', msg)
    s.close()
    print('[ALERT] Connection Closed')
    return msg
