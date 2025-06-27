#!/usr/bin/env python3
"""
Smart Document Processing System with Token Management and Azure Storage
Handles large documents through intelligent chunking and cloud persistence
"""

import tiktoken
import hashlib
import uuid
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import json
import re
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

@dataclass
class DocumentChunk:
    """Represents a chunk of a larger document"""
    content: str
    chunk_index: int
    total_chunks: int
    token_count: int
    start_char: int
    end_char: int
    chunk_type: str  # 'header', 'paragraph', 'section', 'overlap'
    metadata: Dict[str, Any]
    
@dataclass 
class ProcessedDocument:
    """Represents a fully processed document with all chunks and analysis"""
    document_id: str
    original_filename: str
    file_size: int
    total_tokens: int
    total_chunks: int
    document_type: str
    upload_timestamp: datetime
    azure_blob_url: str
    chunks: List[DocumentChunk]
    analysis_results: Dict[str, Any]
    processing_status: str  # 'pending', 'processing', 'completed', 'error'

class SmartDocumentProcessor:
    """Advanced document processing with token management and Azure storage"""
    
    def __init__(self, 
                 model_name: str = "gpt-4", 
                 max_chunk_tokens: int = 4000,
                 azure_connection_string: str = None,
                 container_name: str = "digital-twin-documents"):
        
        # Token management
        try:
            self.encoder = tiktoken.encoding_for_model(model_name)
        except:
            # Fallback encoding if model not found
            self.encoder = tiktoken.get_encoding("cl100k_base")
            
        self.max_chunk_tokens = max_chunk_tokens
        self.model_name = model_name
        
        # Azure Blob Storage setup
        self.azure_connection_string = azure_connection_string
        self.container_name = container_name
        self.blob_client = None
        
        if azure_connection_string:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
                self._ensure_container_exists()
            except Exception as e:
                print(f"⚠️ Azure Blob Storage not available: {e}")
                
        # Processing statistics
        self.processed_documents: Dict[str, ProcessedDocument] = {}
        
    def _ensure_container_exists(self):
        """Create Azure container if it doesn't exist"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            container_client.create_container()
            print(f"✅ Created Azure container: {self.container_name}")
        except ResourceExistsError:
            print(f"✅ Azure container exists: {self.container_name}")
        except Exception as e:
            print(f"❌ Error with Azure container: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Accurately count tokens for the specified model"""
        try:
            return len(self.encoder.encode(text))
        except Exception as e:
            # Fallback: rough estimation (4 chars per token)
            return len(text) // 4
    
    def estimate_processing_time(self, token_count: int) -> int:
        """Estimate processing time in seconds based on token count"""
        # Rough estimate: 1000 tokens per 10 seconds
        return max(10, (token_count // 1000) * 10)
    
    def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """Analyze document structure to inform intelligent chunking"""
        
        structure = {
            "total_chars": len(content),
            "total_tokens": self.count_tokens(content),
            "estimated_pages": len(content) // 2000,  # Rough page estimate
            "has_headers": False,
            "has_sections": False,
            "has_bullets": False,
            "has_numbers": False,
            "paragraph_count": 0,
            "line_count": len(content.split('\n')),
            "document_type": "unknown"
        }
        
        # Detect headers (lines starting with #, or ALL CAPS lines)
        lines = content.split('\n')
        header_patterns = [
            r'^#+\s+',  # Markdown headers
            r'^[A-Z][A-Z\s]{10,}$',  # ALL CAPS headers
            r'^\d+\.',  # Numbered sections
            r'^[IVX]+\.',  # Roman numerals
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for headers
            for pattern in header_patterns:
                if re.match(pattern, line):
                    structure["has_headers"] = True
                    break
        
        # Detect structure patterns
        if '•' in content or '*' in content or '-' in content:
            structure["has_bullets"] = True
            
        if re.search(r'\d+\.', content):
            structure["has_numbers"] = True
            
        # Count paragraphs (double newlines)
        paragraphs = re.split(r'\n\s*\n', content)
        structure["paragraph_count"] = len(paragraphs)
        
        # Determine document type
        if "contract" in content.lower() or "agreement" in content.lower():
            structure["document_type"] = "contract"
        elif "meeting" in content.lower() or "attendees" in content.lower():
            structure["document_type"] = "meeting"
        elif "report" in content.lower() or "summary" in content.lower():
            structure["document_type"] = "report"
        elif structure["has_headers"] and structure["paragraph_count"] > 10:
            structure["document_type"] = "document"
        else:
            structure["document_type"] = "text"
            
        return structure
    
    def create_smart_chunks(self, content: str, structure: Dict[str, Any], 
                           overlap_chars: int = 200) -> List[DocumentChunk]:
        """Create intelligent chunks based on document structure"""
        
        chunks = []
        chunk_size_chars = self.max_chunk_tokens * 3  # Rough char-to-token ratio
        
        if structure["total_tokens"] <= self.max_chunk_tokens:
            # Small document - single chunk
            chunk = DocumentChunk(
                content=content,
                chunk_index=0,
                total_chunks=1,
                token_count=structure["total_tokens"],
                start_char=0,
                end_char=len(content),
                chunk_type="full_document",
                metadata={"document_type": structure["document_type"]}
            )
            return [chunk]
        
        # Strategy 1: Paragraph-based chunking (preferred)
        if structure["paragraph_count"] > 3:
            chunks = self._chunk_by_paragraphs(content, chunk_size_chars, overlap_chars)
        
        # Strategy 2: Section-based chunking
        elif structure["has_headers"]:
            chunks = self._chunk_by_sections(content, chunk_size_chars, overlap_chars)
        
        # Strategy 3: Sentence-based chunking
        else:
            chunks = self._chunk_by_sentences(content, chunk_size_chars, overlap_chars)
        
        # Add token counts to chunks
        for i, chunk in enumerate(chunks):
            chunk.chunk_index = i
            chunk.total_chunks = len(chunks)
            chunk.token_count = self.count_tokens(chunk.content)
            
        return chunks
    
    def _chunk_by_paragraphs(self, content: str, chunk_size: int, overlap: int) -> List[DocumentChunk]:
        """Chunk document by paragraphs with smart overlap"""
        paragraphs = re.split(r'\n\s*\n', content)
        chunks = []
        current_chunk = ""
        start_char = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # If adding this paragraph exceeds chunk size, finalize current chunk
            if current_chunk and len(current_chunk + para) > chunk_size:
                chunks.append(DocumentChunk(
                    content=current_chunk.strip(),
                    chunk_index=len(chunks),
                    total_chunks=0,  # Will be set later
                    token_count=0,   # Will be set later
                    start_char=start_char,
                    end_char=start_char + len(current_chunk),
                    chunk_type="paragraph_group",
                    metadata={"paragraph_count": current_chunk.count('\n\n') + 1}
                ))
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + para
                start_char = start_char + len(current_chunk) - len(overlap_text) - len(para) - 2
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
                    start_char = content.find(para)
        
        # Add final chunk
        if current_chunk:
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                chunk_index=len(chunks),
                total_chunks=0,
                token_count=0,
                start_char=start_char,
                end_char=start_char + len(current_chunk),
                chunk_type="paragraph_group",
                metadata={"paragraph_count": current_chunk.count('\n\n') + 1}
            ))
            
        return chunks
    
    def _chunk_by_sections(self, content: str, chunk_size: int, overlap: int) -> List[DocumentChunk]:
        """Chunk document by detected sections/headers"""
        # Find section boundaries
        lines = content.split('\n')
        section_starts = []
        
        header_patterns = [
            r'^#+\s+',  # Markdown headers
            r'^[A-Z][A-Z\s]{10,}$',  # ALL CAPS headers
            r'^\d+\.',  # Numbered sections
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            for pattern in header_patterns:
                if re.match(pattern, line):
                    section_starts.append(i)
                    break
        
        if not section_starts:
            return self._chunk_by_paragraphs(content, chunk_size, overlap)
        
        chunks = []
        for i, start_line in enumerate(section_starts):
            end_line = section_starts[i + 1] if i + 1 < len(section_starts) else len(lines)
            section_content = '\n'.join(lines[start_line:end_line]).strip()
            
            if len(section_content) > chunk_size:
                # Large section - split further
                sub_chunks = self._chunk_by_paragraphs(section_content, chunk_size, overlap)
                chunks.extend(sub_chunks)
            else:
                chunks.append(DocumentChunk(
                    content=section_content,
                    chunk_index=len(chunks),
                    total_chunks=0,
                    token_count=0,
                    start_char=content.find(section_content),
                    end_char=content.find(section_content) + len(section_content),
                    chunk_type="section",
                    metadata={"header": lines[start_line].strip()}
                ))
        
        return chunks
    
    def _chunk_by_sentences(self, content: str, chunk_size: int, overlap: int) -> List[DocumentChunk]:
        """Fallback chunking by sentences"""
        sentences = re.split(r'[.!?]+', content)
        chunks = []
        current_chunk = ""
        start_char = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if current_chunk and len(current_chunk + sentence) > chunk_size:
                chunks.append(DocumentChunk(
                    content=current_chunk.strip(),
                    chunk_index=len(chunks),
                    total_chunks=0,
                    token_count=0,
                    start_char=start_char,
                    end_char=start_char + len(current_chunk),
                    chunk_type="sentence_group",
                    metadata={"sentence_count": current_chunk.count('.') + current_chunk.count('!') + current_chunk.count('?')}
                ))
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
                start_char = start_char + len(current_chunk) - len(overlap_text) - len(sentence) - 1
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                    start_char = content.find(sentence)
        
        # Add final chunk
        if current_chunk:
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                chunk_index=len(chunks),
                total_chunks=0,
                token_count=0,
                start_char=start_char,
                end_char=start_char + len(current_chunk),
                chunk_type="sentence_group",
                metadata={"sentence_count": current_chunk.count('.') + current_chunk.count('!') + current_chunk.count('?')}
            ))
            
        return chunks
    
    async def store_document_in_azure(self, content: str, filename: str, 
                                    document_id: str) -> Optional[str]:
        """Store document in Azure Blob Storage"""
        
        if not self.blob_service_client:
            return None
            
        try:
            blob_name = f"{document_id}/{filename}"
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            
            # Upload document content
            blob_client.upload_blob(content.encode('utf-8'), overwrite=True)
            
            # Store metadata
            metadata = {
                "document_id": document_id,
                "original_filename": filename,
                "upload_timestamp": datetime.now().isoformat(),
                "file_size": str(len(content)),
                "content_type": "text/plain"
            }
            blob_client.set_blob_metadata(metadata)
            
            return blob_client.url
            
        except Exception as e:
            print(f"❌ Error storing document in Azure: {e}")
            return None
    
    async def retrieve_document_from_azure(self, document_id: str, 
                                         filename: str) -> Optional[str]:
        """Retrieve document from Azure Blob Storage"""
        
        if not self.blob_service_client:
            return None
            
        try:
            blob_name = f"{document_id}/{filename}"
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            download_stream = blob_client.download_blob()
            content = download_stream.readall().decode('utf-8')
            return content
            
        except ResourceNotFoundError:
            print(f"⚠️ Document not found in Azure: {document_id}/{filename}")
            return None
        except Exception as e:
            print(f"❌ Error retrieving document from Azure: {e}")
            return None
    
    async def list_stored_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all stored documents with metadata"""
        
        if not self.blob_service_client:
            return []
            
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blobs = container_client.list_blobs(include=['metadata'])
            
            documents = []
            for blob in blobs:
                if blob.metadata:
                    doc_info = {
                        "document_id": blob.metadata.get("document_id", ""),
                        "filename": blob.metadata.get("original_filename", blob.name),
                        "upload_date": blob.metadata.get("upload_timestamp", ""),
                        "file_size": int(blob.metadata.get("file_size", 0)),
                        "blob_url": f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob.name}",
                        "last_modified": blob.last_modified.isoformat() if blob.last_modified else ""
                    }
                    documents.append(doc_info)
                    
                if len(documents) >= limit:
                    break
                    
            return sorted(documents, key=lambda x: x["upload_date"], reverse=True)
            
        except Exception as e:
            print(f"❌ Error listing documents: {e}")
            return []
    
    def generate_document_id(self, filename: str, content: str) -> str:
        """Generate unique document ID based on filename and content hash"""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return f"{timestamp}_{clean_filename}_{content_hash}"
    
    async def process_document(self, content: str, filename: str, 
                             store_in_azure: bool = True) -> ProcessedDocument:
        """Main document processing pipeline"""
        
        # Generate document ID
        document_id = self.generate_document_id(filename, content)
        
        # Analyze document structure
        structure = self.analyze_document_structure(content)
        
        # Create smart chunks
        chunks = self.create_smart_chunks(content, structure)
        
        # Store in Azure if requested
        azure_url = None
        if store_in_azure:
            azure_url = await self.store_document_in_azure(content, filename, document_id)
        
        # Create processed document object
        processed_doc = ProcessedDocument(
            document_id=document_id,
            original_filename=filename,
            file_size=len(content),
            total_tokens=structure["total_tokens"],
            total_chunks=len(chunks),
            document_type=structure["document_type"],
            upload_timestamp=datetime.now(),
            azure_blob_url=azure_url or "",
            chunks=chunks,
            analysis_results={},
            processing_status="completed"
        )
        
        # Store in memory
        self.processed_documents[document_id] = processed_doc
        
        return processed_doc
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        if not self.processed_documents:
            return {"total_documents": 0}
            
        total_docs = len(self.processed_documents)
        total_tokens = sum(doc.total_tokens for doc in self.processed_documents.values())
        total_chunks = sum(doc.total_chunks for doc in self.processed_documents.values())
        
        doc_types = {}
        for doc in self.processed_documents.values():
            doc_types[doc.document_type] = doc_types.get(doc.document_type, 0) + 1
        
        return {
            "total_documents": total_docs,
            "total_tokens_processed": total_tokens,
            "total_chunks_created": total_chunks,
            "average_tokens_per_document": total_tokens // total_docs if total_docs > 0 else 0,
            "average_chunks_per_document": total_chunks // total_docs if total_docs > 0 else 0,
            "document_types": doc_types,
            "azure_storage_enabled": self.blob_service_client is not None
        }