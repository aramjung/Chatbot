"""
Run Pipeline
Orchestrates the entire document processing pipeline.
"""

import asyncio
import sys
from pathlib import Path

# Add scripts to path
sys.path.append(str(Path(__file__).parent))

from import_docs import DocumentImporter
from chunk_text import TextChunker
from generate_embeddings import EmbeddingGenerator


async def run_full_pipeline():
    """
    Run the complete pipeline: import → chunk → embed
    """
    print("=" * 60)
    print("OneNote Document Processing Pipeline")
    print("=" * 60)
    print()
    
    # Step 1: Import documents
    print("STEP 1: Importing documents from .docx files")
    print("-" * 60)
    importer = DocumentImporter()
    docs = importer.process_all_documents()
    
    if not docs:
        print("\nPipeline stopped: No documents to process")
        print("\nNext steps:")
        print("1. Export your OneNote notebooks as .docx files")
        print("2. Place them in: onenote/raw/")
        print("3. Run this script again")
        return
    
    print("\n")
    
    # Step 2: Chunk texts
    print("STEP 2: Chunking documents into smaller pieces")
    print("-" * 60)
    chunker = TextChunker(chunk_size=500, overlap=50)
    chunks = chunker.process_all_documents()
    
    print("\n")
    
    # Step 3: Generate embeddings
    print("STEP 3: Generating embeddings with OpenAI")
    print("-" * 60)
    generator = EmbeddingGenerator()
    await generator.process_all_chunks()
    
    print("\n")
    print("=" * 60)
    print("✓ Pipeline completed successfully!")
    print("=" * 60)
    print(f"\nProcessed: {len(docs)} document(s)")
    print(f"Created: {len(chunks)} chunk(s)")
    print("\nYour embeddings are ready for vector database storage!")


def run_import_only():
    """Run only the import step."""
    print("Running: Document Import")
    importer = DocumentImporter()
    importer.process_all_documents()


def run_chunk_only():
    """Run only the chunking step."""
    print("Running: Text Chunking")
    chunker = TextChunker(chunk_size=500, overlap=50)
    chunker.process_all_documents()


async def run_embed_only():
    """Run only the embedding step."""
    print("Running: Embedding Generation")
    generator = EmbeddingGenerator()
    await generator.process_all_chunks()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'import':
            run_import_only()
        elif command == 'chunk':
            run_chunk_only()
        elif command == 'embed':
            asyncio.run(run_embed_only())
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  python run_pipeline.py         - Run full pipeline")
            print("  python run_pipeline.py import  - Import documents only")
            print("  python run_pipeline.py chunk   - Chunk documents only")
            print("  python run_pipeline.py embed   - Generate embeddings only")
    else:
        # Run full pipeline
        asyncio.run(run_full_pipeline())
