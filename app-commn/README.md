# Ephemeral Zero-Trust M2M Authentication System

This project implements a secure, zero-trust, and ephemeral Machine-to-Machine (M2M) communication system across three separate network environments using Python and FastAPI. It ensures that no machine trusts another by default, and that cryptographic trust automatically self-destructs the moment a task is completed.

## 🛠️ System Architecture & Component Breakdown

### 1. orchestrator.py (Machine A)
Acts as an isolated Root of Trust and Identity Provider. It maintains a secure registry of public keys and issues tightly scoped, asymmetric, short-lived task tokens (JWTs) using Ed25519 signatures.

### 2. server.py (Machine B)
The defensive processing engine that treats all incoming requests as hostile. It validates the structural authenticity of task tokens against the Orchestrator, checks a local cache to prevent token reuse, verifies the client's cryptographic signature, and executes authorized tasks.

### 3. client.py (Machine C)
The initiating application that coordinates the secure lifecycle of a transaction. It registers its public identity, fetches a single-use lease token from the Orchestrator, cryptographically signs its data payload using its local private key, and triggers automated security test cases against the Server.

---

## 🚀 How to Deploy and Run

### Prerequisites
Run this command on **all three** Ubuntu machines to install the required production-grade libraries:
```bash
pip3 install fastapi uvicorn PyJWT cryptography requests
```

### Step 1: Configure Network IPs
1. Identify the IP address of your machines.
2. Open `server.py` and `client.py`.
3. Update the `ORCH_URL` and `SERVER_URL` variables at the top of the scripts with your real machine IPs instead of `127.0.0.1`.

### Step 2: Execute the Services
Open three separate terminal windows (one for each machine) and run the scripts in this exact sequence:

1. **On Machine A (Orchestrator):**
   ```bash
   python3 orchestrator.py
   ```
2. **On Machine B (Server):**
   ```bash
   python3 server.py
   ```
3. **On Machine C (Client):**
   ```bash
   python3 client.py
   ```

---

## 🎯 What to Expect (Console Output)

When you execute `client.py` on Machine C, the script runs three distinct pipeline scenarios. Your terminals will print out the following verifications:

*   **STEP 1 (Valid Flow):** The server verifies the token and signature, printing `[SUCCESS] Authorized Task...`. The client receives a `200 OK` response confirming the task was processed safely.
*   **STEP 2 (Credential Reuse Check):** The client immediately tries to reuse the exact same token for a secondary message. The server catches this using its nonce cache and returns a `403 Forbidden` error with the message: `Credential reuse detected. Token is burned.`
*   **STEP 3 (Lifespan Expiry):** Any token used past its strict 60-second Time-To-Live (TTL) window is intercepted by the server's decoding layer and met with a `401 Unauthorized` error.

---

## 🏆 What We Achieved

1. **Isolated Environments:** The components share zero memory space, files, or local databases, successfully isolating security boundaries.
2. **Zero-Trust Default:** The server assumes all traffic is hostile and dynamically fetches keys from the Identity Provider to mathematically prove a client's identity before running any code.
3. **Ephemeral Lifespans:** Trust is bound strictly to a single task context. By combining a 60-second TTL with single-use nonce tracking, credentials immediately self-destruct upon consumption, making token theft or replay attacks impossible.
4. **Anti-Impersonation:** By utilizing Ed25519 asymmetric cryptography, a compromised machine can never forge signatures or spoof the identity of another trusted node.
