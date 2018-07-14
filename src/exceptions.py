

class UserException(Exception):
    
    def __init__(self, message, details):
        self.message = message
        self.details = details
        
        super(UserException, self).__init__(message)