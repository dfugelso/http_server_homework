import os
import mimetypes
#import exceptions

def create_directory_list(dir_list):
    '''
    Create a text listing for a directory from a list.
    '''
    text = ''
    for filename in dir_list:
        text = text + filename + '\r\n'
    return text
    
def run_python_script(pyfile):
    import subprocess
    # pyfile = pyfile.replace ('/', '.')
    # pyfile = pyfile [:-3]
    #proc = subprocess.Popen(["python", "-c", "import {}".format(pyfile)], stdout=subprocess.PIPE)
    #proc = subprocess.Popen(["python {}".format(pyfile), "-c", ""], stdout=subprocess.PIPE)
    start_string = "python {}".format(pyfile)
    print start_string
    proc = subprocess.Popen(["python", pyfile, ""], stdout=subprocess.PIPE)
    return proc.communicate()[0]
    
#Set root directory (i.e. Home) for available resources    
root_directory = './webroot'
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
        return create_directory_list(os.listdir(root_directory)), 'text/plain'

    #Strip leading '/'    
    uri = uri[1:]

    #Walk through root directory structure
    for (dirpath, dirnames, filenames) in os.walk(root_directory): 
        uricmp = dirpath[rootLength+1:]
        for dir in dirnames:
            if os.path.join(uricmp, dir) == uri:
                return create_directory_list(os.listdir(os.path.join(dirpath, dir))), 'text/plain'
        for fname in filenames:
            test_path =  os.path.join(uricmp, fname).replace('\\', '/') 
            if test_path == uri:
                extension = os.path.splitext(fname)[1]
                with open(os.path.join(dirpath, fname), 'rb') as f:
                    body = f.read()
                return body, mimetypes.types_map[extension]
    raise NameError
            
            
if __name__ == '__main__':
    resource_list = ['/', '/\images', '/images/sample_1.png', '/images','/sample.txt','/images/TestDepth/t.txt','/Notthere.txt','/make_time.py']
    print run_python_script ("webroot/make_time.py")
    for uri in resource_list:
        try:
            body, type = resolve_uri(uri)
            print '{} is {}'.format(uri, type)
            if type == 'text/plain':
                print body
        except (NameError, IOError):
            print 'Uri {} Not Found'.format(uri)

  
   