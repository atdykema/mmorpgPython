from client import *
from client_functions import *

request_connection_thread = threading.Thread(target=request_connection, args=())
request_connection_thread.start()

wait_for_connection_update()

receive_thread = threading.Thread(target=client_receive, args=())
receive_thread.start()

send_thread = threading.Thread(target=client_send, args=())
send_thread.start()