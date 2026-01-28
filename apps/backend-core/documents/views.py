from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from pgvector.django import CosineDistance
from .models import DocumentChunk
from .utils import get_embedding
from agent_runs.views import IsInternalServiceOrAuthenticated

class VectorSearchView(APIView):
    permission_classes = [IsInternalServiceOrAuthenticated]

    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({"error": "Query required"}, status=400)

        # Generate embedding for the query
        try:
            query_embedding = get_embedding(query)
        except Exception as e:
            return Response({"error": f"Embedding generation failed: {str(e)}"}, status=500)

        # Search for similar chunks using Cosine Distance
        # We limit to top 5 results
        similar_chunks = DocumentChunk.objects.annotate(
            distance=CosineDistance('embedding', query_embedding)
        ).order_by('distance')[:5]

        results = []
        for chunk in similar_chunks:
            results.append({
                "id": chunk.id,
                "document_title": chunk.document.title,
                "text_content": chunk.text_content,
                "score": 1 - chunk.distance  # Convert distance to similarity score
            })

        return Response({"results": results})

class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        title = request.data.get('title')
        
        if not file or not title:
             return Response({"error": "File and title required"}, status=400)
             
        # 1. Create Document
        from .models import Document, DocumentChunk
        doc = Document.objects.create(
            organization=request.user.organization,
            title=title,
            content="Processing..."
        )
        
        try:
            # 2. Extract Text (Simplified for PDF/Text)
            text_content = ""
            if file.name.endswith('.pdf'):
                import pypdf
                pdf = pypdf.PdfReader(file)
                for page in pdf.pages:
                    text_content += page.extract_text() + "\n"
            else:
                text_content = file.read().decode('utf-8')
            
            doc.content = text_content
            doc.save()
            
            # 3. Chunk Text
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            chunks = text_splitter.split_text(text_content)
            
            # 4. Embed and Save Chunks
            for i, chunk_text in enumerate(chunks):
                embedding = get_embedding(chunk_text)
                DocumentChunk.objects.create(
                    document=doc,
                    chunk_index=i,
                    text_content=chunk_text,
                    embedding=embedding
                )
                
            return Response({"status": "success", "document_id": doc.id, "chunks": len(chunks)})
            
        except Exception as e:
            doc.delete() # Cleanup
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)
