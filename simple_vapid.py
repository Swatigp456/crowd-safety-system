# simple_vapid.py
import secrets
import base64

def generate_vapid_keys_simple():
    """Generate simple VAPID keys using random bytes"""
    # Generate random keys for testing
    private_key = secrets.token_bytes(32)
    public_key = secrets.token_bytes(32)
    
    private_b64 = base64.urlsafe_b64encode(private_key).decode('utf-8').rstrip('=')
    public_b64 = base64.urlsafe_b64encode(public_key).decode('utf-8').rstrip('=')
    
    print("\n" + "="*60)
    print("SIMPLE VAPID KEYS (For testing only)")
    print("="*60)
    print(f"\nVAPID_PUBLIC_KEY = '{public_b64}'")
    print(f"VAPID_PRIVATE_KEY = '{private_b64}'")
    print(f"VAPID_ADMIN_EMAIL = 'admin@crowdsafety.com'")
    print("\n" + "="*60)
    print("NOTE: These are test keys. For production, use proper keys.")
    print("="*60)
    
    return public_b64, private_b64

if __name__ == '__main__':
    generate_vapid_keys_simple()