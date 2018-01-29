from socket import *
from urllib.parse import urlparse
import sys
from multiprocessing import *

def connection_request_handler(connection_socket, addr):

    #set default port and variables that will be used in get request
    request_port = 80
    method = http_version = netloc = url_path = None
    first_recv = request_status_ok = True
    header_tags = []
    sentence = ""
    #continues to read all the bytes that are being sent
    while True:
        partial_sentence = connection_socket.recv(1024).decode('utf-8', errors='ignore')
        if partial_sentence == "\r\n\r\n" or partial_sentence == "\r\n":
            break
        sentence += partial_sentence

    sentence_chunks = sentence.split("\r\n")
    sentence_chunks = sentence_chunks[:-1]

    #uses sent bytes to build the request by searching for the variables needed
    for sentence in sentence_chunks:
        if first_recv:
            sentence_split = sentence.split()
            #error handling for first message not being in right format
            if len(sentence_split) != 3:
                error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Request not in proper format</h1></body></html>\r\n\r\n"
                connection_socket.send(error_message.encode())
                request_status_ok = False
                connection_socket.close()
                break
            #gets the variables needed like GET and the http version
            method = sentence_split[0]
            http_version = sentence_split[2]
            first_recv = False
            parsed_sentence = urlparse(sentence_split[1])

            #gets the port, netloc and path to build request
            if parsed_sentence.port != "" and parsed_sentence.port is not None:
                request_port = parsed_sentence.port
            if parsed_sentence.netloc != "" and parsed_sentence.netloc is not None:
                netloc = parsed_sentence.netloc.split(":")[0]
            if parsed_sentence.path != "" and parsed_sentence.path is not None:
                url_path = parsed_sentence.path
        #grabs any of the other header tags sent
        else:
            sentence_split = sentence.split()
            length_of_tag = len(sentence_split[0])
            if sentence_split[0][length_of_tag - 1] != ":":
                error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Header tag in wrong format</h1></body></html>\r\n\r\n"
                connection_socket.send(error_message.encode())
                request_status_ok = False
                connection_socket.close()
                break
            if sentence_split[0] == "Host:":
                netloc = sentence_split[1]
            else:
                header_tags.append(sentence)

    if request_status_ok == False:
        sys.exit()

    #error handling if not HTTP/1.0
    if http_version != "HTTP/1.0":
        error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Improper HTTP version</h1></body></html>\r\n\r\n"
        connection_socket.send(error_message.encode())
        connection_socket.close()
        sys.exit()
    #error handling if no netloc is provided
    if netloc == "" or netloc is None:
        error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>No selected Host</h1></body></html>\r\n\r\n"
        connection_socket.send(error_message.encode())
        connection_socket.close()
        sys.exit()
    #error handling if not GET
    if method != "GET":
        error_message = "HTTP/1.0 501 Not Implemented\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Not a proper GET request</h1></body></html>\r\n\r\n"
        connection_socket.send(error_message.encode())
        connection_socket.close()
        sys.exit()

    #creates new socket to connect to and send GET request
    request_socket = socket(AF_INET, SOCK_STREAM)

    request_socket.connect((netloc, request_port))
    get_request = method + " " + url_path + " " + http_version + "\r\n" + "Host: " + netloc + "\r\n"
    
    for header in header_tags:
        if header != "Connection: close":
            get_request += (header + "\r\n")

    get_request += ("Connection: close" + "\r\n\r\n")
    request_socket.sendall(get_request.encode())

    #reads all of the bytes from the requst and then sends them back to original client connection which is then closed
    html_response = b""
    while True:
        partial_response = request_socket.recv(4096)
        if not partial_response:
            break
        html_response += partial_response
    connection_socket.send(html_response)

    connection_socket.close()
    sys.exit()
    

#port being read as a command line argument
proxy_port = int(sys.argv[1])

#connecting through localhost and creating a socket to bind to
server_address = ('localhost', proxy_port)
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(server_address)
server_socket.listen(20)
print('The server is ready to receive')

#continues loop looking for connection requests to the server

while True:
    connection, addr = server_socket.accept()
    print("new connection")
    process = Process(target=connection_request_handler, args=(connection, addr))
    process.start()
    connection.close()