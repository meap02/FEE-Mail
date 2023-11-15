import re
from prompt_toolkit.validation import Validator, ValidationError

class EmailValidator(Validator):
    '''This class is used to validate an email address'''
    def validate(self, email):
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return True
        else:
            raise ValidationError(message="Please enter valid email")
        
class SeverValidator(Validator):
    '''This class is used to validate an smtp server'''
    def validate(self, smtp_server):
        if re.match(r"[^\.]+\.[^\.]+\.[^\.]+", smtp_server):
            return True
        else:
            raise ValidationError(message="Please enter valid smtp server")

class PortValidator(Validator):
    '''This class is used to validate an smtp port'''
    def validate(self, smtp_port):
        if re.match(r"^((6553[0-5])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))$", smtp_port):
            return True
        else:
            raise ValidationError(message="Please enter valid port number")