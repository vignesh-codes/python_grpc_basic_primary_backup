import grpc
from concurrent import futures
import time
import threading
import replication_pb2
import replication_pb2_grpc
import heartbeat_service_pb2
import heartbeat_service_pb2_grpc
from google.protobuf import empty_pb2  # Import Empty message type

BACKUP_IDENTIFIER = "backup2"

class Backup(replication_pb2_grpc.SequenceServicer):
    def __init__(self):
        self.data_store = {}

    def Write(self, request, context):  
        print(f"Received from primary: {request.key} -> {request.value}")

        # Store locally
        self.data_store[request.key] = request.value

        # Log the write operation
        with open("backup2.txt", "a") as log_file:
            log_file.write(f"{request.key} {request.value}\n")

        return replication_pb2.WriteResponse(ack="Backup write successful")  

def send_heartbeat():
    """Continuously sends heartbeats to the heartbeat service."""
    with grpc.insecure_channel('localhost:50053') as channel:
        stub = heartbeat_service_pb2_grpc.ViewServiceStub(channel)
        while True:
            try:
                stub.Heartbeat(heartbeat_service_pb2.HeartbeatRequest(service_identifier=BACKUP_IDENTIFIER))
                print(f"✅ {BACKUP_IDENTIFIER} heartbeat sent.")
            except grpc.RpcError:
                print(f"⚠️ Failed to send heartbeat for {BACKUP_IDENTIFIER}")
            
            time.sleep(5)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    replication_pb2_grpc.add_SequenceServicer_to_server(Backup(), server)
    server.add_insecure_port('[::]:50050')
    print(f"{BACKUP_IDENTIFIER} running on port 50050...")

    # Start heartbeat in a separate thread
    threading.Thread(target=send_heartbeat, daemon=True).start()

    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
