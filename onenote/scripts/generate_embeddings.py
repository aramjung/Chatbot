"""
Embedding Generation Script
Generates embeddings for text chunks using OpenAI's embedding model.
Also stores embeddings in Chroma vector database.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv
from datetime import datetime
import chromadb

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / '.env')

class EmbeddingGenerator:
    def __init__(self, 
                 processed_folder='../processed',
                 embeddings_folder='../embeddings',
                 chroma_db_path='../../chroma_db',
                 model='text-embedding-3-small'):
        """
        Initialize the embedding generator.
        
        Args:
            processed_folder: Path to processed JSON files with chunks
            embeddings_folder: Path to save embeddings
            chroma_db_path: Path to Chroma database
            model: OpenAI embedding model to use
        """
        self.processed_folder = Path(__file__).parent / processed_folder
        self.embeddings_folder = Path(__file__).parent / embeddings_folder
        self.chroma_db_path = Path(__file__).parent / chroma_db_path
        self.model = model
        
        self.embeddings_folder.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Initialize Chroma client
        self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_db_path))
        self.collection = self.chroma_client.get_or_create_collection(
            name="onenote_chunks",
            metadata={"description": "OneNote document chunks with embeddings"}
        )
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: The text to embed
        
        Returns:
            List of floats representing the embedding vector
        
        sample response:
            {
              "object": "embedding",
              "data": [
                {
                  "object": "embedding",
                  "embedding": [0.0023, -0.0145, ...],
                  "index": 0
                }
              ],
              "model": "text-embedding-3-small",
              "usage": {
                "prompt_tokens": 8,
                "total_tokens": 8
              }
            }
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return None
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in parallel.
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        tasks = [self.generate_embedding(text) for text in texts]
        # Asynchronously execute all tasks and gather results in order
        return await asyncio.gather(*tasks)
    
    async def process_chunks_file(self, chunks_filename: str):
        """
        Process a chunks JSON file and generate embeddings.
        
        Args:
            chunks_filename: Name of the chunks JSON file
        """
        chunks_path = self.processed_folder / chunks_filename
        
        if not chunks_path.exists():
            print(f"Error: File {chunks_filename} not found")
            return
        
        print(f"Processing: {chunks_filename}")
        
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        chunks = chunks_data['chunks']
        total_chunks = len(chunks)
        
        print(f"  - Generating embeddings for {total_chunks} chunks...")
        
        # Extract texts - texts is a list of strings
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings in batches of 100 (API limit)
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size
            
            print(f"    Batch {batch_num}/{total_batches}...")
            embeddings = await self.generate_embeddings_batch(batch)
            all_embeddings.extend(embeddings)
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, all_embeddings):
            chunk['embedding'] = embedding
            chunk['embedding_model'] = self.model
        
        # Save to Chroma vector database
        print(f"  - Storing {total_chunks} chunks in Chroma...")
        self._store_in_chroma(chunks, chunks_data['source_document'])
        
        # Create output data
        output_data = {
            'source_document': chunks_data['source_document'],
            'embedding_model': self.model,
            'total_chunks': total_chunks,
            'generated_date': datetime.now().isoformat(),
            'chunks': chunks
        }
        
        # Save embeddings as JSON backup
        output_filename = f"{chunks_path.stem}_embeddings.json"
        output_path = self.embeddings_folder / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved embeddings to: {output_path.name}")
        print(f"  - Embedding dimensions: {len(all_embeddings[0]) if all_embeddings else 0}")
    
    def _store_in_chroma(self, chunks: List[Dict], source_document: str):
        """
        Store chunks with embeddings in Chroma vector database.
        
        Args:
            chunks: List of chunk dictionaries with embeddings
            source_document: Source document filename
        """
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for idx, chunk in enumerate(chunks):
            # Create unique ID
            chunk_id = f"{source_document}_{chunk.get('section_idx', 0)}_{chunk.get('chunk_num', idx)}"
            ids.append(chunk_id)
            
            # Extract embedding
            embeddings.append(chunk['embedding'])
            
            # Extract document text
            documents.append(chunk['text'])
            
            # Extract metadata (exclude embedding to reduce storage)
            metadata = {
                'source_file': chunk.get('source_file', source_document),
                'heading': chunk.get('heading', ''),
                'heading_level': chunk.get('heading_level', 0),
                'section_idx': chunk.get('section_idx', 0),
                'chunk_num': chunk.get('chunk_num', idx),
                'word_count': chunk.get('word_count', 0),
                'embedding_model': chunk.get('embedding_model', self.model)
            }
            metadatas.append(metadata)
        
        # Add to Chroma collection in batch
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"  ✓ Stored {len(chunks)} chunks in Chroma database")
    
    async def process_all_chunks(self):
        """
        Process all chunk files and generate embeddings.
        """
        chunks_files = list(self.processed_folder.glob('*_chunks.json'))
        
        if not chunks_files:
            print(f"No chunk files found in {self.processed_folder}")
            print("\nRun chunk_text.py first to create chunks")
            return
        
        print(f"Found {len(chunks_files)} chunk file(s) to process\n")
        
        for chunks_file in chunks_files:
            await self.process_chunks_file(chunks_file.name)
            print()
        
        print("✓ All embeddings generated successfully!")


async def main():
    generator = EmbeddingGenerator()
    await generator.process_all_chunks()


if __name__ == '__main__':
    asyncio.run(main())
