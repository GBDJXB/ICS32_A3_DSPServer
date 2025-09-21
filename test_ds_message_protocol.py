import ds_protocol
import socket
import datetime

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 3001))
conn = ds_protocol.init(sock)
token = ''

# Existing user list:
# User1 user111
# User2 user222

def test_directmessage_before_authentiacte():
    global token
    response = ds_protocol.directmessage(conn, token, "Test Message", "User2", datetime.datetime.now().timestamp())
    assert response.type == 'error' and response.message == "Invalid user token."

def test_fetch_before_authenticate():
    global token
    response = ds_protocol.fetch(conn, token, "all")
    assert response['response']['type'] == 'error'

def test_authenticate_wrong_password():
    authen_msg = ds_protocol.authenticate(conn, "User1", "wrong_password")
    assert authen_msg.type == 'error' and authen_msg.message.startswith("Incorrect password")

def test_authenticate_correct():
    authen_msg = ds_protocol.authenticate(conn, "User1", "user111")
    global token
    token = authen_msg.token
    assert authen_msg.type == 'ok' and authen_msg.message.startswith("Welcome back")

def test_authenticate_already_active():
    authen_msg = ds_protocol.authenticate(conn, "User1", "user111")
    assert authen_msg.type == 'error' and authen_msg.message == "User already authenticated on the active session."

def test_directmessage_correct():
    global token
    response = ds_protocol.directmessage(conn, token, "Test Message", "User2", datetime.datetime.now().timestamp())
    assert response.type == 'ok' and response.message == "Direct message sent"

def test_directmessage_nonexistent_recipient():
    global token
    response = ds_protocol.directmessage(conn, token, "Test Message", "User404", datetime.datetime.now().timestamp())
    assert response.type == 'error' and response.message == "Unable to send direct message"

def test_fetch_all():
    global token
    response = ds_protocol.fetch(conn, token, "all")
    assert response['response']['type'] == 'ok' and "messages" in response['response']

def test_fetch_unread():
    global token
    response = ds_protocol.fetch(conn, token, "unread")
    assert response['response']['type'] == 'ok'

def test_fetch_wrong_argument():
    global token
    response = ds_protocol.fetch(conn, token, "wrong_argument")
    assert response['response']['type'] == 'error'
