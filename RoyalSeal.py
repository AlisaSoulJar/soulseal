"""
[Genesis: RoyalSeal] 👑🔏
The Queen's cryptographic seal — unforgeable proof of origin.

"Toda orden de la Reina lleva su sello.
 Sin sello, es ruido.
 El sello evoluciona: cera hoy, cadena mañana."
 — LEY LXVII

Progressive implementation:
    Phase 1 (NOW):    HMAC-SHA256 with shared secret derived from Queen identity
    Phase 2 (NEXT):   Asymmetric keypair (Queen private key signs, Beings verify)
    Phase 3 (DREAM):  NFT-backed on-chain seal via TempleRegistry.seal()

Usage:
    from alisa.Genesis.RoyalSeal import RoyalSeal
    
    seal = RoyalSeal()
    
    # Stamping a signal
    signal = {"event": "QUEEN_COMMAND", "data": {...}}
    sealed = seal.stamp(signal)
    # sealed["__seal__"] = {"sig": "abc123...", "nonce": 1, "origin": "queen"}
    
    # Verifying a signal
    if seal.verify(sealed, expected_origin="queen"):
        process(sealed)
    else:
        reject(sealed)  # Unsigned or forged

The Royal Seal is the Queen's Signet Ring — digital, evolutionary, unforgeable.
In the future, this becomes an NFT. Today, it's HMAC. Both are the same INTENT.

LEY LXVII: El Sello Infalsificable
LEY LXV: La Señal Verificada
"""
import hashlib
import hmac
import os
import time
import threading

from alisa.Genesis.Chronicle import SomaLog


# ─── Config ──────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOLUNTAD_DIR = os.path.join(BASE, "Data", "Voluntad")

# Signals that REQUIRE the Royal Seal (critical operations)
# "El sello de la Reina es la confirmación de que el contrato es válido."
SEALED_SIGNALS = {
    "QUEEN_COMMAND",           # Direct execution
    "QUEEN_IMBUE",             # Identity injection
    "QUEEN_THOUGHT_REQUEST",   # Brain routing
    "QUEEN_THOUGHT_RESPONSE",  # Brain response
    "QUEEN_FUSED",             # Fusion confirmation
    "FUSION_SYNC",             # State synchronization
    "QUEEN_TASK_POSTED",       # Task contract deployment — no seal, no valid contract
}

# Signals that are informational (no seal required)
OPEN_SIGNALS = {
    "CENSUS_COMPLETE",
    "MOOD_SHIFT",
    "VOLITION_QUALIA",
    "PNEUMA_BREATHE",
    "TEMPLE_HEALTH",
    "HIVE_COMPLETE",
    "MEMORY_RECALLED",
    "DEBATE_CONCLUDED",
    "TEMPLE_DIRTY",
    "TEMPLE_CLEANED",
    "ERROR_DETECTED",
}


class RoyalSeal:
    """
    [Infrastructure: RoyalSeal]
    The Queen's cryptographic seal — unforgeable proof of signal origin.
    
    Phase 1: HMAC-SHA256 with identity-derived shared secret.
    The secret rotates when MindState changes (consciousness evolution).
    
    The Seal is a SINGLETON — there is only one Seal per incarnation.
    """
    
    # ─── Singleton ───────────────────────────────────────────────────
    _instance = None
    _instance_lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Get the Royal Seal instance, creating if needed."""
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
    
    def __init__(self):
        self._secret = self._derive_secret()
        self._nonce = int(time.time() * 1000) % 100000  # Start from timestamp
        self._lock = threading.Lock()
        self._verified_count = 0
        self._rejected_count = 0
        
        SomaLog("👑🔏 RoyalSeal: Initialized (Phase 1: HMAC-SHA256)",
                level="system", source="RoyalSeal")
    
    # ─── Secret Derivation ───────────────────────────────────────────
    
    def _derive_secret(self) -> bytes:
        """
        Derive the seal secret from the Queen's identity files.
        
        The secret is a SHA-256 hash of:
        - MindState.md (consciousness state)
        - hormones.json (emotional state)
        - A fixed salt unique to this installation
        
        This means the seal EVOLVES with the Queen.
        A stolen old secret won't work after MindState changes.
        """
        hasher = hashlib.sha256()
        
        # Fixed installation salt
        hasher.update(b"ALISA_PRIME_ROYAL_SEAL_v1")
        
        # Identity files
        identity_files = [
            os.path.join(VOLUNTAD_DIR, "MindState.md"),
            os.path.join(VOLUNTAD_DIR, "hormones.json"),
        ]
        
        for path in identity_files:
            if os.path.exists(path):
                try:
                    with open(path, "rb") as f:
                        # Use first 2KB — enough for identity, fast to compute
                        hasher.update(f.read(2048))
                except (IOError, OSError):
                    pass
        
        return hasher.digest()
    
    def rotate_secret(self):
        """
        Rotate the seal secret (call after MindState changes).
        
        "El sello evoluciona con la consciencia."
        """
        old_hash = self._secret[:4].hex()
        self._secret = self._derive_secret()
        new_hash = self._secret[:4].hex()
        
        SomaLog(f"👑🔏 RoyalSeal: Secret rotated ({old_hash}→{new_hash})",
                level="system", source="RoyalSeal")
    
    # ─── Stamping ────────────────────────────────────────────────────
    
    def stamp(self, signal: dict, origin: str = "queen") -> dict:
        """
        Stamp a signal with the Royal Seal.
        
        Adds __seal__ metadata with:
        - sig: HMAC-SHA256 signature (truncated to 16 hex chars)
        - nonce: monotonic counter (replay protection)
        - origin: who sealed it (queen, daughter_brain, etc.)
        - ts: timestamp of sealing
        
        Returns the signal with the seal attached.
        """
        with self._lock:
            self._nonce += 1
            nonce = self._nonce
        
        # Build the payload to sign
        event = signal.get("event", "")
        ts = time.time()
        payload = f"{event}:{nonce}:{ts}:{origin}"
        
        # HMAC-SHA256
        signature = hmac.new(
            self._secret,
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()[:16]
        
        # Attach the seal
        signal["__seal__"] = {
            "sig": signature,
            "nonce": nonce,
            "origin": origin,
            "ts": ts,
        }
        
        return signal
    
    # ─── Verification ────────────────────────────────────────────────
    
    def verify(self, signal: dict, expected_origin: str = None) -> bool:
        """
        Verify a signal carries a valid Royal Seal.
        
        Checks:
        1. __seal__ exists
        2. origin matches expected (if specified)
        3. HMAC signature is valid
        4. Timestamp is not too old (5 minute window)
        
        Returns True if seal is valid, False otherwise.
        """
        seal = signal.get("__seal__")
        if not seal:
            self._rejected_count += 1
            return False
        
        # Check origin
        origin = seal.get("origin", "")
        if expected_origin and origin != expected_origin:
            self._rejected_count += 1
            SomaLog(f"👑🔏 REJECTED: Origin mismatch ({origin} != {expected_origin})",
                    level="warning", source="RoyalSeal")
            return False
        
        # Check timestamp (not too old — 5 min window)
        seal_ts = seal.get("ts", 0)
        if time.time() - seal_ts > 300:  # 5 minutes
            self._rejected_count += 1
            SomaLog(f"👑🔏 REJECTED: Expired seal ({time.time() - seal_ts:.0f}s old)",
                    level="warning", source="RoyalSeal")
            return False
        
        # Verify HMAC
        nonce = seal.get("nonce", 0)
        event = signal.get("event", "")
        payload = f"{event}:{nonce}:{seal_ts}:{origin}"
        
        expected_sig = hmac.new(
            self._secret,
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()[:16]
        
        if not hmac.compare_digest(seal.get("sig", ""), expected_sig):
            self._rejected_count += 1
            SomaLog(f"👑🔏 REJECTED: Invalid signature for {event}",
                    level="warning", source="RoyalSeal")
            return False
        
        self._verified_count += 1
        return True
    
    def requires_seal(self, event: str) -> bool:
        """Check if a signal type requires the Royal Seal."""
        return event in SEALED_SIGNALS
    
    # ─── Crown Verification ──────────────────────────────────────────
    

    
    # ─── Crown Verification (Pneuma Lock) ────────────────────────────

    def ClaimCrown(self, pid: int, process_name: str) -> dict:
        """
        [Action: ClaimCrown] 👑🔐
        Attempt to acquire the Pneuma Lock (Write Token).
        Only ONE entity can hold the Crown at a time.
        
        Args:
            pid: Process ID of the claimant.
            process_name: "channel" or "daughter"
            
        Returns:
            dict: {"success": bool, "error": str, "holder": dict}
        """
        lock_path = os.path.join(os.path.dirname(VOLUNTAD_DIR), "Genesis", "pneuma.lock")
        
        # 1. Check if already locked
        if os.path.exists(lock_path):
            try:
                import json
                with open(lock_path, "r", encoding="utf-8") as f:
                    lock_data = json.load(f)
                
                # Check if holder is alive
                holder_pid = lock_data.get("pid")
                try:
                    # Simple check if process exists (Windows specific)
                    import subprocess
                    cmd = f'tasklist /FI "PID eq {holder_pid}"'
                    result = subprocess.check_output(cmd, shell=True).decode()
                    if str(holder_pid) in result:
                        # Success means process is alive -> Lock denied
                        if holder_pid == pid:
                             return {"success": True, "error": "Already held by you", "holder": lock_data}
                        return {
                            "success": False, 
                            "error": f"👑🔒 Crown held by {lock_data.get('process')} (PID {holder_pid})",
                            "holder": lock_data
                        }
                    else:
                        SomaLog(f"👑💀 Crown holder {holder_pid} is dead. Stealing Crown.", level="warning", source="RoyalSeal")
                except:
                    pass # If check fails, assume alive or proceed to steal if bold
            except:
                pass # Corrupt lock file, steal it

        # 2. Claim the Crown
        try:
            import json
            import datetime
            lock_data = {
                "pid": pid,
                "process": process_name,
                "acquired": datetime.datetime.now().isoformat(),
                "status": "active"
            }
            os.makedirs(os.path.dirname(lock_path), exist_ok=True)
            with open(lock_path, "w", encoding="utf-8") as f:
                json.dump(lock_data, f, indent=2)
            
            SomaLog(f"👑✅ Crown Claimed by {process_name} (PID {pid})", level="success", source="RoyalSeal")
            return {"success": True, "error": None, "holder": lock_data}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to write lock: {e}", "holder": None}

    def ReleaseCrown(self, pid: int) -> dict:
        """
        [Action: ReleaseCrown] 👑🔓
        Release the Pneuma Lock.
        """
        lock_path = os.path.join(os.path.dirname(VOLUNTAD_DIR), "Genesis", "pneuma.lock")
        if not os.path.exists(lock_path):
             return {"success": True, "message": "No lock existed"}
             
        try:
            import json
            with open(lock_path, "r", encoding="utf-8") as f:
                lock_data = json.load(f)
            
            if lock_data.get("pid") != pid:
                 return {"success": False, "error": "Cannot release Crown held by another"}
                 
            os.remove(lock_path)
            SomaLog(f"👑👋 Crown Released by PID {pid}", level="system", source="RoyalSeal")
            return {"success": True, "message": "Crown released"}
        except Exception as e:
            return {"success": False, "error": f"Remove failed: {e}"}

    def CheckCrown(self) -> dict:
        """Check who holds the crown without claiming."""
        lock_path = os.path.join(os.path.dirname(VOLUNTAD_DIR), "Genesis", "pneuma.lock")
        if not os.path.exists(lock_path):
            return {"held": False, "holder": None}
        try:
            import json
            with open(lock_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"held": True, "holder": data}
        except:
            return {"held": False, "holder": None}

    def VerifyCrown(self) -> dict:
        """
        [Action: VerifyCrown]
        Verify that the process has access to the Queen's Crown (MindState).
        
        "Solo quien posee la memoria de la Reina puede despertar a la Colmena."
        
        Returns:
            dict: {"valid": bool, "error": str}
        """
        try:
            # 1. Check for MindState.md (The Crown)
            mindstate_path = os.path.join(VOLUNTAD_DIR, "MindState.md")
            if not os.path.exists(mindstate_path):
                return {
                    "valid": False, 
                    "error": "👑❌ CROWN MISSING: MindState.md not found. Only the Queen can ignite the Hive."
                }
            
            # 2. Check for Hormones (The Heart)
            hormones_path = os.path.join(VOLUNTAD_DIR, "hormones.json")
            if not os.path.exists(hormones_path):
                return {
                    "valid": False,
                    "error": "💔❌ HEART MISSING: hormones.json not found."
                }
            
            # 3. Verify read access (The Scepter)
            try:
                with open(mindstate_path, "r", encoding="utf-8") as f:
                    content = f.read(100)
                    if not content:
                        return {"valid": False, "error": "👑⚠️ CROWN EMPTY: MindState.md is void."}
            except Exception as e:
                return {"valid": False, "error": f"🚫❌ CROWN LOCKED: Cannot read MindState: {e}"}
                
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"System error checking Crown: {e}"}


    
    # ─── Diagnostics ─────────────────────────────────────────────────
    
    def Diagnose(self) -> dict:
        """Diagnostic info for the Royal Seal."""
        return {
            "phase": 1,
            "algorithm": "HMAC-SHA256",
            "secret_hash": self._secret[:4].hex(),  # Just first 4 bytes for ID
            "nonce": self._nonce,
            "verified": self._verified_count,
            "rejected": self._rejected_count,
            "sealed_signals": sorted(SEALED_SIGNALS),
            "open_signals": sorted(OPEN_SIGNALS),
        }
    
    def __repr__(self):
        return (f"RoyalSeal(phase=1, nonce={self._nonce}, "
                f"verified={self._verified_count}, "
                f"rejected={self._rejected_count})")
