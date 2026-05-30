import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import create_tables

if __name__ == "__main__":
    print("Creating tables...")
    create_tables()