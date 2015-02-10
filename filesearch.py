import os
import mimetypes
#import exceptions

root_directory = '.\webroot'
def resolve_uri (uri):
    '''
    Find the resources on disk that the URI points to. 
    Return content, type
    Raise NotFound error if resource is not there
    '''
    rootLength = len(root_directory)
    

    for (dirpath, dirnames, filenames) in os.walk(root_directory): 
        uricmp = dirpath[rootLength+1:]
        for dir in dirnames:
            if os.path.join(uricmp, dir) == uri:
                return os.listdir(os.path.join(dirpath, dir)), 'test/plain'
        for  fname in filenames:
            test_path =  os.path.join(uricmp, fname).replace('\\', '/') 
            if test_path == uri:
                with open(os.path.join(dirpath, fname), 'rb') as f:
                    extension = os.path.splitext(fname)[1]
                    return f.read(), mimetypes.types_map[extension]
    raise EnvironmentError
            
if __name__ == '__main__':
    resource_list = ['images/sample_1.png', 'images','sample.txt','images/TestDepth/t.txt','Notthere.txt','make_time.py']
    for uri in resource_list:
        try:
            body, type = resolve_uri(uri)
            print '{} is {}'.format(uri, type)
        except (EnvironmentError, IOError):
            print 'Uri {} Not Found'.format(uri)

  
   