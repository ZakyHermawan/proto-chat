import grpc
import chat_pb2
import chat_pb2_grpc

import time
from threading import Thread

def keep_reading(username, stub):
    while True:
        request = chat_pb2.ReadQueueRequest(read_from=username)
        response_iterator = stub.getFromQueue(request)
        for response in response_iterator:
            if response.sender == '' and response.receiver == '': # means error
                time.sleep(1)
                continue
            print(f"message from {response.sender}: {response.message}")

def send_messages(username, pair_name, stub):
    """
    Allow the user to send messages.
    """
    while True:
        try:
            message = input("Insert message: ")
            msg_request = chat_pb2.MessageRequest(sender=username, receiver=pair_name, message=message)
            response = stub.sendMessage(msg_request)
            print(f"Server response: {response}")
        except grpc.RpcError as e:
            print(f"Error sending message: {e}")
            break

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = chat_pb2_grpc.ChatterStub(channel)
    try:
        stub = chat_pb2_grpc.ChatterStub(channel)
        registered = 0
        while not registered:
            name = input("Insert username: ")
            register_request = chat_pb2.RegisterRequest(user_name=name)
            request_reply = stub.register(register_request)
            if request_reply.responseCode == 0:
                registered = 1
            else:
                print("Username has been taken")

        print("registration success")
        paired = 0
        while not paired:
            pair_name = input("Insert target name: ")
            pair_request = chat_pb2.FindPairRequest(target_name=pair_name)
            request_reply = stub.findPair(pair_request)
            if request_reply.responseCode == 0:
                connection_request = chat_pb2.ConnectPairRequest(
                    host_name=name,
                    target_name=pair_name,
                    connection_type=0
                )
                request_reply = stub.connectPair(connection_request)
                if request_reply.is_connection_created:
                    paired = 1
            else:
                print("cannot pairing (target  has not registered yet)")
                continue
        print("connection estabilished")
        reader_thread = Thread(target=keep_reading, args=[name, stub])
        sender_thread = Thread(target=send_messages, args=(name, pair_name, stub))
        reader_thread.start()
        sender_thread.start()
        reader_thread.join()
        sender_thread.join()

    except grpc.RpcError as e:
        print(f"gRPC error: {e}")
    finally:
        channel.close()

if __name__ == '__main__':
    run()

