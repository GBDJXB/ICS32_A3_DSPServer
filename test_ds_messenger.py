import ds_protocol
import socket
import datetime
import ds_messenger

# authencicate has been tested in test_ds_message_protocol,
# thus there is no need to test it again here.

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 3001))
conn = ds_protocol.init(sock)
user = ds_messenger.DirectMessenger(conn, 'User1', 'user111')
authed_msg= ds_protocol.authenticate(dsp_conn=conn, username='User1', password='user111')
user.token = authed_msg.token

def test_send_correct():
    response = user.send("Test Message", "User2")
    assert response

def test_send_nonexistent_recipient():
    response = user.send("Test Message", "User404")
    assert response is False

def test_retrieve_all():
    response = user.retrieve_all()
    assert response['response']['type'] == 'ok' and len(response['response']['messages']) != 0

def test_retrieve_new():
    response = user.retrieve_new()
    assert response['response']['type'] == 'ok' and len(response['response']['messages']) == 0

print(user.send("Test Message", "User2"))
