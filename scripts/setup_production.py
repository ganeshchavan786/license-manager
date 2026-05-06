"""
Production Setup Script
Run: python scripts/setup_production.py

हे script:
1. Encryption key generate करतो
2. Secret key generate करतो
3. Admin account create करतो
4. Database migrations run करतो
"""

import os
import sys
import secrets
import string

def generate_secret_key(length=64):
    """Cryptographically secure random key generate करतो"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_fernet_key():
    """Fernet encryption key generate करतो"""
    from cryptography.fernet import Fernet
    return Fernet.generate_key().decode()


def create_admin_account():
    """Admin account create करतो"""
    print("\n=== Admin Account Setup ===")
    username = input("Admin username (default: admin): ").strip() or "admin"
    full_name = input("Admin full name: ").strip() or "Administrator"
    
    import getpass
    password = getpass.getpass("Admin password (min 8 chars): ")
    if len(password) < 8:
        print("❌ Password too short!")
        return False
    
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("❌ Passwords don't match!")
        return False
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.database import SessionLocal, create_tables
        from app.models import AdminUser
        from app.services.auth import hash_password
        
        create_tables()
        db = SessionLocal()
        
        # Check if admin already exists
        existing = db.query(AdminUser).filter(AdminUser.username == username).first()
        if existing:
            print(f"⚠️  Admin '{username}' already exists!")
            db.close()
            return True
        
        admin = AdminUser(
            full_name=full_name,
            username=username,
            password_hash=hash_password(password),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.close()
        
        print(f"✅ Admin account created: {username}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create admin: {str(e)}")
        return False


def run_migrations():
    """Database migrations run करतो"""
    print("\n=== Database Migrations ===")
    result = os.system("alembic upgrade head")
    if result == 0:
        print("✅ Migrations completed successfully")
        return True
    else:
        print("❌ Migration failed!")
        return False


def generate_env_keys():
    """Production .env keys generate करतो"""
    print("\n=== Generating Production Keys ===")
    
    secret_key = generate_secret_key(64)
    license_key = generate_secret_key(32)
    
    try:
        fernet_key = generate_fernet_key()
    except ImportError:
        fernet_key = generate_secret_key(44)
        print("⚠️  cryptography not installed, using random key for ENCRYPTION_KEY")
    
    internal_key = generate_secret_key(32)
    
    print("\n📋 Add these to your .env file:")
    print("=" * 60)
    print(f"SECRET_KEY={secret_key}")
    print(f"LICENSE_ENCRYPTION_KEY={license_key}")
    print(f"ENCRYPTION_KEY={fernet_key}")
    print(f"INTERNAL_API_KEY={internal_key}")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: Save these keys securely!")
    print("⚠️  LICENSE_ENCRYPTION_KEY कधीही change करू नका!")
    
    return {
        "SECRET_KEY": secret_key,
        "LICENSE_ENCRYPTION_KEY": license_key,
        "ENCRYPTION_KEY": fernet_key,
        "INTERNAL_API_KEY": internal_key
    }


def check_env_file():
    """Check if .env file exists and has required keys"""
    print("\n=== Environment Check ===")
    
    required_keys = [
        "SECRET_KEY",
        "LICENSE_ENCRYPTION_KEY",
        "DATABASE_URL",
        "RAZORPAY_KEY_ID",
        "RAZORPAY_KEY_SECRET",
    ]
    
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("   Run: copy .env.example .env")
        return False
    
    with open(".env") as f:
        content = f.read()
    
    missing = []
    for key in required_keys:
        if key not in content or f"{key}=change-this" in content or f"{key}=your" in content:
            missing.append(key)
    
    if missing:
        print(f"⚠️  These keys need to be updated in .env:")
        for key in missing:
            print(f"   - {key}")
        return False
    
    print("✅ Environment file looks good")
    return True


def main():
    print("=" * 60)
    print("SalaryPay License Server - Production Setup")
    print("=" * 60)
    
    print("\nWhat would you like to do?")
    print("1. Generate production keys")
    print("2. Run database migrations")
    print("3. Create admin account")
    print("4. Check environment")
    print("5. Full setup (all of the above)")
    print("6. Exit")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        generate_env_keys()
    elif choice == "2":
        run_migrations()
    elif choice == "3":
        create_admin_account()
    elif choice == "4":
        check_env_file()
    elif choice == "5":
        print("\n🚀 Starting full production setup...")
        generate_env_keys()
        input("\nPress Enter after updating .env file...")
        check_env_file()
        run_migrations()
        create_admin_account()
        print("\n✅ Production setup complete!")
        print("\nStart server:")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8661")
    elif choice == "6":
        print("Bye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
