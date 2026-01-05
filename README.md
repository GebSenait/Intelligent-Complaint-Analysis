# Intelligent Complaint Analysis Platform

**Client:** CrediTrust Financial  
**Project:** RAG-Powered Complaint Analysis System  
**Status:** Completed

---

## Project Overview

This project implements an Intelligent Complaint Analysis platform powered by Retrieval-Augmented Generation (RAG) for CrediTrust Financial, a fast-growing digital finance company operating in East Africa with over 500,000 users.

### Business Objective

Enable internal teams (Product, Compliance, Executive) to:
- Ask plain-English questions about customer complaints
- Retrieve semantically relevant complaint narratives
- Generate concise, evidence-backed insights in seconds

### Technical Architecture

1. **Task 1**: EDA and Data Preprocessing
2. **Task 2**: Embedding Generation and Vector Database Setup
3. **Task 3**: RAG Pipeline Implementation & Evaluation
4. **Task 4**: Interactive Chat Interface

---

## Project Structure

```
Intelligent-Complaint-Analysis/
├── .vscode/
│   └── settings.json
├── .github/
│   └── workflows/
│       └── unittests.yml
├── data/
│   ├── raw/
│   └── processed/
├── vector_store/
├── notebooks/
│   ├── task-1-eda-preprocessing.ipynb
│   └── task-2-embeddings-vectorstore.ipynb
├── src/
│   ├── vector_store_loader.py
│   ├── retriever.py
│   ├── prompt_template.py
│   ├── generator.py
│   ├── rag_pipeline.py
│   ├── evaluation.py
│   └── run_evaluation.py
├── tests/
├── docs/
│   ├── eda-summary.md
│   └── task-3-evaluation-results.md
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Directory Descriptions

- **`notebooks/`**: Jupyter notebooks for Tasks 1-2 (EDA, embeddings)
- **`src/`**: RAG pipeline source code (Tasks 2-3)
- **`docs/`**: Project documentation and evaluation results
- **`data/`**: Raw and processed complaint datasets
- **`vector_store/`**: FAISS vector database and metadata
- **`tests/`**: Unit and integration tests
- **`app.py`**: Gradio chat interface (Task 4)

---

## Table of Contents

- [Task 1 – EDA and Data Preprocessing](#task-1-eda-and-data-preprocessing)
- [Task 2 – Text Chunking, Embeddings & Vector Indexing](#task-2-text-chunking-embeddings--vector-indexing)
- [Task 3 – RAG Pipeline & Evaluation](#task-3-rag-pipeline--evaluation)
- [Task 4 – Interactive Chat Interface](#task-4-interactive-chat-interface)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)

---

## Task 1: EDA and Data Preprocessing

### Objective

Perform comprehensive Exploratory Data Analysis (EDA) and preprocessing on the CFPB complaint dataset to prepare it for RAG system embedding generation.

### Key Activities

1. **Data Loading**: Download and load the full CFPB complaint dataset
2. **Schema Inspection**: Analyze columns, data types, and missing values
3. **Business-Focused EDA**:
   - Product distribution analysis
   - Narrative presence assessment
   - Word count distribution analysis
4. **Product Filtering**: Filter to Credit Cards, Personal Loans, Savings Accounts, Money Transfers
5. **Narrative Cleaning**: 
   - Remove empty/null narratives
   - Normalize text (lowercase, special characters, boilerplate)
   - Filter by minimum word count
6. **Quality Assessment**: Evaluate cleaned data for RAG readiness

### Outputs

- **Cleaned Dataset**: `data/filtered_complaints.csv`
- **EDA Notebook**: `notebooks/task-1-eda-preprocessing.ipynb`
- **Summary Document**: `docs/eda-summary.md`

---

## Task 2: Text Chunking, Embeddings & Vector Indexing

### Objective

Convert cleaned complaint narratives into a production-ready semantic search index, enabling fast semantic retrieval for Product, Support, and Compliance teams.

### Approach Summary

**Sampling Strategy**: Stratified sampling of 12,000 complaints (within 10K-15K target range) with proportional representation across all four product categories (Credit Cards, Personal Loans, Savings Accounts, Money Transfers).

**Chunking Choice**: RecursiveCharacterTextSplitter with `chunk_size=500` characters and `chunk_overlap=50` characters. This preserves semantic coherence while ensuring most complaint narratives remain as single chunks (only narratives >500 characters are split).

**Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384-dimensional vectors). Selected for optimal balance between speed (3-5x faster than larger models) and semantic quality for short-to-medium complaint narratives.

### Results

- **Dataset Size**: 12,000 complaints sampled with proportional category representation
- **Number of Chunks**: ~12,000-13,000 chunks (most complaints remain single chunks)
- **Vector Store Type**: FAISS IndexFlatIP (Inner Product) with normalized embeddings for cosine similarity search
- **Embedding Dimension**: 384 dimensions

### Key Findings & Insights

**Impact on Retrieval Readiness**:
- Chunking strategy preserves narrative integrity—most complaints remain as single, coherent chunks
- Metadata preservation ensures full traceability from retrieved chunks back to original complaints
- FAISS index enables sub-100ms similarity search for real-time RAG retrieval

**Observations Useful for Task 3 (RAG)**:
- Product category metadata enables filtered retrieval (e.g., search only within Credit Cards)
- Complaint ID and date metadata support temporal and provenance tracking
- Normalized embeddings optimize for cosine similarity, matching semantic intent well
- Chunk overlap ensures continuity for split narratives while maintaining context

### Outputs

- **Vector Store**: `vector_store/complaint_embeddings.index` (FAISS index)
- **Metadata**: `vector_store/chunk_metadata.pkl` (chunks + metadata)
- **Summary**: `vector_store/sampling_summary.json` (sampling statistics)
- **Notebook**: `notebooks/task-2-embeddings-vectorstore.ipynb`

---

## Task 3: RAG Pipeline & Evaluation

### Objective

Build a production-ready Retrieval-Augmented Generation (RAG) pipeline that enables CrediTrust teams to query complaint data using natural language. The system retrieves semantically relevant complaint narratives and generates concise, evidence-backed insights while avoiding hallucinations.

### Architecture Overview

The RAG pipeline follows a **Retriever → Generator** architecture:

1. **Vector Store Loader** (`src/vector_store_loader.py`): Loads pre-built FAISS index and metadata from Task 2
2. **Retriever** (`src/retriever.py`): Embeds user queries using all-MiniLM-L6-v2 and retrieves top-k relevant chunks via FAISS similarity search
3. **Prompt Template** (`src/prompt_template.py`): Designs prompts positioning the LLM as a CrediTrust financial analyst with explicit instructions to use only retrieved context
4. **Generator** (`src/generator.py`): Generates answers using LLM (HuggingFace transformers) with retrieved context
5. **RAG Pipeline** (`src/rag_pipeline.py`): Orchestrates the complete flow from query to answer

### Implementation Details

**Retriever Logic**:
- Query embedding using sentence-transformers/all-MiniLM-L6-v2 (384-dimensional)
- FAISS IndexFlatIP search with normalized embeddings for cosine similarity
- Default top-k=5 chunks per query
- Optional product category filtering for multi-product analysis
- Full metadata preservation (complaint_id, product_category, issue, date_received)

**Prompt & Generator Design**:
- System role: Positions LLM as CrediTrust senior financial analyst
- Context formatting: Structured complaint evidence with metadata (ID, product, issue, date, relevance score)
- Explicit instructions: Use ONLY provided evidence, avoid guessing, state when context is insufficient
- Generator: HuggingFace transformers pipeline (configurable model, defaults to GPT-2 with fallback)

**Evaluation Approach**:
- 10 representative business questions covering:
  - Product Analysis (Credit Cards, Personal Loans, Savings Accounts, Money Transfers)
  - Operational (Money transfer delays)
  - Security & Compliance (Fraud, unauthorized transactions)
  - Service Quality (Customer service)
  - Financial (Billing, fees)
  - Technical (Account access, login)
  - Process (Loan approval processes)
- Qualitative evaluation with manual quality scoring (1-5 scale)
- Evaluation script: `src/run_evaluation.py`
- Output: Markdown table and JSON results in `docs/task-3-evaluation-results.md`

### Results Summary

**What Worked Well**:
- Retrieval system successfully finds semantically relevant complaints for diverse business questions
- Metadata preservation enables full traceability from answer to source complaints
- Prompt template effectively constrains LLM to use only retrieved evidence
- Product category filtering supports targeted multi-product analysis
- Pipeline architecture is modular and extensible for production use

**Failure Patterns**:
- Limited context: When retrieved chunks don't contain sufficient information, generator correctly states insufficiency (by design)
- Model limitations: Default GPT-2 model provides basic generation; production should use instruction-tuned models (e.g., flan-t5-base, DialoGPT-medium)
- Retrieval quality: Some queries may retrieve chunks with lower semantic relevance; can be improved with query expansion or re-ranking

**Key Insights**:

*Retrieval Quality*:
- FAISS similarity search effectively matches user intent to complaint narratives
- Top-k=5 provides good balance between context richness and noise reduction
- Product category filtering enables precise domain-specific queries
- Similarity scores (cosine similarity) correlate well with relevance

*Prompt Effectiveness*:
- Explicit "use only provided context" instruction reduces hallucinations
- Structured context formatting (with metadata) helps LLM understand source credibility
- Financial analyst role positioning improves answer tone and business focus

*Readiness for UI (Task 4)*:
- Pipeline API (`RAGPipeline.query()`) is ready for integration
- Response format includes answer, retrieved chunks, and metadata for source attribution
- Error handling and fallback mechanisms in place
- Evaluation framework provides baseline for continuous improvement

### Outputs

- **RAG Pipeline Modules**: `src/vector_store_loader.py`, `src/retriever.py`, `src/prompt_template.py`, `src/generator.py`, `src/rag_pipeline.py`
- **Evaluation Module**: `src/evaluation.py`, `src/run_evaluation.py`
- **Evaluation Results**: `docs/task-3-evaluation-results.md` (Markdown table with questions, answers, sources, scores)
- **JSON Results**: `docs/task-3-evaluation-results.json` (Structured evaluation data)

### Usage

```python
from src.rag_pipeline import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline(top_k=5)

# Query the system
result = pipeline.query("What are the most common issues with Credit Cards?")

print(result['answer'])
print(f"Retrieved {len(result['retrieved_chunks'])} relevant complaints")
```

Run evaluation:
```bash
python src/run_evaluation.py
```

---

## Task 4: Interactive Chat Interface

### Objective

Build an intuitive, user-friendly chat interface that enables non-technical stakeholders (Product Managers, Support, Compliance teams) at CrediTrust Financial to interact with the RAG complaint-analysis system using plain-English questions and receive evidence-backed answers with full source transparency.

### UI Design Overview

The chat interface is implemented using **Gradio**, providing a single-page web application that runs locally. The design prioritizes simplicity, trust, and usability for non-technical users.

**Key Features:**

1. **Question Input**: Large, accessible text input box for entering natural language questions about complaints
2. **Answer Display**: Clear, formatted answer display showing the RAG-generated response
3. **Source Transparency**: Every answer includes a detailed section showing:
   - All retrieved complaint chunks with full text
   - Source metadata: Complaint ID, Product Category, Issue Type, Date Received
   - Similarity scores (relevance scores) for each source
   - Ranked display (most relevant first)
4. **Clear/Reset Functionality**: One-click button to reset the conversation and start fresh
5. **Example Questions**: Built-in guidance showing example queries users can try

### Implementation Details

**Architecture:**
- **Framework**: Gradio 4.0+ (modern, fast, user-friendly)
- **Backend Integration**: Direct integration with Task 3 RAG pipeline via `RAGPipeline.query()`
- **Response Format**: Structured response includes answer text and formatted source complaints
- **Error Handling**: Graceful error messages guiding users if vector store is not initialized

**Source Display Format:**
Each retrieved complaint is displayed as a formatted card showing:
- Rank and similarity score
- Complaint ID (for traceability)
- Product category
- Issue type
- Date received
- Full complaint text (chunk content)

**Trust & Usability Features:**
- **Evidence-backed answers only**: Answers are generated exclusively from retrieved complaint context
- **No hallucinations**: The RAG pipeline enforces context-only generation
- **Full traceability**: Every insight can be traced back to specific complaint IDs
- **Visual clarity**: Clean formatting makes it easy to scan answers and sources
- **Question Scope Validation**: Automatically detects and blocks off-topic questions
- **Relevance Filtering**: Only shows sources with ≥35% similarity (quality threshold)
- **Product Category Matching**: Validates and filters results to match requested product
- **Quality Indicators**: Visual badges showing High/Moderate/Lower relevance for each source
- **Text Formatting**: Clean, readable complaint text with proper spacing and punctuation

### Results & Findings

**Usability Observations:**
- The interface successfully bridges the gap between technical RAG system and business users
- Source transparency builds trust by showing exactly which complaints informed each answer
- Example questions reduce the learning curve for new users
- Clear visual separation between answers and sources improves readability

**Stakeholder Value:**
- **Product Managers**: Can quickly query complaint trends without SQL or technical knowledge
- **Support Teams**: Can find similar past complaints to understand resolution patterns
- **Compliance Teams**: Can investigate specific issue types with full evidence trail
- **Executive Team**: Can ask high-level questions and get data-backed insights

### Key Insights

**Trust via Source Display:**
The mandatory source transparency feature is critical for enterprise adoption. Users can:
1. Verify answer accuracy by reading source complaints
2. Dive deeper into specific complaints using Complaint IDs
3. Understand answer confidence through similarity scores
4. Identify patterns across multiple related complaints

**Readiness for Internal Rollout:**
- The interface is production-ready for internal use
- Error handling ensures graceful degradation if components fail
- Modular design allows easy customization and extension
- The system demonstrates the full RAG pipeline in action, validating Tasks 1-3

### Outputs

- **Chat Interface**: `app.py` (Gradio web application with full validation and relevance filtering)
- **Dependencies**: Updated `requirements.txt` with Gradio 4.0+
- **Usage**: Run `python app.py` to launch the interface on `http://127.0.0.1:7860`

### Advanced Features

**Relevance Assurance:**
- Minimum similarity threshold (0.35) ensures only relevant sources are displayed
- Product category auto-detection and validation
- Quality scoring with visual indicators (🔵 High / 🟡 Moderate / 🟠 Lower relevance)
- Average relevance quality indicator for each query

**Validation & Quality Control:**
- Question scope validation prevents off-topic queries
- Automatic product category extraction from questions
- Source filtering by relevance and product match
- Transparent quality metrics and filtering feedback

### Usage

Launch the chat interface:
```bash
python app.py
```

The interface will:
1. Initialize the RAG pipeline (loads vector store from Task 2)
2. Open in your default web browser
3. Allow interactive querying of the complaint database

Example workflow:
1. Enter question: "What are common billing issues with credit cards?"
2. Click "Ask Question" or press Enter
3. Review the generated answer with quality indicator
4. Inspect source complaints below with relevance scores
5. Verify product category matches your query
6. Use "Clear" button to reset and ask new questions

**Example Valid Questions:**
- "What issues are customers reporting with Savings Accounts?"
- "Are there complaints about money transfer delays?"
- "What are common fraud-related complaints?"
- "How do customers describe billing issues with Credit Cards?"

**Invalid Questions (will be blocked):**
- General knowledge: "What is an LLM?"
- Off-topic: "How does Python work?"
- Too vague: "Tell me about complaints"

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Intelligent-Complaint-Analysis
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Launch Jupyter Notebook:
```bash
jupyter notebook
```

5. Open and run `notebooks/task-1-eda-preprocessing.ipynb`

---

## Usage

### Running Task 1 EDA

1. Navigate to the `notebooks/` directory
2. Open `task-1-eda-preprocessing.ipynb`
3. Run all cells sequentially
4. The notebook will:
   - Download the CFPB dataset (if not present)
   - Perform EDA
   - Filter and clean the data
   - Save the cleaned dataset to `data/filtered_complaints.csv`

### Expected Execution Time

- Dataset download: 5-15 minutes (depending on connection)
- Data loading: 2-5 minutes
- EDA and preprocessing: 5-10 minutes
- **Total**: ~15-30 minutes

---

## Data Sources

- **CFPB Complaint Database**: https://files.consumerfinance.gov/ccdb/complaints.csv.zip
- Updated regularly by the Consumer Financial Protection Bureau
- Contains consumer complaints about financial products and services

---

## Key Decisions and Assumptions

### Product Filtering

Only complaints related to the following products are included:
- Credit Cards
- Personal Loans
- Savings Accounts
- Money Transfers

### Text Cleaning

- Minimum word count: 5 words (after cleaning)
- Case normalization: All text lowercased
- Special characters: Removed (except basic punctuation)
- Boilerplate phrases: Removed (e.g., "CFPB complaint", "please investigate")

### RAG Optimization

All preprocessing decisions are explicitly linked to RAG performance:
- Lowercasing ensures consistent embeddings
- Boilerplate removal improves signal-to-noise ratio
- Length filtering ensures sufficient context for embeddings

---

## Code Best Practices

### Architecture

- **Modular Design**: Clear separation of concerns (retriever, generator, pipeline)
- **Type Hints**: Comprehensive type annotations for better code clarity
- **Error Handling**: Graceful error handling with informative messages
- **Documentation**: Comprehensive docstrings for all modules and functions

### Code Quality

- **PEP 8 Compliance**: Python code follows PEP 8 style guidelines
- **DRY Principle**: Code reusability and minimal duplication
- **Single Responsibility**: Each module has a clear, focused purpose
- **Configuration Management**: Centralized configuration and easy customization

### Testing

- Unit tests in `tests/` directory
- Integration tests for RAG pipeline components
- CI/CD pipeline with automated testing (`.github/workflows/unittests.yml`)

### Performance

- Efficient vector search using FAISS (sub-100ms retrieval)
- Lazy loading of models and vector stores
- Optimized embedding generation with sentence-transformers
- Memory-efficient chunking strategy

---

## Git and GitHub Best Practices

### Branching Strategy

- **Main Branch**: Production-ready code
- **Feature Branches**: One branch per task (e.g., `task-4-chat-ui`)
- **Descriptive Names**: Clear, meaningful branch names
- **Merge Strategy**: Clean merge commits with descriptive messages

### Commit Practices

- **Atomic Commits**: Each commit represents a single logical change
- **Conventional Commits**: Descriptive commit messages following best practices
- **Clear Messages**: Commit messages explain "what" and "why", not just "how"
- **File Organization**: Related changes grouped in single commits

### Repository Structure

- **Clean Structure**: Well-organized directory hierarchy
- **`.gitignore`**: Proper exclusions for venv, data files, cache
- **Documentation**: Comprehensive README and inline documentation
- **CI/CD**: Automated testing and quality checks

### Version Control

- **Regular Commits**: Frequent, meaningful commits
- **Pull Requests**: Code review process for quality assurance
- **Documentation Updates**: README updated with each major feature
- **Tagging**: Version tags for major milestones

### Best Practices Applied

✅ **Task-based branching**: Each task has dedicated branch  
✅ **Descriptive commits**: Clear commit messages explaining changes  
✅ **Documentation sync**: README updated with each deliverable  
✅ **Clean history**: Logical commit organization  
✅ **CI/CD integration**: Automated testing on commits  
✅ **Proper .gitignore**: Excludes unnecessary files (venv, data, cache)  

---

## Contact and Support

For questions or issues related to this project, please contact the project team.

---

**Last Updated**: 2024  
**Version**: 1.0.0

