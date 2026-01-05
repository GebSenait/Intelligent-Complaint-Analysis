# Intelligent Complaint Analysis Platform

**Client:** CrediTrust Financial  
**Project:** RAG-Powered Complaint Analysis System  
**Status:** Task 3 - RAG Pipeline & Evaluation (Completed)

---

## Project Overview

This project implements an Intelligent Complaint Analysis platform powered by Retrieval-Augmented Generation (RAG) for CrediTrust Financial, a fast-growing digital finance company operating in East Africa with over 500,000 users.

### Business Objective

Enable internal teams (Product, Compliance, Executive) to:
- Ask plain-English questions about customer complaints
- Retrieve semantically relevant complaint narratives
- Generate concise, evidence-backed insights in seconds

### Technical Architecture

1. **Task 1**: EDA and Data Preprocessing (Current)
2. **Task 2**: Embedding Generation and Vector Database Setup
3. **Task 3**: RAG Pipeline Implementation
4. **Task 4**: Query Interface and Evaluation
5. **Task 5**: Model Training and Tracking

---

## Project Structure

```
Intelligent-Complaint-Analysis/
├── .vscode/
│   └── settings.json                    # VS Code workspace settings
├── .github/
│   └── workflows/
│       └── unittests.yml                # CI/CD unit tests workflow
├── data/
│   ├── raw/                             # Raw data files (excluded from git)
│   │   └── .gitkeep
│   └── processed/                       # Processed/cleaned data files
│       └── .gitkeep
├── vector_store/                         # Persisted FAISS/ChromaDB index
│   └── .gitkeep
├── notebooks/
│   ├── __init__.py
│   ├── README.md                        # Notebooks documentation
│   ├── task-1-eda-preprocessing.ipynb  # Task 1: EDA and preprocessing
│   └── task-2-embeddings-vectorstore.ipynb  # Task 2: Embeddings & vector indexing
├── src/
│   ├── __init__.py                      # Source code (Tasks 2-5)
│   ├── vector_store_loader.py          # Task 3: Vector store loader
│   ├── retriever.py                     # Task 3: Semantic retriever
│   ├── prompt_template.py               # Task 3: Prompt engineering
│   ├── generator.py                     # Task 3: LLM generator
│   ├── rag_pipeline.py                  # Task 3: RAG orchestrator
│   ├── evaluation.py                    # Task 3: Evaluation framework
│   └── run_evaluation.py                # Task 3: Evaluation script
├── tests/
│   └── __init__.py                      # Unit and integration tests
├── docs/
│   ├── eda-summary.md                   # EDA findings and recommendations
│   └── task-3-evaluation-results.md    # Task 3: RAG evaluation results
├── app.py                                # Gradio/Streamlit interface (Task 4)
├── requirements.txt                     # Python dependencies
├── README.md                            # This file
└── .gitignore                           # Git ignore rules
```

### Directory Descriptions

- **`.vscode/`**: VS Code workspace configuration for consistent development environment
- **`.github/workflows/`**: GitHub Actions workflows for CI/CD
- **`data/raw/`**: Raw data files (CFPB dataset downloads, etc.) - excluded from git
- **`data/processed/`**: Cleaned and processed datasets ready for RAG system
- **`vector_store/`**: Persisted vector database indices (FAISS/ChromaDB) for embeddings
- **`notebooks/`**: Jupyter notebooks for exploratory analysis and task-specific work
- **`src/`**: Source code modules for RAG pipeline, embedding generation, retrieval, etc.
- **`tests/`**: Unit tests, integration tests, and test utilities
- **`docs/`**: Project documentation, summaries, and reports
- **`app.py`**: User interface for querying the RAG system (Gradio/Streamlit)

---

## Table of Contents

- [Task 1 – EDA and Data Preprocessing](#task-1-eda-and-data-preprocessing)
- [Task 2 – Text Chunking, Embeddings & Vector Indexing](#task-2-text-chunking-embeddings--vector-indexing)
- [Task 3 – RAG Pipeline & Evaluation](#task-3-rag-pipeline--evaluation)
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

## Next Steps

After completing Task 3:

1. **Task 4**: Build query interface (Gradio/Streamlit) and production evaluation framework
2. **Task 5**: Model training and tracking

---

## Contact and Support

For questions or issues related to this project, please contact the project team.

---

**Last Updated**: 2024  
**Version**: 1.0.0

