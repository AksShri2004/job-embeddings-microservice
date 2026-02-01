import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from src.schemas import JobOutput
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "conductor_db")
COLLECTION_NAME = "jobs"

client = None
db = None

async def connect_to_mongo():
    global client, db
    print(f"Connecting to MongoDB at {MONGO_URI}...")
    client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    # Verify connection
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")

async def save_job(job_output: JobOutput):
    """
    Saves the processed job to MongoDB.
    Uses 'job_id' as the unique identifier for upsert operations.
    """
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    
    collection = db[COLLECTION_NAME]
    
    # Convert Pydantic model to dict
    document = job_output.model_dump()
    
    # Use job_id as the filter for upsert
    result = await collection.update_one(
        {"job_id": job_output.job_id},
        {"$set": document},
        upsert=True
    )
    
    return result
