from concurrent import futures

import grpc
import chat_pb2
import chat_pb2_grpc

class ChatterServicer(chat_pb2_grpc.ChatterServicer):
    def __init__(self):
        self.registered_user = []
        self.chat_pair = {}
        self.messages = {}
        super().__init__()

    def sendMessage(self, request, context):
        print("send message request have been made")
        reply_message = chat_pb2.MessageRequest()
        if self.messages.get(request.receiver) == None:
            reply_message.message = f"{request.receiver} is not registered"
            return reply_message
        print("xd")
        print(self.messages[request.receiver])
        tmp = {}
        tmp['sender'] = request.sender
        tmp['receiver'] = request.receiver
        tmp['message'] = request.message
        self.messages[request.receiver].append(tmp)
        print(self.messages[request.receiver])
        print("successssssssssssssssssssssssss")
        reply_message.message = f"message to {request.receiver} has been added to queue"
        return reply_message

    def register(self, request, context):
        print("register request received")
        host_name = request.user_name
        if host_name in self.registered_user:
            reply = chat_pb2.StatusResponse(
                responseCode=1,
                responseMessage="fail to register, username already exist"
            )
        else:
            self.registered_user.append(host_name)
            reply = chat_pb2.StatusResponse(
                responseCode=0,
                responseMessage="user registered"
            )
        return reply

    def findPair(self, request, context):
        print("find pair request has been made")
        target_name = request.target_name
        if target_name in self.registered_user:
            reply = chat_pb2.StatusResponse(
                responseCode=0,
                responseMessage="target found"
            )
        else:
            reply = chat_pb2.StatusResponse(
                responseCode=2,
                responseMessage="target has not registered yet"
            )
        return reply

    def connectPair(self, request, context):
        print("Connection request has been made")
        self.chat_pair[request.host_name] = request.target_name
        self.chat_pair[request.target_name] = request.host_name
        self.messages[request.host_name] = []
        self.messages[request.target_name] = []
        reply = chat_pb2.PairConnection(
            sender_name=request.host_name,
            receiver_name=request.target_name,
            is_connection_created=1
        )
        return reply

    def getFromQueue(self, request, context):
        print("getFromQueue message received")
        print(f"read from {request.read_from}")
        print(self.messages)

        if self.messages.get(request.read_from) == []:
            reply = chat_pb2.MessageRequest(
                sender='',
                receiver='',
                message='no incoming message'
            )
            yield reply
            return

        queue = self.messages[request.read_from]
        print(f"queue: {queue}")
        for message in queue:
            messageRequest = chat_pb2.MessageRequest(
                sender=message['sender'],
                receiver=message['receiver'],
                message=message['message']
            )
            yield messageRequest
        self.messages[request.read_from] = []



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    chat_pb2_grpc.add_ChatterServicer_to_server(ChatterServicer(), server)
    server.add_insecure_port("localhost:50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

