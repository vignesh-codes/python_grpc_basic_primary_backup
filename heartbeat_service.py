import grpc
from concurrent import futures
import time
import threading
import heartbeat_service_pb2
import heartbeat_service_pb2_grpc
from google.protobuf import empty_pb2

class ViewServiceServicer(heartbeat_service_pb2_grpc.ViewServiceServicer):
    def __init__(self):
        self.heartbeat_times = {"primary": None, "backup1": None, "backup2": None}  # Track multiple backups

    def Heartbeat(self, request, context):
        self.heartbeat_times[request.service_identifier] = time.time()
        with open("heartbeat.txt", "a") as log_file:
            log_file.write(f"{request.service_identifier} is alive. Latest heartbeat received at {time.ctime()}\n")
        print(f"✅ {request.service_identifier} is alive.")
        return empty_pb2.Empty()

def check_failures(service):
    """Continuously checks for missed heartbeats every 5 seconds."""
    while True:
        current_time = time.time()
        for service_id, last_heartbeat in service.heartbeat_times.items():
            if last_heartbeat and (current_time - last_heartbeat > 10):  # If no heartbeat for 10 seconds
                with open("heartbeat.txt", "a") as log_file:
                    log_file.write(f"{service_id} might be down. Latest heartbeat received at {time.ctime(last_heartbeat)}\n")
                print(f"⚠️ {service_id} might be down! No heartbeat received since {time.ctime(last_heartbeat)}")
        time.sleep(5)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = ViewServiceServicer()
    heartbeat_service_pb2_grpc.add_ViewServiceServicer_to_server(service, server)
    server.add_insecure_port('[::]:50053')
    print("✅ Heartbeat monitor running on port 50053...")

    # Start failure detection thread with the same instance
    threading.Thread(target=check_failures, args=(service,), daemon=True).start()

    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
