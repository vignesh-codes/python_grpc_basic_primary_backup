import grpc
import replication_pb2
import replication_pb2_grpc

def send_request(key, value):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = replication_pb2_grpc.SequenceStub(channel)
        response = stub.Write(replication_pb2.WriteRequest(key=key, value=value))
        with open("client.txt", "a") as log_file:
            log_file.write(f"{key} {value}\n")
        print(f"Response from primary: {response.ack}")

if __name__ == "__main__":
    while True:
        key = input("Enter key: ")
        value = input("Enter value: ")
        send_request(key, value)
