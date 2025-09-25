# core/init_db.py

from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    engine: Optional[AIOEngine] = None

database = Database()

async def connect_to_mongo():
    """Create database connection"""
    username = quote_plus("backend_user")
    password = quote_plus("Ecell@2025") 

    # Build MongoDB URL
    mongodb_url = f"mongodb+srv://{username}:{password}@cluster0.blyrgyf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    database_name = "Rec_Backend"

    # Create Motor client
    database.client = AsyncIOMotorClient(mongodb_url)

    # Create ODMantic engine
    database.engine = AIOEngine(database=database_name, client=database.client)
    # engine = AIOEngine(database=database_name, client=database.client)


    print(f"Connected to MongoDB: {mongodb_url}")

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        print("Disconnected from MongoDB")

def get_database() -> AIOEngine:
    """Get ODMantic engine instance"""
    if database.engine is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return database.engine

# Optional: simple function-based approach
def get_engine() -> AIOEngine:
    """Get ODMantic engine - simpler approach"""
    from urllib.parse import quote_plus
    from motor.motor_asyncio import AsyncIOMotorClient
    from odmantic import AIOEngine

    username = quote_plus("backend_user")
    password = quote_plus("Ecell@2025")
    mongodb_url = f"mongodb+srv://{username}:{password}@cluster0.blyrgyf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    database_name = "Rec_Backend"

    client = AsyncIOMotorClient(mongodb_url)
    engine = AIOEngine(client, database=database_name) 
    return engine
