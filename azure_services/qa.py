# #from config import SEARCH_SERVICE_ENDPOINT, SEARCH_INDEX_NAME, SEARCH_API_KEY
# from azure.core.credentials import AzureKeyCredential
# from azure.search.documents import SearchClient
# from transformers import pipeline


# qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2", revision="main", use_auth_token=False)


# def semantic_qa(query, search_top_k=5, model_top_k=1):
#     search_client = SearchClient(
#         endpoint=SEARCH_SERVICE_ENDPOINT,
#         index_name=SEARCH_INDEX_NAME,
#         credential=AzureKeyCredential(SEARCH_API_KEY)
#     )

#     results = search_client.search(search_text=query, top=search_top_k)
#     relevant_chunks = [result['content'] for result in results]

#     answers = []
#     for chunk in relevant_chunks:
#         try:
#             result = qa_pipeline(question=query, context=chunk)
#             if result['score'] > 0.1:
#                 result['source_context'] = chunk
#                 answers.append(result)
#         except Exception as e:
#             print(f"Error: {e}")

#     if not answers:
#         return {"answer": "❌ No confident answer found.", "context": ""}

#     top_answers = sorted(answers, key=lambda x: x['score'], reverse=True)[:model_top_k]

#     for i, ans in enumerate(top_answers):
#         print(f"\n🧠 Answer {i+1}: {ans['answer']}")
#         print(f"📄 Context: {ans['source_context'][:300]}...")

#     # Return a dictionary with both answer and context
#     return {
#         "answer": top_answers[0]['answer'],
#         "context": top_answers[0]['source_context']
#     }

# qa.py
import time
#from config import SEARCH_SERVICE_ENDPOINT, SEARCH_INDEX_NAME, SEARCH_API_KEY
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from transformers import pipeline

qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2", revision="main", use_auth_token=False)

def semantic_qa(query, search_top_k=5, model_top_k=1):
    search_client = SearchClient(
        endpoint=SEARCH_SERVICE_ENDPOINT,
        index_name=SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_API_KEY)
    )

    # Measure retrieval time with higher precision
    start_time = time.perf_counter()
    results = search_client.search(search_text=query, top=search_top_k)
    # Iterate over results to include in timing
    relevant_chunks = []
    filenames = []
    for result in results:
        relevant_chunks.append(result['content'])
        filenames.append(result['filename'])
    retrieval_time = time.perf_counter() - start_time

    answers = []
    for i, chunk in enumerate(relevant_chunks):
        try:
            result = qa_pipeline(question=query, context=chunk)
            if result['score'] > 0.1:
                result['source_context'] = chunk
                result['filename'] = filenames[i]  # Associate filename with answer
                answers.append(result)
        except Exception as e:
            print(f"Error: {e}")

    if not answers:
        return {
            "answer": "❌ No confident answer found.",
            "context": "",
            "filename": "",
            "retrieval_time": retrieval_time
        }

    top_answers = sorted(answers, key=lambda x: x['score'], reverse=True)[:model_top_k]

    for i, ans in enumerate(top_answers):
        print(f"\n🧠 Answer {i+1}: {ans['answer']}")
        print(f"📄 Context: {ans['source_context'][:300]}...")

    # Return a dictionary with answer, context, filename, and retrieval time
    return {
        "answer": top_answers[0]['answer'],
        "context": top_answers[0]['source_context'],
        "filename": top_answers[0]['filename'],
        "retrieval_time": retrieval_time
    }