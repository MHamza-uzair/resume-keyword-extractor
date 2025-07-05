from io import BytesIO
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import pdfplumber
import spacy
import json
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")
nlp = spacy.load("en_core_web_sm")

with open("skills.json", "r") as f:
    skills_list = json.load(f)["skills"]

# ---------- Extraction Functions ----------


def extract_name_spacy(text):
    """Extract name using spaCy NER, focusing on first few lines"""
    lines = text.split('\n')
    # Check first 5 lines for name
    for line in lines[:5]:
        if line.strip():
            doc = nlp(line)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text

    # Fallback: check entire text
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None


def extract_email(text):
    """Extract email address using regex"""
    email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
    matches = re.findall(email_pattern, text)
    if matches:
        return matches[0]
    return None


def extract_phone(text):
    """Extract phone number using improved regex"""
    # Multiple phone patterns
    phone_patterns = [
        # US format
        r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
        # International
        r'\+?[0-9]{1,3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}',
        r'\([0-9]{3}\)[0-9]{3}-[0-9]{4}',  # (123)456-7890
        r'[0-9]{3}-[0-9]{3}-[0-9]{4}',  # 123-456-7890
        r'[0-9]{10}'  # 1234567890
    ]

    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean up the match
            cleaned = re.sub(r'[^\d+]', '', match)
            if len(cleaned) >= 10:
                return match.strip()
    return None


def extract_experience(text):
    """Extract work experience information"""
    experience_info = []

    # Keywords that indicate experience sections
    experience_keywords = [
        r'experience', r'work experience', r'employment', r'professional experience',
        r'career', r'work history', r'job history'
    ]

    # Split text into lines
    lines = text.split('\n')

    # Find experience section
    experience_section = False
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()

        # Check if this line starts an experience section
        if any(re.search(keyword, line_lower) for keyword in experience_keywords):
            experience_section = True
            continue

        # Stop if we hit another major section
        if experience_section and any(section in line_lower for section in ['education', 'skills', 'projects']):
            break

        # Extract experience entries
        if experience_section and line.strip():
            # Look for job titles, companies, dates
            if re.search(r'(19|20)\d{2}', line) or any(word in line_lower for word in ['manager', 'developer', 'analyst', 'engineer', 'specialist']):
                experience_info.append(line.strip())

    return experience_info if experience_info else None


def extract_linkedin_url(text):
    """Extract LinkedIn URL using improved regex"""
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+'
    matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
    if matches:
        url = matches[0]
        if not url.startswith('http'):
            url = 'https://' + url
        return url
    return None


def extract_github_url(text):
    """Extract GitHub URL using improved regex"""
    github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9-_]+'
    matches = re.findall(github_pattern, text, re.IGNORECASE)
    if matches:
        url = matches[0]
        if not url.startswith('http'):
            url = 'https://' + url
        return url
    return None


def extract_education_details(text):
    """Extract education information"""
    education_info = []

    # Degree keywords
    degree_keywords = [
        r'bachelor', r'bsc', r'bs', r'b\.s\.', r'b\.sc\.', r'ba', r'b\.a\.',
        r'master', r'msc', r'ms', r'm\.s\.', r'm\.sc\.', r'ma', r'm\.a\.',
        r'phd', r'ph\.d\.', r'doctorate', r'doctoral', r'mba', r'm\.b\.a\.',
        r'associate', r'diploma', r'certificate', r'bachelors', r'masters'
    ]

    # University/School keywords
    university_keywords = [
        r'university', r'college', r'institute', r'school', r'academy'
    ]

    lines = text.split('\n')
    education_section = False

    for line in lines:
        line_lower = line.lower().strip()

        # Check if this line starts education section
        if 'education' in line_lower and len(line.strip()) < 50:
            education_section = True
            continue

        # Stop if we hit another major section
        if education_section and any(section in line_lower for section in ['experience', 'skills', 'projects']):
            break

        # Extract education entries
        if (education_section or
            any(re.search(keyword, line_lower) for keyword in degree_keywords) or
                any(re.search(keyword, line_lower) for keyword in university_keywords)):

            if line.strip() and len(line.strip()) > 5:
                # Extract year if present
                year_match = re.search(r'(19|20)\d{2}', line)
                year = year_match.group() if year_match else ""

                education_info.append(line.strip())

    return education_info if education_info else None


def extract_skills(text):
    """Extract skills from text"""
    text_lower = text.lower()
    found_skills = []

    for skill in skills_list:
        if skill.lower() in text_lower:
            found_skills.append(skill.title())

    return found_skills if found_skills else None


def extract_all_info(text):
    """Extract all information from resume text"""
    extracted_info = {
        'name': extract_name_spacy(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'experience': extract_experience(text),
        'linkedin': extract_linkedin_url(text),
        'github': extract_github_url(text),
        'education': extract_education_details(text),
        'skills': extract_skills(text)
    }
    return extracted_info

# ---------- Routes ----------


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(None),
    pasted_text: str = Form(None)
):
    text = ""

    if pasted_text:
        text = pasted_text
    elif file:
        if file.filename.endswith(".txt"):
            text = (await file.read()).decode("utf-8")
        elif file.filename.endswith(".pdf"):
            try:
                with pdfplumber.open(BytesIO(await file.read())) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                text = f"Error processing PDF: {str(e)}"
        else:
            text = "Unsupported file type. Please upload .txt or .pdf files."
    else:
        text = "No input provided."

    # Extract all information
    if text and "Error" not in text and "Unsupported" not in text:
        extracted_info = extract_all_info(text)
    else:
        extracted_info = {}

    return templates.TemplateResponse("result.html", {
        "request": request,
        "text": text,
        "extracted_info": extracted_info
    })
