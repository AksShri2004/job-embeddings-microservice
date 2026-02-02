import asyncio
from src.database import db, COLLECTION_NAME
from src.normalizer import normalize_job
from src.embedder import generate_embeddings, get_metadata

async def watch_and_embed():
    """
    Background task that polls the database for jobs without embeddings.
    It generates embeddings and updates the document in place.
    """
    print("Starting Background Watcher (Polling Mode)...")
    
    while True:
        try:
            # Wait for DB connection
            if db is None:
                await asyncio.sleep(2)
                continue

            collection = db[COLLECTION_NAME]
            
            # CRITICAL: Find jobs where embedding is NOT ready.
            # This handles new inserts AND ensures we don't re-process finished jobs.
            cursor = collection.find(
                {"metadata.embedding_ready": {"$ne": True}}
            ).limit(10)  # Process in small batches
            
            processed_count = 0
            
            async for raw_doc in cursor:
                try:
                    # Fallback for ID
                    job_id = raw_doc.get("job_id")
                    if not job_id:
                        job_id = str(raw_doc.get("_id"))

                    # 1. Normalize
                    # We map your app's raw fields to our canonical schema
                    canonical_job = normalize_job(raw_doc, job_id)
                    
                    # 2. Embed
                    embeddings = generate_embeddings(canonical_job.job_data)
                    
                    # 3. Metadata
                    metadata = get_metadata(embeddings)
                    
                    # 4. Update In-Place
                    # We add 'embeddings', 'metadata', and 'cleaned_job' fields.
                    # We preserve all other original fields in the document.
                    update_payload = {
                        "embeddings": embeddings.model_dump(),
                        "metadata": metadata.model_dump(),
                        "cleaned_job": canonical_job.job_data.model_dump()
                    }
                    
                    # Only if we successfully generated embeddings do we set them
                    await collection.update_one(
                        {"_id": raw_doc["_id"]},
                        {"$set": update_payload}
                    )
                    
                    processed_count += 1
                    print(f"✅ [Watcher] Embedded Job ID: {job_id}")

                except Exception as inner_e:
                    print(f"⚠️ [Watcher] Failed to process job {raw_doc.get('_id')}: {inner_e}")
            
            if processed_count == 0:
                # If no work found, sleep longer (5 seconds)
                await asyncio.sleep(5)
            else:
                # If we did work, sleep briefly (1 second) to process queue faster
                await asyncio.sleep(1)

        except Exception as e:
            print(f"❌ [Watcher] Error: {e}")
            await asyncio.sleep(10)
