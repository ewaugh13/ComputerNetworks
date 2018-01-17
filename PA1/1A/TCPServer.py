from socket import *

server_address = ('localhost', 2100)
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(server_address)
server_socket.listen(1)
print 'The server is ready to receive'
while 1:
    connection_socket, addr = server_socket.accept()
    sentence = connection_socket.recv(1024)
    capitalized_sentence = sentence.upper()
    connection_socket.send(capitalized_entence)
    connection_socket.close()
