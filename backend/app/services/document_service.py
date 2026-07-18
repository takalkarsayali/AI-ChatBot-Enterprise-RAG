# backend/app/services/document_service.py

class DocumentService:
    def __init__(self):
        # This is where your Pinecone setup from Phase 3 lives
        # self.vector_store = PineconeVectorStore()
        pass
        
    async def process_and_store(self, filename: str, contents: bytes, file_ext: str, metadata: dict):
        """Handles the parsing, chunking, and upserting from Phase 2 & 3"""
        # MOCK response for now so the UI upload button works
        return {"status": "success", "chunks_upserted": 5, "filename": filename}

    async def get_all_documents(self):
        """Retrieves the list of uploaded documents"""
        # MOCK response for the UI list
        return [
            {"id": "doc-1", "filename": "sample_handbook.pdf", "upload_time": "2026-07-04"},
        ]

    async def delete_document_by_id(self, document_id: str):
        """Deletes a document from the Pinecone index"""
        # MOCK response
        return True

# This is the exact instance the router is trying to import
document_service = DocumentService()