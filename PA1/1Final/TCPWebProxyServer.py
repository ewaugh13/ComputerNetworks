from socket import *
from urllib.parse import urlparse
import sys
from multiprocessing import *
import requests
import hashlib
import json

def connection_request_handler(connection_socket, addr, api_key):
    try:
        #set default port and variables that will be used in get request
        request_port = 80
        method = http_version = netloc = url_path = None
        first_recv = request_status_ok = True
        header_tags = []
        sentence = ""
        #continues to read all the bytes that are being sent
        while True:
            try:
                partial_sentence = connection_socket.recv(2048).decode('utf-8')
            except UnicodeDecodeError:
                connection_socket.close()
                sys.exit()
            if partial_sentence == '':
                error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Improper read</h1></body></html>\r\n\r\n"
                connection_socket.send(error_message.encode())
                connection_socket.close()
                sys.exit()
            partial_sentence_split = partial_sentence.split("\r\n")
            len_part = len(partial_sentence_split)
            if partial_sentence == "\r\n\r\n" or partial_sentence == "\r\n":
                break
            sentence += partial_sentence
            if len(partial_sentence_split) > 2 and partial_sentence_split[len_part - 1] == '' and partial_sentence_split[len_part - 2] == '':
                break
        sentence_chunks = sentence.split("\r\n")
        sentence_chunks = sentence_chunks[:-1]

        #uses sent bytes to build the request by searching for the variables needed
        for sentence_element in sentence_chunks:
            if first_recv:
                sentence_split = sentence_element.split()
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
                try:
                    parsed_sentence = urlparse(sentence_split[1])
                except:
                    error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Could not parse request</h1></body></html>\r\n\r\n"
                    connection_socket.send(error_message.encode())
                    connection_socket.close()
                    sys.exit()

                #gets the port, netloc and path to build request
                if parsed_sentence.port != "" and parsed_sentence.port is not None:
                    request_port = parsed_sentence.port
                if parsed_sentence.netloc != "" and parsed_sentence.netloc is not None:
                    netloc = parsed_sentence.netloc.split(":")[0]
                if parsed_sentence.path != "" and parsed_sentence.path is not None:
                    url_path = parsed_sentence.path
            #grabs any of the other header tags sent
            else:
                sentence_split = sentence_element.split()
                if len(sentence_split) != 0: 
                    length_of_tag = len(sentence_split[0])
                    if sentence_split[0][length_of_tag - 1] != ":":
                        error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Header tag in wrong format</h1></body></html>\r\n\r\n"
                        connection_socket.send(error_message.encode())
                        request_status_ok = False
                        connection_socket.close()
                        break
                    if sentence_split[0] == "Host:":
                        colon_split = sentence_element.split(":")
                        if len(colon_split) == 3:
                            request_port = int(colon_split[2])
                        netloc = sentence_split[1].split(":")[0]
                    else:
                        header_tags.append(sentence_element)
        
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
        try:
            request_socket.settimeout(10)
            request_socket.connect((netloc, request_port))
        except:
            error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Request to address and port did not work</h1></body></html>\r\n\r\n"
            connection_socket.send(error_message.encode())
            connection_socket.close()
            sys.exit()
        get_request = method + " " + url_path + " " + http_version + "\r\n" + "Host: " + netloc + "\r\n"
        
        add_connection_close = True
        for header in header_tags:
            header_split = header.split()
            if header_split[0] == "Connection:":
                add_connection_close = False
            if header_split[0] != "Accept-Encoding:":
                get_request += (header + "\r\n")

        if add_connection_close:
            get_request += ("Connection: close" + "\r\n\r\n")
        else:
            get_request += "\r\n"
        request_socket.sendall(get_request.encode())
        #reads all of the bytes from the requst and then sends them back to original client connection which is then closed
        html_response = b""
        while True:
            partial_response = request_socket.recv(4096)
            if not partial_response or partial_response == b'':
                break
            html_response += partial_response
        html_response_split = html_response.decode('utf-8', errors='ignore').split('\r\n')
        if html_response_split[0] == 'HTTP/1.1 200 OK' or html_response_split[0] == 'HTTP/1.0 200 OK':
            html_response_split_again = html_response.split(b'\r\n\r\n')
            content = html_response_split_again[len(html_response_split_again) - 1]
            try:
                md5_response = hashlib.md5(content).hexdigest()
            except:
                error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Could not get MD5 checksum on content recieved</h1></body></html>\r\n\r\n"
                connection_socket.send(error_message.encode())
                connection_socket.close()
                sys.exit()
            params = {'apikey': api_key, 'resource': md5_response}
            headers = {
                "Accept-Encoding": "gzip, deflate",
                "User-Agent" : "gzip,  My Python requests library example client or username"
            }
            
            try:
                response = requests.get('https://www.virustotal.com/vtapi/v2/file/report',
                    params = params, headers = headers)
            except:
                error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Could not get response from virus total</h1></body></html>\r\n\r\n"
                connection_socket.send(error_message.encode())
                connection_socket.close()
                sys.exit()
            if response.status_code == 204:
                error_message = "HTTP/1.0 200 OK\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Too may request to virustotal</h1></body></html>\r\n\r\n"
                connection_socket.send(error_message.encode())
            try:
                virustotal_response = response.json()
            except:
                error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>JSON decode error</h1></body></html>\r\n\r\n"
                connection_socket.send(error_message.encode())
                connection_socket.close()
                sys.exit()
            #need to check if request was succsesful
            if response.json()['response_code'] == 0:
                connection_socket.send(html_response)
            elif response.json()['response_code'] == 1:
                if response.json()['positives'] > 0:        
                    error_message = "HTTP/1.0 200 OK\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>This is malware so the content will not be sent to you</h1></body></html>\r\n\r\n"
                    connection_socket.send(error_message.encode())
                else:
                    connection_socket.send(html_response)
        else: #when the returned response is not ok we send back the error message from the get request made
            connection_socket.send(html_response)
        
        connection_socket.close()
        sys.exit()
    except KeyboardInterrupt:
        if connection_socket is not None:
            connection_socket.close()
        sys.exit()

#port being read as a command line argument
proxy_port = int(sys.argv[1])
api_key = sys.argv[2]

#connecting through localhost and creating a socket to bind to
server_address = ('localhost', proxy_port)
server_socket = socket(AF_INET, SOCK_STREAM)

# allow us to quickly reuse the port number...
server_socket.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)

server_socket.bind(server_address)
server_socket.listen(20)
print('The server is ready to receive')
connection = None

#continues loop looking for connection requests to the server
try:
    while True:
        connection, addr = server_socket.accept()
        print("new connection")
        process = Process(target=connection_request_handler, args=(connection, addr, api_key))
        try:
            process.start()
        except:
            error_message = "HTTP/1.0 400 Bad Request\r\n" + "Content-Type: text/html\r\n\r\n" + "<html><body><h1>Too many requests to handle</h1></body></html>\r\n\r\n"
            connection.send(error_message.encode())
        connection.close()
except KeyboardInterrupt:
    if connection is not None:
        connection.close()
    if server_socket is not None:
        server_socket.close()