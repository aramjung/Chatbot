# OneNote Document Processing Pipeline

This folder contains scripts to process OneNote notebooks and prepare them for RAG (Retrieval Augmented Generation) integration with your chatbot.

## 📁 Folder Structure

```
onenote/
├── raw/                    # Place your exported .docx files here
├── processed/              # Extracted and structured text (JSON)
├── embeddings/             # Generated embeddings ready for vector DB
└── scripts/                # Processing scripts
    ├── import_docs.py      # Extract text from .docx files
    ├── chunk_text.py       # Split text into chunks
    ├── generate_embeddings.py  # Create embeddings
    └── run_pipeline.py     # Run the full pipeline
```

## 🚀 Quick Start

### 1. Export Your OneNote Data

1. Open OneNote
2. Select a notebook/section
3. **File → Export → Word Document (.docx)**
4. Save the .docx files to `onenote/raw/`

### 2. Install Dependencies

```powershell
cd onenote/scripts
pip install python-docx
```

(OpenAI and other dependencies are already installed from the main project)

### 3. Run the Pipeline

```powershell
cd onenote/scripts
python run_pipeline.py
```

This will:

- ✅ Extract text from all .docx files in `raw/`
- ✅ Chunk the text into ~500-word pieces with 50-word overlap
- ✅ Generate embeddings using OpenAI's `text-embedding-3-small` model
- ✅ Store embeddings in Chroma vector database
- ✅ Save JSON backups for reference

## 📝 Individual Steps

You can also run steps individually:

```powershell
# Import documents only
python run_pipeline.py import

# Chunk documents only
python run_pipeline.py chunk

# Generate embeddings only
python run_pipeline.py embed
```

## ⚙️ Configuration

### Chunk Size

Edit `chunk_text.py` or pass parameters:

```python
chunker = TextChunker(
    chunk_size=500,  # Words per chunk
    overlap=50       # Overlapping words between chunks
)
```

### Embedding Model

Edit `generate_embeddings.py`:

```python
generator = EmbeddingGenerator(
    model='text-embedding-3-small'  # or 'text-embedding-3-large'
)
```

**Models:**

- `text-embedding-3-small`: Faster, cheaper, 1536 dimensions
- `text-embedding-3-large`: Higher quality, 3072 dimensions

## 📊 Output Format

### Processed Documents (`processed/*.json`)

```json
{
  "source_file": "My Notes.docx",
  "processed_date": "2025-12-22T10:30:00",
  "num_sections": 5,
  "sections": [
    {
      "heading": "Project Ideas",
      "level": 1,
      "text": "Content of the section..."
    }
  ]
}
```

### Chunks (`processed/*_chunks.json`)

```json
{
  "source_document": "My Notes.docx",
  "chunk_size": 500,
  "overlap": 50,
  "total_chunks": 12,
  "chunks": [
    {
      "text": "Chunk content...",
      "word_count": 487,
      "chunk_num": 0,
      "heading": "Project Ideas",
      "heading_level": 1
    }
  ]
}
```

### Embeddings (`embeddings/*_embeddings.json`)

```json
{
  "source_document": "My Notes.docx",
  "embedding_model": "text-embedding-3-small",
  "total_chunks": 12,
  "generated_date": "2025-12-22T10:35:00",
  "chunks": [
    {
      "text": "Chunk content...",
      "embedding": [0.123, -0.456, ...],  // 1536 dimensions
      "heading": "Project Ideas"
    }
  ]
}
```

## �️ Chroma Vector Database

The pipeline automatically stores embeddings in Chroma, a local vector database perfect for RAG applications.

### Database Location

Chroma database is stored at: `Chatbot/chroma_db/`

### Working with Chroma

**Check database stats:**

```powershell
cd onenote/scripts
python load_to_chroma.py stats
```

**Load existing embeddings** (if you already have JSON files):

```powershell
python load_to_chroma.py
```

**Query the database** (from your backend code):

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="onenote_chunks")

# Search for similar chunks
results = collection.query(
    query_embeddings=[question_embedding],
    n_results=5
)
```

## 🔄 Next Steps: Integrate with Chatbot

Now that embeddings are in Chroma, you can enhance your chatbot:

1. **Choose a vector database:**

   - Chroma (local, simple)
   - Pinecone (cloud, scalable)
   - Weaviate (self-hosted, feature-rich)

2. **Load embeddings into the database**

3. **Modify your chatbot backend** to:
   - Generate embedding for user's question
   - Search vector DB for similar chunks
   - Include relevant chunks in OpenAI prompt
   - Return contextual answer

## 💡 Tips

- **Document structure**: The pipeline preserves headings and sections, which helps with context during retrieval
- **Chunk size**: 500 words is a good balance. Too small = loss of context. Too large = less precise retrieval
- **Overlap**: Ensures important information at chunk boundaries isn't lost
- **Cost**: Embeddings cost ~$0.02 per 1M tokens. A typical document might cost $0.001-0.01

## 🐛 Troubleshooting

**No .docx files found:**

- Make sure files are in `onenote/raw/`
- Check file extension is `.docx` (not `.doc`)

**OpenAI API error:**

- Verify your API key in `.env` file
- Check you have credits in your OpenAI account

**Import errors:**

- Run: `pip install python-docx` from the scripts folder

## 📚 Learn More

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Chunking Strategies](https://www.pinecone.io/learn/chunking-strategies/)
