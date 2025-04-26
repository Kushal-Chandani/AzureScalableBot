# AzureNexus: AI-Powered Legal Knowledge Bot
## Team Members: 
- #### Rania Siddiqui
- #### Kushal Chandani
## 🚀 Project Overview: 

AzureNexus is a scalable AI-powered knowledge bot designed to streamline legal research and document analysis. By leveraging Azure Cognitive Services, our system enables legal professionals to efficiently retrieve insights from vast volumes of legal texts through semantic search, document parsing, and precise Q&A functionalities.

## 📌 Key Features
-  ⚖ Legal Document Search & Insights – Instantly retrieve relevant legal clauses, case laws, and regulatory information.
- 🧠 AI-Powered Q&A – Ask legal questions in natural language and receive precise, context-aware answers.
- 🔍 Azure Cognitive Search – Advanced indexing and semantic search for enhanced document retrieval.
- ⏳ Fast & Scalable – Optimized for efficiency, with target response times under 5 seconds for documents up to 50 pages.
## 🏗 Architecture & Technology Stack
- Backend: Azure Cognitive Search, Huggingface Models, Azure Functions
- Storage: Azure Blob Storage (for legal documents)
- AI Models: Azure Form Recognizer (OCR), Cognitive Search, Hugging Face models
- Frontend: Chatbot-based interface for user interaction
## 📚 Supported Legal Data Sources
Our bot processes publicly available legal documents from Pakistani regulations which has different documents
## 📊 Performance Goals
- Response Time: < 5 seconds for 50-page documents
- Handling Large Documents: Supports 500+ page PDFs via document chunking & OCR processing
## 🎯 Use Case Example
- Query: "What is the termination notice period in this contract?"
- Bot Response: "The contract requires a 30-day written notice for termination."

## Legal and Regulatory Resources

- **Pakistani Regulations**: [pakistancode.gov.pk](https://pakistancode.gov.pk)  
  Includes downloadable PDFs.
- **U.S. Code and Related Documents**: [govinfo.gov](https://www.govinfo.gov)  
  Example: Title 18 of the U.S. Code, includes downloadable PDFs.
- **UK Statutes**: [legislation.gov.uk](https://www.legislation.gov.uk)
- **European Court of Human Rights Cases**: [hudoc.echr.coe.int](https://hudoc.echr.coe.int)
- **German Court Decisions** (JSON format): [openlegaldata.io](https://openlegaldata.io)
- **International Court of Justice**: [icj-cij.org](https://www.icj-cij.org/list-of-all-cases)
