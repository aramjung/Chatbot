# AI Chatbot Application

A modern chatbot application with a React frontend and FastAPI backend, powered by OpenAI's GPT models.

## Features

- 🤖 Real-time chat interface with OpenAI integration
- 💬 Maintains conversation context across messages
- 🎨 Modern, responsive UI with gradient design
- 🔄 Loading indicators and smooth animations
- 📱 Mobile-friendly responsive design
- 🧹 Clear chat functionality
- ⚡ Async FastAPI backend for optimal performance
- 📚 Automatic API documentation at /docs

## Project Structure

```
Chatbot/
├── backend/
│   ├── app.py              # FastAPI server with async support
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # Styling
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Global styles
│   └── package.json        # Node dependencies
└── .env.example           # Environment variables template
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create and activate a virtual environment (if not already activated):

   ```bash
   # Windows
   ..\myenv\Scripts\activate

   # macOS/Linux
   source ../myenv/bin/activate
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory:

   ```bash
   # Copy from .env.example
   cp ../.env.example ../.env
   ```

5. Edit `.env` and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

6. Run the FastAPI backend:

   ```bash
   python app.py
   ```

   Or use uvicorn directly:

   ```bash
   uvicorn app:app --reload --port 5000
   ```

   The backend will start on `http://localhost:5000`

   📚 **API Documentation**: Visit `http://localhost:5000/docs` for interactive API docs!

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:

   ```bash
   npm install
   ```

3. Start the React development server:

   ```bash
   npm start
   ```

   The frontend will start on `http://localhost:3000`

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Type your message in the input field at the bottom
3. Press Enter or click the "Send" button
4. The AI will respond with context from your conversation history
5. Use "Clear Chat" button to start a new conversation

## API Endpoints

### POST /api/chat

Send a message to the chatbot and receive a response.

**Request Body:**

```json
{
  "messages": [
    { "role": "user", "content": "Hello!" },
    { "role": "assistant", "content": "Hi! How can I help you?" },
    { "role": "user", "content": "Tell me about AI" }
  ]
}
```

**Response:**

```json
{
  "message": "AI stands for Artificial Intelligence...",
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 100,
    "total_tokens": 150
  }
}
```

### GET /api/health

Check if the backend is running.

**Response:**

```json
{
  "status": "healthy"
}
```

## Configuration

### OpenAI Model

By default, the app uses `gpt-4o-mini`. You can change this in [backend/app.py](backend/app.py#L58):

```python
model="gpt-4o-mini",  # Change to "gpt-4", "gpt-3.5-turbo", etc.
```

### Temperature & Token Limits

Adjust these parameters in [backend/app.py](backend/app.py#L59-L60):

```python
temperature=0.7,      # Controls randomness (0.0-2.0)
max_tokens=1000       # Maximum response length
```

## Future Enhancements (RAG Capability)

The next phase will add:

- Vector database integration (e.g., Pinecone, Weaviate, or Chroma)
- Document ingestion and chunking
- Embedding generation and storage
- Semantic search for relevant context
- Enhanced prompts combining chat history + retrieved documents

## Troubleshooting

### Backend Issues

- **ImportError**: Make sure all dependencies are installed with `pip install -r requirements.txt`
- **OpenAI API Error**: Verify your API key is correct in the `.env` file
- **Port 5000 in use**: Change the port in `app.py`: `uvicorn.run(app, host="0.0.0.0", port=5001)`

### Frontend Issues

- **Cannot connect to backend**: Ensure the FastAPI backend is running on port 5000
- **Module not found**: Run `npm install` in the frontend directory
- **Port 3000 in use**: React will prompt you to use a different port

## License

MIT License - Feel free to use this project for learning or commercial purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
