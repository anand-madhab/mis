import time
import uuid
import jwt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

app = FastAPI(title="Zero-Trust Orchestrator Authority")

# Asymmetric Root of Trust Key Pair
ORCH_PVT = ed25519.Ed25519PrivateKey.generate()
ORCH_PUB_PEM = ORCH_PVT.public_key().public_bytes(
    encoding=serialization.Encoding.PEM, 
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode()

# Key registry to store Node IDs -> Public Key strings
PUBLIC_KEY_REGISTRY = {}

class RegisterRequest(BaseModel):
    entity_id: str
    public_key: str

class TokenRequest(BaseModel):
    task_id: str
    client_id: str
    server_id: str

@app.post("/register")
def register_node(data: RegisterRequest):
    PUBLIC_KEY_REGISTRY[data.entity_id] = data.public_key
    print(f"[+] Successfully registered identity: {data.entity_id}")
    return {"status": "REGISTERED", "orchestrator_public_key": ORCH_PUB_PEM}

@app.get("/get_key/{entity_id}")
def get_key(entity_id: str):
    if entity_id not in PUBLIC_KEY_REGISTRY:
        raise HTTPException(status_code=404, detail="Entity identity not found")
    return {"public_key": PUBLIC_KEY_REGISTRY[entity_id]}

@app.post("/issue_token")
def issue_token(data: TokenRequest):
    if data.client_id not in PUBLIC_KEY_REGISTRY:
        raise HTTPException(status_code=400, detail="Requested client is unregistered")
        
    payload = {
        "iss": "orchestrator",
        "sub": data.task_id,
        "jti": str(uuid.uuid4()),  # One-time cryptographic nonce
        "client_id": data.client_id,
        "server_id": data.server_id,
        "exp": time.time() + 60    # Ephemeral window: strictly 60 seconds
    }
    token = jwt.encode(payload, ORCH_PVT, algorithm="EdDSA")
    return {"status": "ISSUED", "token": token}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
