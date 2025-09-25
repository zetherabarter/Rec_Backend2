from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://backend_user:<db_password>@cluster0.blyrgyf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" 
MONGO_DB = "fastapi_db"

# Create client
client = AsyncIOMotorClient(MONGO_URI)

# Create engine
engine = AIOEngine(client=client, database=MONGO_DB)
