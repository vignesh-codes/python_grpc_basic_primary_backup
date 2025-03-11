import grpc
from concurrent import futures
import time
import threading
import replication_pb2
import replication_pb2_grpc
import heartbeat_service_pb2
import heartbeat_service_pb2_grpc

def send_heartbeat(identifier):
    with grpc.insecure_channel('localhost:50053') as channel:
        stub = heartbeat_service_pb2_grpc.ViewServiceStub(channel)
        while True:
            try:
                stub.Heartbeat(heartbeat_service_pb2.HeartbeatRequest(service_identifier=identifier))
                print(f"✅ {identifier} heartbeat sent.")
                time.sleep(5)
            except grpc.RpcError:
                print(f"⚠️ Failed to send heartbeat for {identifier}")

class Primary(replication_pb2_grpc.SequenceServicer):
    def __init__(self):
        self.data_store = {}

    def Write(self, request, context):
        print(f"Received request: {request.key} -> {request.value}")

        # Attempt to forward request to backup1 (50052)
        backup1_ack = False
        try:
            with grpc.insecure_channel('localhost:50052') as channel:
                stub = replication_pb2_grpc.SequenceStub(channel)
                response = stub.Write(replication_pb2.WriteRequest(key=request.key, value=request.value))
                if response.ack == "Backup write successful":
                    backup1_ack = True
                    print("✅ Backup 1 acknowledged the write.")
        except grpc.RpcError:
            print("⚠️ Backup 1 is unreachable.")

        # Attempt to forward request to backup2 (50050)
        backup2_ack = False
        try:
            with grpc.insecure_channel('localhost:50050') as channel:
                stub = replication_pb2_grpc.SequenceStub(channel)
                response = stub.Write(replication_pb2.WriteRequest(key=request.key, value=request.value))
                if response.ack == "Backup write successful":
                    backup2_ack = True
                    print("✅ Backup 2 acknowledged the write.")
        except grpc.RpcError:
            print("⚠️ Backup 2 is unreachable.")

        # Commit to primary if at least one backup acknowledged
        if backup1_ack or backup2_ack:
            self.data_store[request.key] = request.value

            # Log to file
            with open("primary.txt", "a") as log_file:
                log_file.write(f"{request.key} {request.value}\n")

            print(f"✅ Committed write {request.key} -> {request.value} to primary.")
            return replication_pb2.WriteResponse(ack="Write successful")
        else:
            print(f"❌ Write {request.key} -> {request.value} failed. No backup acknowledged.")
            return replication_pb2.WriteResponse(ack="Write failed - No backup available")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    replication_pb2_grpc.add_SequenceServicer_to_server(Primary(), server)
    server.add_insecure_port('[::]:50051')
    print("Primary running on port 50051...")

    # Start heartbeat in a separate thread
    threading.Thread(target=send_heartbeat, args=("primary",), daemon=True).start()

    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
