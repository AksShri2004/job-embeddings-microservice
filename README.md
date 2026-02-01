# Job Embedding Microservice (Conductor)

This microservice is designed to power AI-driven job search and matching applications. It accepts raw job postings, normalizes the data into a standard format, generates high-quality vector embeddings using the **BAAI/bge-small-en-v1.5** model, and automatically stores the results in a MongoDB database.

## 🚀 Capabilities

*   **Normalization:** Cleans and standardizes job titles, skills, and descriptions from various formats (e.g., LinkedIn, Naukri).
*   **Vector Embeddings:** Converts text into 384-dimensional vectors, enabling semantic search and similarity matching.
*   **Database Sync:** Automatically saves or updates processed job records in your MongoDB cluster.
*   **Secure Access:** Protected by API Key authentication.

## 🔌 How to Use the API

The service exposes a secure REST endpoint to process job data.

### **Endpoint**
`POST /process`

### **Authentication**
You must include your secret API key in the `X-API-Key` header for every request.

### **Example Request**

You can send a job object with any common field names (e.g., `title`, `job_title`, `skills`, `description`). The service automatically maps them.

```bash
curl -X POST "https://your-service-url.onrender.com/process" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_SECRET_API_KEY>" \
  -d '{
    "job_id": "job-101",
    "title": "Senior Backend Engineer",
    "company_name": "FutureTech",
    "location": "Remote",
    "description": "We need an expert in Python, FastAPI, and Vector Databases to build scalable microservices.",
    "skills_desc": "Python, MongoDB, Docker, Kubernetes"
  }'
```

### **Response**

The service returns the normalized job data along with the generated vector embeddings.

```json
{
  "job_id": "job-101",
  "cleaned_job": {
    "title": "Senior Backend Engineer",
    "company": "FutureTech",
    "location": "Remote",
    "sections": {
      "required_skills": ["Python, MongoDB, Docker, Kubernetes"],
      "description": "We need an expert in Python, FastAPI, and Vector Databases to build scalable microservices."
    }
  },
  "metadata": {
    "embedding_model": "BAAI/bge-small-en-v1.5",
    "embedding_ready": true
  }
}
```
