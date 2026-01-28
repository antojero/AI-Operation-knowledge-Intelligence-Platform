from django.contrib import admin
from .models import Document, DocumentChunk

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'created_at', 'id')
    search_fields = ('title', 'content')
    list_filter = ('organization', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'chunk_index', 'id')
    search_fields = ('text_content', 'document__title')
    list_filter = ('document__organization',)
    # Prevent loading massive embedding vectors in list view which creates lag
    # We can still view them in detail view if needed