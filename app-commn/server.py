import base64
import jwt
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

SERVER_ID = "secure-backend-server-01"
ORCH_URL = "http://127.0.0.1:8001"  # Change to Machine A's real IP

app = FastAPI(title="Zero-Trust Processing Server")

# Self-generated server identity keys
SERVER_PVT = ed25519.Ed25519PrivateKey.generate()
SERVER_PUB_PEM = SERVER_PVT.public_key().public_bytes(
    encoding=serialization.Encoding.PEM, 
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode()

# Local cache to track consumed nonces (Constraint 2: No Replay)
CONSUMED_NONCES = set()
ORCHESTRATOR_PUB_KEY = None

class SecurePayload(BaseModel):
    task_token: str
    payload: str
    signature: str

@app.on_event("startup")
def register_with_authority():
    global ORCHESTRATOR_PUB_KEY
    try:
        resp = requests.post(f"{ORCH_URL}/register", json={
            "entity_id": SERVER_ID, "public_key": SERVER_PUB_PEM
        }).json()
        ORCHESTRATOR_PUB_KEY = serialization.load_pem_public_key(
            resp["orchestrator_public_key"].encode()
        )
        print("[*] Server identity registered successfully with Authority.")
    except Exception as e:
        print(f"[!] Critical Error: Cannot connect to Orchestrator at launch: {e}")

@app.post("/execute_task")
async def execute_task(data: SecurePayload):
    global CONSUMED_NONCES
    try:
        # 1. Decode & verify Task Token using the saved Orchestrator Public Key
        claims = jwt.decode(data.task_token, ORCHESTRATOR_PUB_KEY, algorithms=["EdDSA"])
        
        token_nonce = claims["jti"]
        client_id = claims["client_id"]
        task_id = claims["sub"]

        # Constraint 2 Validation: Block token reuse
        if token_nonce in CONSUMED_NONCES:
            raise HTTPException(status_code=403, detail="Credential reuse detected. Token is burned.")

        # 2. Constraint 3 Validation: Fetch Client Public Key from Orchestrator Network Endpoint
        client_resp = requests.get(f"{ORCH_URL}/get_key/{client_id}").json()
        client_pub_pem = client_resp["public_key"]
        client_pub_key = serialization.load_pem_public_key(client_pub_pem.encode())

        # Cryptographically verify the client's signature against raw payload
        client_pub_key.verify(base64.b64decode(data.signature), data.payload.encode())

        # 3. Validation passed successfully. Consume token nonce forever.
        CONSUMED_NONCES.add(token_nonce)
        print(f"[SUCCESS] Authorized Task {task_id} from {client_id}")
        return {"status": "SUCCESS", "message": f"Secured task processed: '{data.payload}'"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Task window lease has expired.")
    except ed25519.InvalidSignature:
        raise HTTPException(status_code=401, detail="Signature verification failed. Impersonation blocked.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failure: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9999)
