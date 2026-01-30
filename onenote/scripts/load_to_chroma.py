"""
Load Embeddings to Chroma
Loads existing embeddings from JSON files into Chroma vector database.
Use this if you already have embeddings generated and want to populate Chroma.
"""

import json
import chromadb
from pathlib import Path
from typing import List, Dict


class ChromaLoader:
    def __init__(self, 
                 embeddings_folder='../embeddings',
                 chroma_db_path='../../chroma_db'):
        """
        Initialize the Chroma loader.
        
        Args:
            embeddings_folder: Path to embeddings JSON files
            chroma_db_path: Path to Chroma database
        """
        self.embeddings_folder = Path(__file__).parent / embeddings_folder
        self.chroma_db_path = Path(__file__).parent / chroma_db_path
        
        # Initialize Chroma client
        self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_db_path))
        self.collection = self.chroma_client.get_or_create_collection(
            name="onenote_chunks",
            metadata={"description": "OneNote document chunks with embeddings"}
        )
    
    def load_embeddings_file(self, json_filename: str):
        """
        Load embeddings from a single JSON file into Chroma.
        
        Args:
            json_filename: Name of the embeddings JSON file
        """
        json_path = self.embeddings_folder / json_filename
        
        if not json_path.exists():
            print(f"Error: File {json_filename} not found")
            return
        
        print(f"Loading: {json_filename}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = data['chunks']
        source_document = data['source_document']
        
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for idx, chunk in enumerate(chunks):
            # Create unique ID
            chunk_id = f"{source_document}_{chunk.get('section_idx', 0)}_{chunk.get('chunk_num', idx)}"
            
            # Check if already exists (avoid duplicates)
            try:
                existing = self.collection.get(ids=[chunk_id])
                if existing['ids']:
                    continue  # Skip if already exists
            except:
                pass
            
            ids.append(chunk_id)
            embeddings.append(chunk['embedding'])
            documents.append(chunk['text'])
            
            # Extract metadata
            metadata = {
                'source_file': chunk.get('source_file', source_document),
                'heading': chunk.get('heading', ''),
                'heading_level': chunk.get('heading_level', 0),
                'section_idx': chunk.get('section_idx', 0),
                'chunk_num': chunk.get('chunk_num', idx),
                'word_count': chunk.get('word_count', 0),
                'embedding_model': chunk.get('embedding_model', 'unknown')
            }
            metadatas.append(metadata)
        
        if ids:
            # Add to Chroma collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            print(f"  ✓ Loaded {len(ids)} chunks into Chroma")
        else:
            print(f"  - All chunks already exist in Chroma")
    
    def load_all_embeddings(self):
        """
        Load all embeddings JSON files into Chroma.
        """
        embeddings_files = list(self.embeddings_folder.glob('*_embeddings.json'))
        
        if not embeddings_files:
            print(f"No embeddings files found in {self.embeddings_folder}")
            print("\nRun generate_embeddings.py first to create embeddings")
            return
        
        print(f"Found {len(embeddings_files)} embeddings file(s)\n")
        
        total_loaded = 0
        for embeddings_file in embeddings_files:
            self.load_embeddings_file(embeddings_file.name)
            total_loaded += 1
        
        # Get collection stats
        count = self.collection.count()
        print(f"\n✓ Chroma database now contains {count} chunks")
    
    def get_collection_stats(self):
        """
        Print statistics about the Chroma collection.
        """
        count = self.collection.count()
        print(f"Chroma Collection: onenote_chunks")
        print(f"Total chunks: {count}")
        
        if count > 0:
            # Get a sample to show metadata
            sample = self.collection.get(limit=1, include=['metadatas'])
            if sample['metadatas']:
                print(f"\nSample metadata:")
                for key, value in sample['metadatas'][0].items():
                    print(f"  {key}: {value}")


if __name__ == '__main__':
    import sys
    
    loader = ChromaLoader()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'stats':
        # Show collection statistics
        loader.get_collection_stats()
    else:
        # Load all embeddings
        loader.load_all_embeddings()
