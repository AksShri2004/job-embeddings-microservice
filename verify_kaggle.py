import json
from src.normalizer import normalize_job
from src.embedder import generate_embeddings, get_metadata
from src.schemas import JobOutput

# Sample data mimicking the exact Kaggle 'job_postings.csv' schema you provided
kaggle_samples = [
    {
        "job_id": "3757934318",
        "title": "Senior Machine Learning Engineer",
        "company_name": "Anthropic",
        "location": "San Francisco, CA",
        "description": "We are building safe AI systems. You will work on RLHF and language model training.",
        "formatted_work_type": "Full-time",
        "formatted_experience_level": "Mid-Senior level",
        "skills_desc": "Python, PyTorch, Kubernetes, Distributed Systems",
        "max_salary": 350000,
        "pay_period": "Yearly"
    },
    {
        "job_id": "999999999",
        "title": "React Frontend Developer",
        "company_name": "Netflix",
        "location": "Remote",
        "description": "Building the next generation of TV UIs. Must have deep experience with React performance.",
        "formatted_work_type": "Contract",
        "formatted_experience_level": "Associate",
        "skills_desc": "JavaScript, TypeScript, React, CSS",
        "views": 1500
    }
]

def verify_kaggle():
    print(f"Testing with {len(kaggle_samples)} Kaggle-schema samples...\n")
    
    for i, raw_data in enumerate(kaggle_samples):
        print(f"--- Sample {i+1}: {raw_data['title']} ---")
        
        # 1. Normalize
        # matches formatted_work_type -> employment_type
        # matches formatted_experience_level -> experience_required
        # matches skills_desc -> required_skills
        canonical_job = normalize_job(raw_data, raw_data["job_id"])
        
        print(f"Mapped 'formatted_work_type' -> Employment Type: '{canonical_job.job_data.employment_type}'")
        print(f"Mapped 'formatted_experience_level' -> Experience: '{canonical_job.job_data.experience_required}'")
        print(f"Mapped 'skills_desc' -> Skills: {canonical_job.job_data.sections.required_skills}")
        
        # 2. Embed
        print("Generating embeddings...")
        embeddings = generate_embeddings(canonical_job.job_data)
        
        # 3. Metadata
        metadata = get_metadata(embeddings)
        
        # Output Object
        output = JobOutput(
            job_id=canonical_job.job_id,
            cleaned_job=canonical_job.job_data,
            embeddings=embeddings,
            metadata=metadata
        )
        
        # Check result
        if output.metadata.embedding_ready:
            print("SUCCESS: Embeddings generated.")
            if output.embeddings.description.vector:
                print(f"Description vector dimension: {len(output.embeddings.description.vector)}")
            if output.embeddings.required_skills.vector:
                print(f"Skills vector dimension: {len(output.embeddings.required_skills.vector)}")
        else:
            print("FAILURE: Embedding not ready.")
        print("\n" + "="*30 + "\n")

if __name__ == "__main__":
    verify_kaggle()