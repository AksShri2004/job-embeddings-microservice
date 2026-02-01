import asyncio
import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "conductor_db")

async def verify_record():
    print(f"Connecting to {MONGO_URI}...")
    client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    collection = db["jobs"]
    
    # Count documents
    count = await collection.count_documents({})
    print(f"Total documents in 'jobs' collection: {count}")
    
    # Find the curl-test record
    doc = await collection.find_one({"job_id": "curl-test-001"})
    if doc:
        print("SUCCESS: Found 'curl-test-001' in MongoDB.")
        print(f"Job Title stored: {doc['cleaned_job']['title']}")
    else:
        print("FAILURE: 'curl-test-001' not found in MongoDB.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verify_record())
