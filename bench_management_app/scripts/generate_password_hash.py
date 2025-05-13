"""
Utility script to generate bcrypt password hashes for sample data
"""
from passlib.context import CryptContext
import sys

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    """Hash a password for storing"""
    return pwd_context.hash(password)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = "password123"  # Default password
    
    hashed_password = get_password_hash(password)
    print(f"Password: {password}")
    print(f"Hashed: {hashed_password}")
    print(f"SQL-ready: '{hashed_password}'")