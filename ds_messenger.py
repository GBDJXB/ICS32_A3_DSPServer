'''
ds_messenger defines a message and provides DirectMessenger for
more convenient connection between GUI and the server.
'''
# ds_messenger.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Xinrong Le
# xinrol5@uci.edu
# 14083389

import datetime
import ds_protocol

class DirectMessage:
    '''
    DirectMessage represents a basic piece of message.
    '''
    def __init__(self):
        self.recipient = None
        self.message = None
        self.sender = None
        self.timestamp = None

class DirectMessenger:
    '''
    DirectMessenger is a media betwen a3 and server.
    It contains the socket required to connect to the server
    and user information.
    It can also send a single message to another user, 
    or get chatting records from server.
    '''
    def __init__(self, dsuserver=None, username=None, password=None):
        self.token = None
        self.dsuserver = dsuserver
        self.username = username
        self.password = password
	# more code should go in here

    def send(self, message:str, recipient:str) -> bool:
        '''Send a single message to the server.'''
        # must return true if message successfully sent, false if send failed.
        try:
            response = ds_protocol.directmessage(self.dsuserver,
                                             self.token,
                                             message,
                                             recipient,
                                             datetime.datetime.now().timestamp())
            return response.type == 'ok'
        except Exception as ex:
            print(f"Error: {ex}")
            return False

    def retrieve_new(self) -> dict:
        '''Request all the unread messages from the server.'''
        # must return a list of DirectMessage objects containing all new messages
        try:
            response = ds_protocol.fetch(self.dsuserver, self.token, 'unread')
            return response
        except Exception as ex:
            print(f"Error: {ex}")
            return {}
        

    def retrieve_all(self) -> dict:
        '''Request all messages from the server.'''
        # must return a list of DirectMessage objects containing all messages
        try:
            response = ds_protocol.fetch(self.dsuserver, self.token, 'all')
            return response
        except Exception as ex:
            print(f"Error: {ex}")
            return {}
