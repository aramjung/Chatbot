# Docker Deployment Guide

## Build Images

### Backend API

```bash
docker build -f backend/Dockerfile -t chatbot-api:latest .
```

### Frontend

```bash
docker build -f frontend/Dockerfile -t chatbot-frontend:latest .
```

## Run Locally with Docker Compose

```bash
# Make sure .env file has OPENAI_API_KEY
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Deploy to Cloud

### AWS ECR + ECS

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Tag and push backend
docker tag chatbot-api:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/chatbot-api:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/chatbot-api:latest

# Tag and push frontend
docker tag chatbot-frontend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/chatbot-frontend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/chatbot-frontend:latest
```

### Google Cloud Run

```bash
# Backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT/chatbot-api backend/
gcloud run deploy chatbot-api --image gcr.io/YOUR_PROJECT/chatbot-api --platform managed

# Frontend
gcloud builds submit --tag gcr.io/YOUR_PROJECT/chatbot-frontend frontend/
gcloud run deploy chatbot-frontend --image gcr.io/YOUR_PROJECT/chatbot-frontend --platform managed
```

### Azure Container Instances

```bash
# Create container registry
az acr create --resource-group myResourceGroup --name chatbotregistry --sku Basic

# Build and push
az acr build --registry chatbotregistry --image chatbot-api:latest backend/
az acr build --registry chatbotregistry --image chatbot-frontend:latest frontend/

# Deploy
az container create --resource-group myResourceGroup --name chatbot-api \
  --image chatbotregistry.azurecr.io/chatbot-api:latest --ports 5000
```

## Environment Variables

### Backend

- `OPENAI_API_KEY` - Your OpenAI API key (required)

### Frontend (build-time)

Update `.env.production` before building:

```
REACT_APP_API_URL=https://your-api-domain.com
```

## Important Notes

1. **Update CORS**: In `backend/app.py`, update allowed origins:

   ```python
   allow_origins=["https://your-frontend-domain.com"]
   ```

2. **Chroma DB Volume**: Mount persistent volume for vector database:

   ```bash
   -v /path/to/chroma_db:/app/chroma_db
   ```

3. **HTTPS**: Use reverse proxy (nginx, Cloudflare, load balancer) for SSL termination
