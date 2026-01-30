"""
Text Chunking Script
Splits processed documents into chunks suitable for embedding and retrieval.
"""

import os
import json
from pathlib import Path
from typing import List, Dict

class TextChunker:
    def __init__(self, 
                 processed_folder='../processed',
                 chunk_size=500,
                 overlap=50):
        """
        Initialize the chunker.
        
        Args:
            processed_folder: Path to processed JSON files
            chunk_size: Target number of words per chunk
            overlap: Number of words to overlap between chunks
        """
        self.processed_folder = Path(__file__).parent / processed_folder
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: The text to chunk
            metadata: Metadata to attach to each chunk (heading, level, etc.)
        
        Returns:
            List of chunk dictionaries with text and metadata
        """
        words = text.split()
        chunks = []
        
        if len(words) <= self.chunk_size:
            # Text is short enough, return as single chunk
            chunks.append({
                'text': text,
                'word_count': len(words),
                **metadata
            })
            return chunks
        
        # Create overlapping chunks
        start = 0
        chunk_num = 0
        
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                'text': chunk_text,
                'word_count': len(chunk_words),
                'chunk_num': chunk_num,
                **metadata
            })
            
            chunk_num += 1
            start += self.chunk_size - self.overlap
        
        return chunks
    
    def process_document(self, json_filename: str) -> List[Dict]:
        """
        Process a single JSON document and create chunks.
        
        Args:
            json_filename: Name of the JSON file to process
        
        Returns:
            List of all chunks from the document
        """
        json_path = self.processed_folder / json_filename
        
        if not json_path.exists():
            print(f"Error: File {json_filename} not found")
            return []
        
        print(f"Chunking: {json_filename}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
        
        all_chunks = []
        
        for section_idx, section in enumerate(doc_data['sections']):
            # Create metadata for this section
            section_metadata = {
                'source_file': doc_data['source_file'],
                'section_idx': section_idx,
                'heading': section['heading'],
                'heading_level': section['level']
            }
            
            # Chunk this section
            section_chunks = self.chunk_text(section['text'], section_metadata)
            all_chunks.extend(section_chunks)
        
        print(f"  - Created {len(all_chunks)} chunks")
        
        # Save chunks as separate JSON
        output_filename = f"{json_path.stem}_chunks.json"
        output_path = json_path.parent / output_filename
        
        chunks_data = {
            'source_document': doc_data['source_file'],
            'chunk_size': self.chunk_size,
            'overlap': self.overlap,
            'total_chunks': len(all_chunks),
            'chunks': all_chunks
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved chunks to: {output_path.name}")
        
        return all_chunks
    
    def process_all_documents(self) -> List[Dict]:
        """
        Process all JSON files in the processed folder.
        
        Returns:
            List of all chunks from all documents
        """
        json_files = [f for f in self.processed_folder.glob('*.json') 
                     if not f.name.endswith('_chunks.json')]
        
        if not json_files:
            print(f"No processed JSON files found in {self.processed_folder}")
            print("\nRun import_docs.py first to process your .docx files")
            return []
        
        print(f"Found {len(json_files)} document(s) to chunk\n")
        
        all_chunks = []
        for json_file in json_files:
            chunks = self.process_document(json_file.name)
            all_chunks.extend(chunks)
        
        print(f"\n✓ Total chunks created: {len(all_chunks)}")
        return all_chunks


if __name__ == '__main__':
    chunker = TextChunker(chunk_size=500, overlap=50)
    chunker.process_all_documents()
