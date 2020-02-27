#!/ust/bin/python

class AtlasError(Exception):
    ''' base class for Atlas Scientific based errors '''
    pass

class AtlasSyntaxError(AtlasError):
    ''' Raised when the Atlas Scientific component returns an error code of '2' '''
    def __init__(self,message=''):
        self.message = message
        
class AtlasTimeError(AtlasError):
    ''' Raised when the Atlas Scientific component returns an error code of '254' '''
    def __init__(self,message=''):
        self.message = message
        
class AtlasNoDataError(AtlasError):
    ''' Raised when the Atlas Scientific component returns an error code of '255' '''
    def __init__(self,message=''):
        self.message = message
    
