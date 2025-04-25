# import streamlit as st
# import tempfile
# import os

# from azure_services.blob import upload_file_to_blob
# from azure_services.search import create_or_use_search_index, upload_text_to_search, get_existing_index_fields
# from azure_services.text_extraction import extract_text_from_pdf
# from azure_services.qa import semantic_qa
# #from config import FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_KEY, SEARCH_SERVICE_ENDPOINT, SEARCH_API_KEY, SEARCH_INDEX_NAME

# # Page configuration
# st.set_page_config(
#     page_title="Legal Document QA",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # --- Sidebar ---
# with st.sidebar:
#     st.title("⚖️ Legal Document QA")
    
#     # About section
#     st.markdown("### About")
#     st.info("""
#     This application allows you to upload legal PDF documents and ask questions about their content.
    
#     **Features:**
#     - PDF document upload
#     - Text extraction using Azure Form Recognizer
#     - Document indexing with Azure Cognitive Search
#     - AI-powered question answering
    
#     **How to use:**
#     1. Upload legal PDF documents
#     2. Wait for processing to complete
#     3. Ask questions about the document content
#     """)
    
#     # Advanced settings
#     st.markdown("### Settings")
#     search_top_k = st.slider(
#         "Number of documents to retrieve (top-k)",
#         min_value=1,
#         max_value=10,
#         value=5,
#         help="Controls how many documents are retrieved during the search phase."
#     )
    
#     st.markdown("---")
#     st.markdown("Powered by Azure Cognitive Services")

# # Main content
# st.title("⚖️ Legal Document Question Answering")

# # Create tabs
# tabs = st.tabs(["📄 Document Upload", "🤖 Ask Questions"])

# # --- File Upload Section ---
# with tabs[0]:
#     st.header("Upload Legal PDF Document")
    
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         uploaded_files = st.file_uploader("Choose PDF file(s)", type=["pdf"], accept_multiple_files=True)

#     with col2:
#         if "documents" in st.session_state and st.session_state.documents:
#             last_doc = st.session_state.documents[-1]
#             st.success(f"Most recent document: {last_doc['filename']}")

#     if uploaded_files:
#         if "documents" not in st.session_state:
#             st.session_state.documents = []

#         for uploaded_file in uploaded_files:
#             if uploaded_file.name in [doc["filename"] for doc in st.session_state.documents]:
#                 st.info(f"Document '{uploaded_file.name}' already uploaded.")
#                 continue

#             with st.spinner(f"Processing document: {uploaded_file.name}"):
#                 progress_bar = st.progress(0)

#                 # Step 1: Save temp file
#                 with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#                     tmp_file.write(uploaded_file.read())
#                     local_path = tmp_file.name
#                     filename = uploaded_file.name
#                 progress_bar.progress(20)

#                 # Step 2: Upload to Azure Blob Storage
#                 upload_file_to_blob(local_path, filename)
#                 progress_bar.progress(40)

#                 # Step 3: Extract text
#                 extracted_text = extract_text_from_pdf(local_path)
#                 progress_bar.progress(60)

#                 # Step 4: Create search index
#                 index_name, allowed_fields = create_or_use_search_index()
#                 progress_bar.progress(80)

#                 # Step 5: Upload to Azure Search
#                 upload_text_to_search(filename, extracted_text, index_name, allowed_fields)
#                 progress_bar.progress(100)

#                 # Save to session state
#                 st.session_state.documents.append({
#                     "filename": filename,
#                     "local_path": local_path,
#                     "extracted_text": extracted_text,
#                     "index_name": index_name,
#                     "allowed_fields": allowed_fields,
#                 })

#                 # Show success and metrics
#                 st.success(f"✅ Document '{filename}' processed successfully!")
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.metric("Document Size", f"{len(uploaded_file.getvalue())/1024:.1f} KB")
#                 with col2:
#                     st.metric("Extracted Text", f"{len(extracted_text)} characters")

# # # --- Question Answering Section ---
# # with tabs[1]:
# #     st.header("Ask Questions from Your Legal Documents")
    
# #     if "documents" in st.session_state and st.session_state.documents:
# #         query = st.text_input("Enter your legal question:", placeholder="Example: What are the main contractual obligations?")
        
# #         if query:
# #             with st.spinner("Finding answers..."):
# #                 # Use top-k value
# #                 result = semantic_qa(query, search_top_k=search_top_k)
                
# #                 # Show answer
# #                 st.markdown("### Results")
# #                 answer_container = st.container()
# #                 with answer_container:
# #                     st.markdown(f"""
# #                     <div style="padding: 20px; border-radius: 5px; background-color: #f0f2f6;">
# #                         <h4>Answer:</h4>
# #                         <p>{result['answer']}</p>
# #                     </div>
# #                     """, unsafe_allow_html=True)
                
# #                 with st.expander("📄 View source context"):
# #                     context = result['context']
# #                     if context:
# #                         st.markdown(context)
# #                     else:
# #                         st.info("No context available for this answer.")

# #                 st.markdown("#### Not what you're looking for?")
# #                 st.markdown("Try refining your question or adjusting the top-k value in the sidebar.")
# #     else:
# #         st.info("👈 Please upload and process at least one document in the 'Document Upload' tab first.")
# #         st.markdown("""
# #         <div style="text-align: center; padding: 50px;">
# #             <h3>No documents indexed yet</h3>
# #             <p>Upload a legal document to start asking questions</p>
# #         </div>
# #         """, unsafe_allow_html=True)

# # --- Question Answering Section ---
# with tabs[1]:
#     st.header("Ask Questions from Your Legal Documents")
    
#     if "documents" in st.session_state and st.session_state.documents:
#         query = st.text_input("Enter your legal question:", placeholder="Example: What are the main contractual obligations?")
        
#         if query:
#             with st.spinner("Finding answers..."):
#                 # Use top-k value
#                 result = semantic_qa(query, search_top_k=search_top_k)
                
#                 # Show answer
#                 st.markdown("### Results")
#                 answer_container = st.container()
#                 with answer_container:
#                     st.markdown(f"""
#                     <div style="padding: 20px; border-radius: 5px; background-color: #f0f2f6;">
#                         <h4>Answer:</h4>
#                         <p>{result['answer']}</p>
#                         <h5>Source Document:</h5>
#                         <p>{result['source_filename'] if result['source_filename'] else 'Not available'}</p>
#                         <h5>Retrieval Latency:</h5>
#                         <p>{result['search_latency']:.3f} seconds</p>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 with st.expander("📄 View source context"):
#                     context = result['context']
#                     if context:
#                         st.markdown(context)
#                     else:
#                         st.info("No context available for this answer.")

#                 st.markdown("#### Not what you're looking for?")
#                 st.markdown("Try refining your question or adjusting the top-k value in the sidebar.")
#     else:
#         st.info("👈 Please upload and process at least one document in the 'Document Upload' tab first.")
#         st.markdown("""
#         <div style="text-align: center; padding: 50px;">
#             <h3>No documents indexed yet</h3>
#             <p>Upload a legal document to start asking questions</p>
#         </div>
#         """, unsafe_allow_html=True)
import streamlit as st
import tempfile
import os

from azure_services.blob import upload_file_to_blob
from azure_services.search import create_or_use_search_index, upload_text_to_search, get_existing_index_fields
from azure_services.text_extraction import extract_text_from_pdf
from azure_services.qa import semantic_qa
#from config import FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_KEY, SEARCH_SERVICE_ENDPOINT, SEARCH_API_KEY, SEARCH_INDEX_NAME

# Page configuration
st.set_page_config(
    page_title="Legal Document QA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar ---
with st.sidebar:
    st.title("⚖️ Legal Document QA")
    
    # About section
    st.markdown("### About")
    st.info("""
    This application allows you to upload legal PDF documents and ask questions about their content.
    
    **Features:**
    - PDF document upload
    - Text extraction using Azure Form Recognizer
    - Document indexing with Azure Cognitive Search
    - AI-powered question answering
    
    **How to use:**
    1. Upload legal PDF documents
    2. Wait for processing to complete
    3. Ask questions about the document content
    """)
    
    # Advanced settings
    st.markdown("### Settings")
    search_top_k = st.slider(
        "Number of documents to retrieve (top-k)",
        min_value=1,
        max_value=10,
        value=5,
        help="Controls how many documents are retrieved during the search phase."
    )
    
    st.markdown("---")
    st.markdown("Powered by Azure Cognitive Services")

# Main content
st.title("⚖️ Legal Document Question Answering")

# Create tabs
tabs = st.tabs(["📄 Document Upload", "🤖 Ask Questions"])

# --- File Upload Section ---
with tabs[0]:
    st.header("Upload Legal PDF Document")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader("Choose PDF file(s)", type=["pdf"], accept_multiple_files=True)

    with col2:
        if "documents" in st.session_state and st.session_state.documents:
            last_doc = st.session_state.documents[-1]
            st.success(f"Most recent document: {last_doc['filename']}")

    if uploaded_files:
        if "documents" not in st.session_state:
            st.session_state.documents = []

        for uploaded_file in uploaded_files:
            if uploaded_file.name in [doc["filename"] for doc in st.session_state.documents]:
                st.info(f"Document '{uploaded_file.name}' already uploaded.")
                continue

            with st.spinner(f"Processing document: {uploaded_file.name}"):
                progress_bar = st.progress(0)

                # Step 1: Save temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    local_path = tmp_file.name
                    filename = uploaded_file.name
                progress_bar.progress(20)

                # Step 2: Upload to Azure Blob Storage
                upload_file_to_blob(local_path, filename)
                progress_bar.progress(40)

                # Step 3: Extract text
                extracted_text = extract_text_from_pdf(local_path)
                progress_bar.progress(60)

                # Step 4: Create search index
                index_name, allowed_fields = create_or_use_search_index()
                progress_bar.progress(80)

                # Step 5: Upload to Azure Search
                upload_text_to_search(filename, extracted_text, index_name, allowed_fields)
                progress_bar.progress(100)

                # Save to session state
                st.session_state.documents.append({
                    "filename": filename,
                    "local_path": local_path,
                    "extracted_text": extracted_text,
                    "index_name": index_name,
                    "allowed_fields": allowed_fields,
                })

                # Show success and metrics
                st.success(f"✅ Document '{filename}' processed successfully!")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Document Size", f"{len(uploaded_file.getvalue())/1024:.1f} KB")
                with col2:
                    st.metric("Extracted Text", f"{len(extracted_text)} characters")

# --- Question Answering Section ---
with tabs[1]:
    st.header("Ask Questions from Your Legal Documents")
    
    if "documents" in st.session_state and st.session_state.documents:
        query = st.text_input("Enter your legal question:", placeholder="Example: What are the main contractual obligations?")
        
        if query:
            with st.spinner("Finding answers..."):
                # Use top-k value
                result = semantic_qa(query, search_top_k=search_top_k)
                
                # Show answer
                st.markdown("### Results")
                answer_container = st.container()
                with answer_container:
                    st.markdown(f"""
                    <div style="padding: 20px; border-radius: 5px; background-color: #f0f2f6;">
                        <h4>Answer:</h4>
                        <p>{result['answer']}</p>
                        <p><strong>Source Document:</strong> {result['filename']}</p>
                        <p><strong>Retrieval Time:</strong> {result['retrieval_time']*1000:.2f} ms</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with st.expander("📄 View source context"):
                    context = result['context']
                    if context:
                        st.markdown(context)
                    else:
                        st.info("No context available for this answer.")

                st.markdown("#### Not what you're looking for?")
                st.markdown("Try refining your question or adjusting the top-k value in the sidebar.")
    else:
        st.info("👈 Please upload and process at least one document in the 'Document Upload' tab first.")
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h3>No documents indexed yet</h3>
            <p>Upload a legal document to start asking questions</p>
        </div>
        """, unsafe_allow_html=True)