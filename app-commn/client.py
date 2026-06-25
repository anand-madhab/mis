import base64
import requests
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

CLIENT_ID = "trusted-analytics-client"
ORCH_URL = "http://127.0.0.1:8001"   # Update to Machine A's real IP
SERVER_URL = "http://127.0.0.1:9999" # Update to Machine B's real IP

# Generate isolated client identities
CLIENT_PVT = ed25519.Ed25519PrivateKey.generate()
CLIENT_PUB_PEM = CLIENT_PVT.public_key().public_bytes(
    encoding=serialization.Encoding.PEM, 
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode()

def run_pipeline():
    # 1. Register local Identity with Authority
    requests.post(f"{ORCH_URL}/register", json={"entity_id": CLIENT_ID, "public_key": CLIENT_PUB_PEM})
    print("[*] Client initialization complete.")

    # 2. Request ephemeral task lease token from Orchestrator
    print("\n--- STEP 1: Fetching Short-Lived Token ---")
    token_resp = requests.post(f"{ORCH_URL}/issue_token", json={
        "task_id": "TASK-HTTP-99", "client_id": CLIENT_ID, "server_id": "secure-backend-server-01"
    }).json()
    token = token_resp["token"]
    print(f"Token acquired.")

    # 3. Sign and execute valid payload block
    print("\n--- STEP 2: Executing Authorized Request ---")
    payload_data = "Export system metrics snapshot #401"
    raw_sig = CLIENT_PVT.sign(payload_data.encode())
    sig_b64 = base64.b64encode(raw_sig).decode()

    response = requests.post(f"{SERVER_URL}/execute_task", json={
        "task_token": token, "payload": payload_data, "signature": sig_b64
    })
    print(f"Server Status Code: {response.status_code}")
    print(f"Server Body: {response.json()}")

    # 4. Attempt credential reuse to prove Constraint 2
    print("\n--- STEP 3: Attempting Replay/Reuse (Should Fail) ---")
    replay_response = requests.post(f"{SERVER_URL}/execute_task", json={
        "task_token": token, "payload": "Malicious secondary command payload insertion", "signature": sig_b64
    })
    print(f"Server Status Code: {replay_response.status_code}")
    print(f"Server Body: {replay_response.json()}")

if __name__ == "__main__":
    run_pipeline()
