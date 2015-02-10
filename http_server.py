import socket
import sys
import os
import mimetypes

def response_ok():
    """returns a basic HTTP response"""
    resp = []
    resp.append("HTTP/1.1 200 OK")
    resp.append("Content-Type: text/plain")
    resp.append("")
    resp.append("this is a pretty minimal response")
    return "\r\n".join(resp)


def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 405 Method Not Allowed")
    resp.append("")
    return "\r\n".join(resp)


def parse_request(request):
    first_line = request.split("\r\n", 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    print >>sys.stderr, 'request is okay'
    return uri
    
#Set root directory (i.e. Home) for available resources    
root_directory = '.\webroot'
def resolve_uri (uri):
    '''
    Find the resources on disk that the URI points to. 
    Return content, type
    Raise NotFound error if resource is not there
    '''
    rootLength = len(root_directory)
    
    for (dirpath, dirnames, filenames) in os.walk(root_directory): 
    
        #Check against string w/o root_directory in it
        uricmp = dirpath[rootLength+1:]
        
        #Check for folder first
        for dir in dirnames:
            if os.path.join(uricmp, dir) == uri:
                return os.listdir(os.path.join(dirpath, dir)), 'test/plain'
                
        for  fname in filenames:
            #Windows, ugh, again.
            test_path =  os.path.join(uricmp, fname).replace('\\', '/') 
            if test_path == uri:
                with open(os.path.join(dirpath, fname), 'rb') as f:
                    extension = os.path.splitext(fname)[1]
                    return f.read(), mimetypes.types_map[extension]
    raise EnvironmentError


def server():
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print >>sys.stderr, "making a server on %s:%s" % address
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print >>sys.stderr, 'waiting for a connection'
            conn, addr = sock.accept() # blocking
            try:
                print >>sys.stderr, 'connection - %s:%s' % addr
                request = ""
                while True:
                    data = conn.recv(1024)
                    request += data
                    if len(data) < 1024 or not data:
                        break

                try:
                    uri = parse_request(request)
                except NotImplementedError:
                    response = response_method_not_allowed()
                else:
                    # replace this line with the following once you have
                    # written resolve_uri
                    response = response_ok()
                    # content, type = resolve_uri(uri) # change this line

                    ## uncomment this try/except block once you have fixed
                    ## response_ok and added response_not_found
                    # try:
                    #     response = response_ok(content, type)
                    # except NameError:
                    #     response = response_not_found()

                print >>sys.stderr, 'sending response'
                conn.sendall(response)
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
