from socket import *
from urllib.parse import urlparse

server_address = ('localhost', 2117)
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(server_address)
server_socket.listen(5)
print('The server is ready to receive')
while True:
    connection_socket, addr = server_socket.accept()

    request_port = 80
    method = http_version = netloc = url_path = None
    first_recv = request_status_ok = True
    while method is None or http_version is None or netloc is None or url_path is None:
        sentence = connection_socket.recv(4096).decode()
        if sentence == "\r\n":
            print("breaking")
            break
        if first_recv:
            sentence_split = sentence.split()
            if len(sentence_split) != 3:
                error_message = "not a proper http request"
                connection_socket.send(error_message.encode())
                connection_socket.close()
                request_status_ok = False
                break

            method = sentence_split[0]
            http_version = sentence_split[2]
            first_recv = False
            parsed_sentence = urlparse(sentence_split[1])

            if parsed_sentence.port != "" and parsed_sentence.port is not None:
                request_port = parsed_sentence.port
            if parsed_sentence.netloc != "" and parsed_sentence.netloc is not None:
                netloc = parsed_sentence.netloc
            if parsed_sentence.path != "" and parsed_sentence.path is not None:
                url_path = parsed_sentence.path
        else:
            sentence_split = sentence.split()
            #check for 2 words and that it is one of the header tags
            if sentence_split[0] == "Host:":
                netloc = sentence_split[1]

    if method != "GET":
        error_message = "not a proper http request"
        connection_socket.send(error_message.encode())
        connection_socket.close()
        request_status_ok = False
    if http_version != "HTTP/1.0"
        error_message = "not a proper http request"
        connection_socket.send(error_message.encode())
        connection_socket.close()
        request_status_ok = False

    if request_status_ok == False:
        continue

    #check method, then http version, then host and then endpoint
    request_socket = socket(AF_INET, SOCK_STREAM)

    request_socket.connect((netloc, request_port))
    get_request = method + " " + url_path + " " + http_version + "\r\n" + "Host: " + netloc + "\r\n" + "Connection: close" + "\r\n\r\n"
    request_socket.sendall(get_request.encode())

    html_response = request_socket.recv(4096)
    connection_socket.send(html_response)

    request_socket.close()
    connection_socket.close()

#ask how to pass in port