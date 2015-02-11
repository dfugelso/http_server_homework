import socket
import sys
import os
import mimetypes

def response_ok(body, mimetype):
    """returns a basic HTTP response"""
    resp = []
    resp.append("HTTP/1.1 200 OK")
    resp.append("Content-Type: {}".format(mimetype))
    resp.append("")
    if 'text' in mimetype:
        resp.append(body)
    else:
        resp.append(body)   
    return "\r\n".join(resp)


def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 405 Method Not Allowed")
    resp.append("")
    return "\r\n".join(resp)
 
def response_internal_server_error():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 500 Internal Server Error")
    resp.append("")
    return "\r\n".join(resp) 

    
def response_not_found ():
    """returns a 404 Method Not Found"""
    resp = []
    resp.append("HTTP/1.1 404 Not Found")
    resp.append("")
    return "\r\n".join(resp)

def response_bad_value_error ():
    """returns a erro when Chrome keeps trying to get things"""
    resp = []
    resp.append("HTTP/1.1 400 What are you looking for")
    resp.append("")
    return "\r\n".join(resp)

def parse_request(request):
    first_line = request.split("\r\n", 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    print >>sys.stderr, 'request is okay'
    return uri
 
def run_python_script(pyfile):
    import subprocess
    pyfile = pyfile.replace ('/', '.')
    pyfile = pyfile [:-3]
    proc = subprocess.Popen(["python", "-c", "import {}"], stdout=subprocess.PIPE)
    return proc.communicate()[0]
 
def create_directory_list(dir_list, uri):
    '''
    Create a text listing for a directory from a list.
    '''
    text = '<!DOCTYPE html>\r\n<html>\r\n<body>\r\n'
    for filename in dir_list:
        if uri == '':
            url = 'http://localhost:10000/{}'.format (filename)
        else:
            url = 'http://localhost:10000/{}/{}'.format (uri, filename)
        link = '<a href="{}">{}</a>\r\n'.format (url, filename)
        print link
        text = text + link
    text = text + '</body>\r\n</html>\r\n'
    return text
    
    
#Set root directory (i.e. Home) for available resources    
root_directory = '.\webroot'
def resolve_uri (uri):
    '''
    Find the resources on disk that the URI points to. 
    Return content, type
    Raise NotFound error if resource is not there
    '''
    rootLength = len(root_directory)
    uri = uri.replace("\\", '') 
    print 'this uri {}'.format(uri)

    #Check for root directory
    if uri == "/":
        return create_directory_list(os.listdir(root_directory), ''), 'text/html'

    #Strip leading '/'    
    uri = uri[1:]

    #Walk through root directory structure
    for (dirpath, dirnames, filenames) in os.walk(root_directory): 
        uricmp = dirpath[rootLength+1:]
        for dir in dirnames:
            if os.path.join(uricmp, dir) == uri:
                return create_directory_list(os.listdir(os.path.join(dirpath, dir)),uri), 'text/html'
        for fname in filenames:
            test_path =  os.path.join(uricmp, fname).replace('\\', '/') 
            if test_path == uri:
                extension = os.path.splitext(fname)[1]
                if extension == ".py":
                    body = run_python_script(os.path.join(dirpath, fname))
                else:
                    with open(os.path.join(dirpath, fname), 'rb') as f:
                        body = f.read()
                return body, mimetypes.types_map[extension]
    raise NameError
            


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
                except ValueError:
                    response = response_bad_value_error()
                else:
                    # Try to get URI and resolve it. Catch NameError for resource not found
                    try:
                        content, type = resolve_uri(uri)
                        print '{} is type {}'.format(uri,type)
                        response = response_ok(content, type)
                    except NameError:
                        print 'failed to find: {} len {}'.format(uri, len(uri))
                        response = response_not_found()

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
