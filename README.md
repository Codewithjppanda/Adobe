Looking at the GitHub repository image showing both Round 1A and Round 1B challenges in a single repository, here's a short README.md for the main repository page:

# Adobe India Hackathon 2025 - Document Intelligence Solutions

## 🎯 Challenge Theme: "Connecting the Dots Through Docs"

This repository contains our complete solutions for Adobe India Hackathon 2025, focusing on intelligent document processing and analysis.

## 📁 Repository Structure

```
Adobe-Hackathon-2025/
├── Challenge_1a/                    # PDF Outline Extraction
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── process_pdfs.py
│   └── README.md
├── Challenge_1b/                    # Persona-Driven Document Intelligence  
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── process_challenge1b.py
│   ├── persona_analyzer.py
│   ├── approach_explanation.md
│   └── README.md
└── README.md                    # This file
```

## 🚀 Solutions Overview

### Round 1A: PDF Outline Extraction
**"Understand Your Document"**

- **Objective**: Extract structured outlines (Title + H1/H2/H3 headings) from PDF documents
- **Approach**: Font-based analysis using pdfminer.six for heading detection
- **Performance**: ≤10 seconds for 50-page PDFs
- **Architecture**: CPU-only, AMD64 compatible, offline processing

**Key Features:**
- ✅ Sophisticated font analysis for accurate heading detection
- ✅ Document type adaptation (research papers, business docs, technical manuals)
- ✅ Hierarchical structure enforcement (proper H1→H2→H3 flow)
- ✅ Error-resilient processing with graceful fallbacks

### Round 1B: Persona-Driven Document Intelligence
**"Connect What Matters — For the User Who Matters"**

- **Objective**: Extract and prioritize relevant sections based on user persona and job-to-be-done
- **Approach**: Font-based structure analysis + persona-driven relevance scoring
- **Performance**: ≤60 seconds for 3-5 document collections
- **Architecture**: Generic, domain-agnostic solution for any document type

**Key Features:**
- ✅ Works across research papers, business reports, educational content
- ✅ Adaptive relevance scoring for diverse personas (researchers, analysts, students)
- ✅ Intelligent section selection with document diversity
- ✅ High-quality subsection analysis and ranking
