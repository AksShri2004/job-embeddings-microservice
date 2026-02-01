import sys
from src.normalizer import normalize_job
from src.embedder import generate_embeddings, get_metadata
from src.schemas import JobOutput
import json

def verify():
    raw_input = {
        "id": "test-101",
        "Job Title": "  Senior Python Developer  ",
        "Company": "  AI Innovations Inc. ",
        "Location": "Remote",
        "Skills": "Python\nFastAPI\nPydantic\nVector Databases",
        "Responsibilities": "- Build microservices\n- Optimize embeddings",
        "Description": "We are looking for an expert."
    }
    
    print("--- Raw Input ---")
    print(json.dumps(raw_input, indent=2))
    
    print("\n--- Processing ---")
    # 1. Normalize
    print("Normalizing...")
    canonical_job = normalize_job(raw_input, raw_input["id"])
    print(f"Cleaned Title: '{canonical_job.job_data.title}'")
    print(f"Cleaned Skills: {canonical_job.job_data.sections.required_skills}")
    
    # 2. Embed
    print("Generating Embeddings (this may take a moment to load the model)...")
    embeddings = generate_embeddings(canonical_job.job_data)
    
    # Check vectors
    if embeddings.title.vector:
        print(f"Title Vector Dimension: {len(embeddings.title.vector)}")
    else:
        print("Error: Title vector missing")
        
    if embeddings.required_skills.vector:
        print(f"Skills Vector Dimension: {len(embeddings.required_skills.vector)}")
        
    # 3. Metadata
    metadata = get_metadata(embeddings)
    
    # Final Output
    output = JobOutput(
        job_id=canonical_job.job_id,
        cleaned_job=canonical_job.job_data,
        embeddings=embeddings,
        metadata=metadata
    )
    
    print("\n--- Final Output Metadata ---")
    print(output.metadata.model_dump_json(indent=2))
    
    print("\nSUCCESS: Pipeline verified.")

if __name__ == "__main__":
    verify()
