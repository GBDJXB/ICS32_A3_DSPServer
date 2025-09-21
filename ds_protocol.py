'''
ds_protocol.py clarifies how users should communicate with the server.
When a user connects to the server for the first time, 
the server will authentiate the user first and provide a one-time
token for all the communication later.
'''
# ds_protocol.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Xinrong Le
# xinrol5@uci.edu
# 14083389

import json
from collections import namedtuple
import socket

# Create a namedtuple to hold the values we expect to retrieve from json messages.
ServerResponse = namedtuple('ServerResponse', ['type', 'message', 'token'])
class InvalidProtocolError(Exception):
    '''
    An error that is raised when the socket is incorrect.
    To be honest I'm not exactly sure what it is,
    but since it's there when I got the .py file,
    maybe it's better to leave it as it is.
    '''

def extract_json(json_msg: str) -> ServerResponse:
    '''
    Call the json.loads function on a json string and convert it to a DataTuple object
    '''
    try:
        json_obj = json.loads(json_msg)
        print("json_obj:", json_obj)
        _type = json_obj['response']['type']
        message = json_obj['response']['message']
        if 'token' in json_obj['response']:
            token = json_obj['response']['token']
        else:
            token = ''
    except json.JSONDecodeError:
        print("Json cannot be decoded.")
    return ServerResponse(_type, message, token)

DSPConnection = namedtuple('DSPConnection', ['socket', 'send', 'recv'])

def init(sock: socket) -> DSPConnection:
    '''
    Create socket files for user and server to write in.
    '''
    try:
        f_send = sock.makefile('wb')
        f_recv = sock.makefile('rb')
        print(f_recv, type(f_recv))
    except Exception as ex:
        raise InvalidProtocolError from ex
    return DSPConnection(socket = sock, send = f_send, recv = f_recv)


def authenticate(dsp_conn: DSPConnection, username: str, password: str) -> ServerResponse:
    '''
    When a user connects to the server for the first time,
    a token will be generated and provided back to the user.
    All information sent back to the user will be returned
    for potential debugging.
    '''
    request = {'authenticate': {'username': username, 'password': password}}
    request_json = json.dumps(request)
    dsp_conn.send.write(request_json.encode())
    dsp_conn.send.flush()
    response = extract_json(dsp_conn.recv.readline())
    return response


def directmessage(dsp_conn: DSPConnection,
                  token: str,
                  entry: str,
                  recipient:str,
                  timestamp: float) -> ServerResponse:
    '''
    Send a message from user to the server.
    Returns the response of the server (Success or fail)
    '''
    request = {'token': token, 'directmessage': {'entry': entry,
                                                 'recipient': recipient,
                                                 'timestamp': timestamp}}
    request_json = json.dumps(request)




    dsp_conn.send.write(request_json.encode())
    dsp_conn.send.flush()
    response = extract_json(dsp_conn.recv.readline())
    return response


def fetch(dsp_conn: DSPConnection, token: str, mode: str) -> dict:
    '''
    Request all contact information relevant to the
    token holder (the user).
    Can return either all or just unread messages.
    Mind that a DICTIONARY is returned.
    (Why is this inconsistent with others...)
    '''
    request = {'token': token, 'fetch': mode}
    request_json = json.dumps(request)
    dsp_conn.send.write(request_json.encode())
    dsp_conn.send.flush()
    response = json.loads(dsp_conn.recv.readline())
    return response
