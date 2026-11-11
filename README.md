# ARGUS

AI-Powered Document Intelligence & Investigation Platform.

## Overview
ARGUS is a full-stack document processing platform. It allows users to upload documents (PDF, DOCX, TXT, Images), automatically extract text using OCR (Tesseract), identify entities (dates, amounts, emails, organizations) using deterministic Regex engines, and compare documents to detect discrepancies.

## Technology Stack
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic, Celery, Redis
- **Frontend:** React, TypeScript, Tailwind CSS, React Query
- **Document Processing:** PyMuPDF, python-docx, pytesseract, Pillow, fpdf2
- **Database:** PostgreSQL (with Full-Text Search)
- **Infrastructure:** Docker, Docker Compose

## Key Features
- **Document Ingestion:** Supports PDF, DOCX, TXT, PNG, JPG with SHA-256 duplicate detection.
- **Intelligent Extraction:** Background Celery workers extract text and OCR images.
- **Entity Recognition:** Automatically identifies monetary amounts, dates, and organizations.
- **Document Comparison:** Detects discrepancies between two documents.
- **Intelligent Search:** PostgreSQL Full-Text Search with keyword highlighting.
- **Investigations:** Workspace to group documents, add notes, and track findings.
- **Report Generation:** Export investigations as formatted PDF or JSON files.

## Getting Started

### Prerequisites
Docker Desktop installed and running.

### Installation
1. Clone the repository: git clone https://github.com/Adijah6838/argus.git
2. Setup env: cp .env.example .env
3. Start cluster: docker compose up -d --build
4. Run migrations: docker compose exec api alembic upgrade head

### Access
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs
