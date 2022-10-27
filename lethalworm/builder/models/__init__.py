from __future__ import annotations
from dataclasses import dataclass,asdict


@dataclass
class EmailTime:
    """Class for storing message session start and duration
    
    args:
        start   (str):
        duration (str):
    """
    start:str
    duration:str

@dataclass
class EmailAddress:
    """Class for storing From and To addresses
    
    args:
        from   (str):
        to (str):
    """
    from_:str
    to:str

@dataclass
class Email:
    """Class for storing Email Messages
    
    args:
        time      (EmailTime):
        sessionid (str):
        client    (str):
        messageid (str):
        address   (EmailAddress):
        status    (str):
    """
    time:EmailTime
    sessionid:str
    client:str
    messageid:str
    address:EmailAddress
    status:str
    
    @classmethod
    def build_from_template(cls, message_template, sessionid:str,time:EmailTime) -> Email:
        address = EmailAddress(from_=message_template['from'],to=message_template['to'])

        return Email(
            time=time,
            sessionid=sessionid,
            messageid=message_template['message-id'],
            address=address,
            client=message_template['client'],
            status=message_template['status']
        )
    
    def json(cls) -> dict:
        
        object_as_dict = asdict(cls)
        object_as_dict['address']['from'] = object_as_dict['address']['from_']
        
        del object_as_dict['address']['from_']

        return object_as_dict