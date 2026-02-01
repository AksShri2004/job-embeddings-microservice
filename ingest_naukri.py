import asyncio
import csv
import sys
import os
from src.normalizer import normalize_job
from src.embedder import generate_embeddings, get_metadata
from src.schemas import JobOutput
from src.database import connect_to_mongo, save_job, close_mongo_connection

CSV_FILE = "naukri_com-job_sample.csv"

async def ingest():
    if not os.path.exists(CSV_FILE):
        print(f"Error: File '{CSV_FILE}' not found.")
        print(f"Please download the dataset from Kaggle and place it in: {os.getcwd()}/{CSV_FILE}")
        return

    print(f"Starting ingestion from {CSV_FILE}...")
    
    # Connect to DB
    await connect_to_mongo()
    
    count = 0
    success = 0
    
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if success >= 2000:
                    print("Reached limit of 2000 jobs. Stopping ingestion.")
                    break
                
                count += 1
                try:
                    # Use unique ID from CSV if available (handled in normalize_job via 'Uniq Id')
                    # We pass a placeholder UUID, but normalize_job will overwrite it if 'Uniq Id' exists
                    temp_id = f"naukri-{count}"
                    
                    # 1. Normalize
                    canonical_job = normalize_job(row, temp_id)
                    
                    # Skip if no title (junk data)
                    if not canonical_job.job_data.title:
                        print(f"Skipping row {count}: No Job Title found.")
                        continue
                        
                    # 2. Embed
                    embeddings = generate_embeddings(canonical_job.job_data)
                    
                    # 3. Metadata
                    metadata = get_metadata(embeddings)
                    
                    job_output = JobOutput(
                        job_id=canonical_job.job_id,
                        cleaned_job=canonical_job.job_data,
                        embeddings=embeddings,
                        metadata=metadata
                    )
                    
                    # 4. Save
                    await save_job(job_output)
                    success += 1
                    
                    if count % 10 == 0:
                        print(f"Processed {count} jobs... (Saved: {success})")
                        
                except Exception as e:
                    print(f"Error processing row {count}: {e}")
                    
    finally:
        await close_mongo_connection()

    print(f"\nIngestion Complete!")
    print(f"Total processed: {count}")
    print(f"Successfully saved: {success}")

if __name__ == "__main__":
    asyncio.run(ingest())
