from app.models.user_model import pwd_context
import sys

def verify_argon2():
    # 1. Test long password (> 72 bytes)
    long_password = "x" * 100
    try:
        hashed = pwd_context.hash(long_password)
        print(f"Successfully hashed long password (len={len(long_password)})")
        print(f"Hash prefix: {hashed[:10]}")
    except Exception as e:
        print(f"Failed to hash long password: {e}")
        return False

    # 2. Verify hash type
    if not hashed.startswith("$argon2"):
        print(f"Error: Hash does not start with $argon2. Hash: {hashed}")
        return False
    
    # 3. Verify validation
    if not pwd_context.verify(long_password, hashed):
        print("Error: Failed to verify password against hash")
        return False
        
    print("Verification SUCCESS: Argon2 is working and handling long passwords.")
    return True

if __name__ == "__main__":
    success = verify_argon2()
    sys.exit(0 if success else 1)
