# Primary-Backup Replication System with gRPC  

## 📌 Project Overview  
This project implements a **Primary-Backup Replication System** using **gRPC in Python**.  
It ensures **data consistency** by forwarding client requests to multiple backups and committing data only if at least one backup acknowledges the write.  
Additionally, a **heartbeat service** monitors the availability of the primary and backups.

---

## 📁 Project Structure  
── client.py # Client sends key-value writes to the primary │ \
── primary.py # Primary server (port 50051) │ that forwards writes to backups │ \
── backup.py # First backup server (port 50052) │ \
── backup2.py # Second backup server (port 50050) │ \
── heartbeat_service.py # Heartbeat server (post 50053) monitoring primary & backups │ \
── replication.proto # gRPC service definition for primary-backup communication │ \
── heartbeat_service.proto # gRPC service definition for heartbeat monitoring │ \
── requirements.txt # List of required Python packages │ \
── README.md 


---

## 🔧 Setup & Installation  

### **1️⃣ Install Dependencies**  
Ensure you have Python **3.8+** installed, then install the required packages:  
```sh
pip install -r requirements.txt
```

### 2️⃣ Generate gRPC Code from .proto Files
Run the following commands to generate Python gRPC files:

```sh
python -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. replication.proto
python -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. heartbeat_service.proto
```


# 🚀 Running the System
### 1️⃣ Start the Heartbeat Service
This monitors the primary and backups for failures:

```sh
python heartbeat_service.py # Runs on port 50053
```

### 2️⃣ Start Backup Servers
Run two separate backup instances:

```
python backup.py   # Runs on port 50052 (backup1)
python backup2.py  # Runs on port 50050 (backup2)
```
### 3️⃣ Start the Primary Server
```
python primary.py  # Runs on port 50051
```
### 4️⃣ Run the Client
The client sends key-value writes to the primary:
```
python client.py
```

Example input:
```
Enter key: 1  
Enter value: book  
```
Expected output:
```
Response from primary: Write successful
```
### 🛠 How It Works
✅ The client sends a key-value request to the primary.
✅ The primary forwards the request to both backups (backup.py & backup2.py).
✅ The primary commits the write only if at least one backup acknowledges it.
✅ The heartbeat service detects failures if any server stops sending heartbeats.

### 📜 Failure Handling
1️⃣ If a backup fails, the primary still commits if at least one backup is alive.
2️⃣ If the primary fails, backups continue running, but client writes will be lost until it restarts.
3️⃣ The heartbeat service logs failures in heartbeat.txt and prints warnings.

### 📄 Log Files

client.txt ->   Stores client write requests
primary.txt ->	Stores committed writes by primary
backup.txt ->	Stores received writes by backup1
backup2.txt ->	Stores received writes by backup2
heartbeat.txt ->  Tracks alive/down services

### 💡 Example heartbeat.txt Log
```
primary is alive. Latest heartbeat received at Wed Mar 05 12:30:00 2025
backup1 is alive. Latest heartbeat received at Wed Mar 05 12:30:05 2025
backup2 is alive. Latest heartbeat received at Wed Mar 05 12:30:10 2025
⚠️ primary might be down! No heartbeat received since Wed Mar 05 12:30:00 2025
```
# ❌ Simulating Failures
### 1️⃣ Kill the Primary
Stop primary.py using CTRL+C. You should see in heartbeat.txt:
```
⚠️ primary might be down! No heartbeat received since Wed Mar 05 12:30:00 2025
```
### 2️⃣ Kill One Backup
Stop backup.py using CTRL+C. If the second backup is still running, writes will continue.
If both backups fail, the primary will not commit writes.

### 3️⃣ Restart Servers
To recover from failure, restart any failed component using:

```
python primary.py
python backup.py
python backup2.py
```
Heartbeats will resume, and heartbeat.txt will update.
