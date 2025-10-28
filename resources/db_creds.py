import os
from dotenv import load_dotenv

load_dotenv()

class DataBaseCreds:
    HOSTDB = os.getenv('HOSTDB')
    PORTDB = os.getenv('PORTDB')
    NAMEDB = os.getenv('NAMEDB')
    USERNAMEDB = os.getenv('USERDB')
    PASSWORDDB = os.getenv('PASSWORDDB')
