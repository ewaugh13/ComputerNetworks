from socket import *
from urllib.parse import urlparse

server_address = ('localhost', 2101)
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(server_address)
server_socket.listen(5)
print('The server is ready to receive')
while True:
    connection_socket, addr = server_socket.accept()
    sentence = connection_socket.recv(1024).decode()
    #if we have a full request do this
    sentence_split = sentence.split()

    parsed_sentence = urlparse(sentence)

    #else figure out how to handle multiple line requests
    request_socket = socket(AF_INET, SOCK_STREAM)
    request_port = 80
    if parsed_sentence.port != None:
        request_port = parsed_sentence.port

    request_socket.connect((parsed_sentence.netloc, request_port))
    get_request = "GET " + parsed_sentence.path + " HTTP/1.0"
    request_socket.sendall(get_request.encode())

    html_response = request_socket.recv(4096)
    connection_socket.send(html_response)

    request_socket.close()
    connection_socket.close()


#questions for TAs
#1 how to handle seperate messages from telnet
#2 how to seperate get request line
#3 how to validate its a proper request line