from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import chromadb
from pathlib import Path

load_dotenv()

app = FastAPI(title="AI Chatbot API", version="1.0.0")

# Configure CORS - prevent API calls from unauthorized origins.  This is a browser security feature.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "http://localhost",        # Docker frontend
        "http://localhost:80"      # Docker frontend explicit port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI async client
client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Chroma client
chroma_db_path = Path(__file__).parent.parent / 'chroma_db'
chroma_client = chromadb.PersistentClient(path=str(chroma_db_path))
try:
    chroma_collection = chroma_client.get_collection(name="onenote_chunks")
except:
    # Collection doesn't exist yet - that's okay
    chroma_collection = None

# Pydantic models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class UsageInfo(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponse(BaseModel):
    message: str
    usage: UsageInfo

class ContextChunk(BaseModel):
    text: str
    source_file: str
    heading: str

class RagChatResponse(BaseModel):
    message: str
    usage: UsageInfo
    context_chunks: List[ContextChunk]

class HealthResponse(BaseModel):
    status: str

@app.post('/api/chat', response_model=RagChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with RAG (Retrieval-Augmented Generation).
    Queries Chroma for relevant context when available, otherwise falls back to standard chat.
    """
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail='No messages provided')
        
        context_chunks = []
        context_text = ""
        
        # Try to retrieve context from Chroma if available
        if chroma_collection:
            # Get the last user message as the query
            user_message = next(
                (msg.content for msg in reversed(request.messages) if msg.role == 'user'),
                None
            )
            
            if user_message:
                try:
                    # Generate embedding for the user's question
                    embedding_response = await client.embeddings.create(
                        model="text-embedding-3-small",
                        input=user_message
                    )
                    question_embedding = embedding_response.data[0].embedding
                    
                    # Query Chroma for similar chunks
                    results = chroma_collection.query(
                        query_embeddings=[question_embedding],
                        n_results=5
                    )
                    
                    # Extract context chunks
                    if results['documents'] and results['documents'][0]:
                        for i, doc in enumerate(results['documents'][0]):
                            metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                            context_chunks.append(ContextChunk(
                                text=doc,
                                source_file=metadata.get('source_file', 'Unknown'),
                                heading=metadata.get('heading', 'No heading')
                            ))
                            context_text += f"\n\n--- Context {i+1} ---\n{doc}"
                except Exception as e:
                    # If retrieval fails, continue without context
                    print(f"Context retrieval failed: {str(e)}")
        
        # Build messages with injected context if available
        messages_dict = [msg.model_dump() for msg in request.messages]
        
        if context_text:
            # Inject context into system message
            system_message = {
                'role': 'system',
                'content': f"""You are a helpful AI assistant with access to the user's personal knowledge base.

Use the following context from their documents to answer questions. If the context doesn't contain relevant information, say so and answer based on your general knowledge.

Context from user's documents:{context_text}

Provide clear, helpful answers based on this context when relevant."""
            }
            messages_dict.insert(0, system_message)
        
        # Call OpenAI API
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_dict,
            temperature=0.7,
            max_tokens=1500
        )
        
        assistant_message = response.choices[0].message.content
        
        return RagChatResponse(
            message=assistant_message,
            usage=UsageInfo(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            ),
            context_chunks=context_chunks
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get('/api/health', response_model=HealthResponse)
async def health():
    return HealthResponse(status='healthy')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
