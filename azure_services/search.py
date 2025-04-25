import os
import base64
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField
# from azure_services.text_extraction import create_chunks
from transformers import pipeline
from dotenv import load_dotenv
load_dotenv()
#from config import FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_KEY, SEARCH_SERVICE_ENDPOINT, SEARCH_API_KEY, SEARCH_INDEX_NAME

SEARCH_INDEX_NAME = "legal-index-rania"
CHUNK_SIZE = 2000  # Increased chunk size
OVERLAP = 200  

def get_existing_index_fields(index_name):
    index_client = SearchIndexClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=AzureKeyCredential(SEARCH_API_KEY))

    try:
        index = index_client.get_index(index_name)
        return [field.name for field in index.fields]
    except Exception as e:
        print(f"Could not get index schema: {str(e)}")
        return None

# Create the search index if it doesn't exist or create a new version if it does
def create_or_use_search_index():
    index_client = SearchIndexClient(endpoint=SEARCH_SERVICE_ENDPOINT, credential=AzureKeyCredential(SEARCH_API_KEY))

    # Check if the index already exists
    existing_indexes = [i.name for i in index_client.list_indexes()]
    existing_fields = None

    if SEARCH_INDEX_NAME in existing_indexes:
        print(f"Search index '{SEARCH_INDEX_NAME}' already exists.")
        existing_fields = get_existing_index_fields(SEARCH_INDEX_NAME)
        print(f"Existing fields: {existing_fields}")
        return SEARCH_INDEX_NAME, existing_fields

    # If not, create a new index
    fields = [
        SimpleField(name="id", type="Edm.String", key=True),
        SearchableField(name="content", type="Edm.String", analyzer_name="en.microsoft"),
        SimpleField(name="filename", type="Edm.String"),
    ]

    index = SearchIndex(name=SEARCH_INDEX_NAME, fields=fields)

    try:
        index_client.create_index(index)
        print(f"Search index '{SEARCH_INDEX_NAME}' created successfully.")
        return SEARCH_INDEX_NAME, [field.name for field in fields]
    except Exception as e:
        print(f"Error creating index: {str(e)}")
        return None, None

# Create better chunks with text segmentation
def create_chunks(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    if not text:
        return []

    # Try to chunk at paragraph breaks first
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
        else:
            # If the current chunk has content, add it to chunks
            if current_chunk:
                chunks.append(current_chunk)

            # If paragraph is larger than chunk_size, split it further
            if len(paragraph) > chunk_size:
                sentences = paragraph.split(". ")
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 2 <= chunk_size:
                        if current_chunk:
                            current_chunk += ". " + sentence
                        else:
                            current_chunk = sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)

                        # If the sentence is still too large, split it by hard character limits
                        if len(sentence) > chunk_size:
                            for i in range(0, len(sentence), chunk_size - overlap):
                                chunks.append(sentence[i:i + chunk_size])
                        else:
                            current_chunk = sentence
            else:
                current_chunk = paragraph

    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(current_chunk)

    # If no chunks were created (unlikely but possible), fall back to character-based chunking
    if not chunks and text:
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]

    return chunks

# Upload extracted text to Azure Search with better batching
def upload_text_to_search(filename, text, index_name, allowed_fields):
    search_client = SearchClient(
        endpoint=SEARCH_SERVICE_ENDPOINT,
        index_name=index_name,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )

    # Create semantically meaningful chunks
    chunks = create_chunks(text)
    total_chunks = len(chunks)

    print(f"📦 Created {total_chunks} chunks for {filename}")

    # Prepare all documents before uploading
    documents = []
    for i, chunk in enumerate(chunks):
        # Encode the filename to create a valid document ID
        encoded_filename = base64.urlsafe_b64encode(filename.encode()).decode().rstrip("=")

        # Create document with only the allowed fields
        doc = {"id": f"{encoded_filename}_{i}", "content": chunk, "filename": filename}

        # Only add fields that exist in the index schema
        documents.append(doc)

    # Upload documents in batches
    batch_size = 100
    success_count = 0

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        print(f"Uploading batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}...")
        try:
            results = search_client.upload_documents(documents=batch)
            succeeded = sum(1 for r in results if r.succeeded)
            success_count += succeeded
            print(f"✅ Batch upload: {succeeded}/{len(batch)} succeeded")
        except Exception as e:
            print(f"❌ Error uploading batch: {str(e)}")

            # Try uploading documents one by one for this batch
            if len(batch) > 1:
                print("Trying to upload documents one by one...")
                for doc in batch:
                    try:
                        result = search_client.upload_documents(documents=[doc])
                        if result[0].succeeded:
                            success_count += 1
                            print("✅ Single document upload succeeded")
                        else:
                            print(f"❌ Single document upload failed: {result[0].error_message}")
                    except Exception as e2:
                        print(f"❌ Error uploading single document: {str(e2)}")

    print(f"✅ Indexed {filename} with {total_chunks} chunks. Successfully uploaded {success_count} chunks.")
    return success_count

# New function to search for top-k chunks related to a query
def search_top_k_chunks(query, top_k=5):
    """
    Search for top-k chunks that match the given query.
    
    Args:
        query (str): The search query
        top_k (int): Number of top chunks to retrieve
        
    Returns:
        list: List of dictionaries containing search results
    """
    search_client = SearchClient(
        endpoint=SEARCH_SERVICE_ENDPOINT,
        index_name=SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    # Execute search with semantic ranking
    results = search_client.search(
        search_text=query,
        top=top_k,
        search_fields=["content"],
        select=["id", "content", "filename"],
        query_type="semantic",
        semantic_configuration_name="default",
        query_caption="extractive|highlight-false"
    )
    
    # Convert results to list
    result_list = []
    for result in results:
        result_list.append({
            "id": result["id"],
            "content": result["content"],
            "filename": result["filename"],
            "score": result["@search.score"] if "@search.score" in result else 0.0
        })
    
    print(f"🔍 Found {len(result_list)} chunks matching the query")
    return result_list

# Get chunks from search index without executing a search
def get_chunks_by_filename(filename, top_k=None):
    """
    Retrieve chunks from the search index by filename.
    
    Args:
        filename (str): Name of the file to retrieve chunks for
        top_k (int, optional): Limit the number of returned chunks
        
    Returns:
        list: List of chunks for the specified file
    """
    search_client = SearchClient(
        endpoint=SEARCH_SERVICE_ENDPOINT,
        index_name=SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )
    
    # Create a filter expression for the filename
    filter_expression = f"filename eq '{filename}'"
    
    # Execute search with filter
    results = search_client.search(
        search_text="*",
        filter=filter_expression,
        top=top_k if top_k else 1000,  # Use top_k if provided, otherwise use a large number
        select=["id", "content", "filename"]
    )
    
    # Convert results to list
    chunk_list = []
    for result in results:
        chunk_list.append({
            "id": result["id"],
            "content": result["content"],
            "filename": result["filename"]
        })
    
    print(f"📄 Retrieved {len(chunk_list)} chunks for file '{filename}'")
    return chunk_list

