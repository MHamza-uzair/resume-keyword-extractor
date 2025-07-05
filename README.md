Resume Information Extractor
A web-based application built with FastAPI that extracts key information from resumes in PDF or text format using Natural Language Processing (NLP) and regex patterns.
🚀 Features

Multi-format Support: Upload PDF files or paste text directly
Comprehensive Extraction: Extracts the following information:

 Name
 Email Address
 Phone Number
 Work Experience
 LinkedIn Profile
 GitHub Profile
 Education Details
 Technical Skills


Clean Web Interface: User-friendly design with responsive layout
Real-time Processing: Instant extraction and display of results

🛠️ Technologies Used

Backend: FastAPI (Python)
NLP: spaCy for Named Entity Recognition
PDF Processing: pdfplumber for PDF text extraction
Frontend: HTML, CSS, Jinja2 Templates
Text Processing: Regular expressions (regex) for pattern matching

📦 Installation
Prerequisites

Python 3.8 or higher
pip package manager

Setup Instructions

Clone the repository

bashgit clone https://github.com/yourusername/resume-extractor.git
cd resume-extractor

Install required packages

bashpip install fastapi uvicorn pdfplumber spacy python-multipart jinja2

Download spaCy language model

bashpython -m spacy download en_core_web_sm

Run the application

bashuvicorn app:app --reload

Access the application

Open your browser and navigate to http://127.0.0.1:8000



📁 Project Structure
resume-extractor/
├── app.py                 # Main FastAPI application
├── skills.json           # List of technical skills for extraction
├── templates/
│   ├── index.html        # Home page template
│   ├── result.html       # Results page template
│   ├── index.css         # Styling for home page
│   └── result.css        # Styling for results page
├── README.md             # Project documentation
└── requirements.txt      # Python dependencies
How It Works

Upload or Paste: Users can either upload a PDF resume or paste text directly
Text Extraction: The application extracts text from PDFs using pdfplumber
Information Processing: Uses a combination of:

spaCy NLP for name extraction
Regex patterns for email, phone, and URLs
Keyword matching for skills and experience
Section-based parsing for education and experience


Results Display: Extracted information is displayed in a clean, organized format
