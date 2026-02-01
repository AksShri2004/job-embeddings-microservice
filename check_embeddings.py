import asyncio
import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "conductor_db")

async def check_embeddings():
    print(f"Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    collection = db["jobs"]
    
    # Check a few random documents for embeddings
    cursor = collection.find({}, {"job_id": 1, "embeddings": 1}).limit(5)
    docs = await cursor.to_list(length=5)
    
    print(f"\nChecking 5 sample records for embeddings:")
    for doc in docs:
        job_id = doc.get("job_id")
        embs = doc.get("embeddings", {})
        
        # Check if any major section has a vector
        has_vectors = False
        for section in ["title", "description", "required_skills"]:
            section_data = embs.get(section)
            if isinstance(section_data, dict) and isinstance(section_data.get("vector"), list):
                has_vectors = True
                break
        
        status = "✅ DONE" if has_vectors else "❌ MISSING"
        print(f"- Job {job_id}: {status}")
        
    # Count how many have 'embedding_ready': true in metadata
    ready_count = await collection.count_documents({"metadata.embedding_ready": True})
    total_count = await collection.count_documents({})
    
    print(f"\nSummary:")
    print(f"Total jobs: {total_count}")
    print(f"Jobs with embeddings ready: {ready_count}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_embeddings())