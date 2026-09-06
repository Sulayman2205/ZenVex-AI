import re


# ==========================================
# SKILL DATABASE
# ==========================================

SKILLS = {
    "Python": [
        "python"
    ],

    "Java": [
        "java"
    ],

    "C++": [
        "c++",
        "cpp"
    ],

    "JavaScript": [
        "javascript",
        "js"
    ],

    "HTML": [
        "html"
    ],

    "CSS": [
        "css"
    ],

    "React": [
        "react",
        "react.js"
    ],

    "Node.js": [
        "node.js",
        "nodejs"
    ],

    "Flask": [
        "flask"
    ],

    "Django": [
        "django"
    ],

    "SQL": [
        "sql",
        "mysql",
        "postgresql",
        "postgres"
    ],

    "MongoDB": [
        "mongodb",
        "mongo"
    ],

    "Machine Learning": [
        "machine learning",
        "machine-learning"
    ],

    "Deep Learning": [
        "deep learning"
    ],

    "Artificial Intelligence": [
        "artificial intelligence",
        "ai"
    ],

    "Data Science": [
        "data science",
        "data analysis"
    ],

    "TensorFlow": [
        "tensorflow"
    ],

    "PyTorch": [
        "pytorch"
    ],

    "Git": [
        "git",
        "github"
    ],

    "Docker": [
        "docker"
    ],

    "REST API": [
        "rest api",
        "restful api",
        "api development"
    ],

    "AWS": [
        "aws",
        "amazon web services"
    ],

    "Azure": [
        "azure"
    ],

    "Linux": [
        "linux"
    ]
}


# ==========================================
# JOB ROLES
# ==========================================

JOB_ROLES = {

    "Python Developer": [
        "python",
        "flask",
        "django",
        "sql"
    ],

    "Web Developer": [
        "html",
        "css",
        "javascript"
    ],

    "Backend Developer": [
        "python",
        "node.js",
        "sql",
        "rest api"
    ],

    "Frontend Developer": [
        "html",
        "css",
        "javascript",
        "react"
    ],

    "Machine Learning Engineer": [
        "python",
        "machine learning",
        "tensorflow",
        "pytorch"
    ],

    "AI Engineer": [
        "python",
        "artificial intelligence",
        "machine learning"
    ],

    "Data Scientist": [
        "python",
        "data science",
        "machine learning",
        "sql"
    ]
}


# ==========================================
# SECTION DETECTION
# ==========================================

SECTIONS = {
    "Summary": [
        "summary",
        "professional summary",
        "profile",
        "objective"
    ],

    "Experience": [
        "experience",
        "work experience",
        "employment"
    ],

    "Education": [
        "education",
        "academic background",
        "qualifications"
    ],

    "Projects": [
        "projects",
        "personal projects",
        "academic projects"
    ],

    "Skills": [
        "skills",
        "technical skills",
        "technologies"
    ],

    "Certifications": [
        "certifications",
        "certificates"
    ]
}


# ==========================================
# FIND SKILLS
# ==========================================

def find_skills(text):

    text_lower = text.lower()

    detected = []

    for skill, keywords in SKILLS.items():

        for keyword in keywords:

            if keyword in text_lower:

                detected.append(skill)

                break

    return detected


# ==========================================
# FIND SECTIONS
# ==========================================

def find_sections(text):

    text_lower = text.lower()

    found = []

    for section, keywords in SECTIONS.items():

        for keyword in keywords:

            if keyword in text_lower:

                found.append(section)

                break

    return found


# ==========================================
# FIND JOB ROLES
# ==========================================

def find_job_roles(skills):

    skill_set = set(
        skill.lower()
        for skill in skills
    )

    matches = []

    for role, required_skills in JOB_ROLES.items():

        score = 0

        for skill in required_skills:

            if skill.lower() in skill_set:

                score += 1

        if score >= 2:

            matches.append(
                (
                    role,
                    score
                )
            )

    matches.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return [
        role
        for role, score in matches[:4]
    ]


# ==========================================
# ATS KEYWORDS
# ==========================================

ATS_KEYWORDS = [
    "developed",
    "implemented",
    "designed",
    "optimized",
    "automated",
    "analyzed",
    "managed",
    "built",
    "created",
    "improved",
    "deployed",
    "tested"
]


def analyze_ats(text):

    text_lower = text.lower()

    found = []

    missing = []

    for keyword in ATS_KEYWORDS:

        if keyword in text_lower:

            found.append(keyword)

        else:

            missing.append(keyword)

    return found, missing


# ==========================================
# CONTACT INFORMATION
# ==========================================

def analyze_contact_info(text):

    email = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    phone = re.search(
        r"(?:\+?\d[\d\s\-()]{8,}\d)",
        text
    )

    linkedin = "linkedin.com" in text.lower()

    github = "github.com" in text.lower()

    return {
        "email": bool(email),
        "phone": bool(phone),
        "linkedin": linkedin,
        "github": github
    }


# ==========================================
# RESUME SCORE
# ==========================================

def calculate_score(
    text,
    skills,
    sections,
    contact,
    ats_found
):

    score = 0

    # --------------------------------------
    # Resume length
    # --------------------------------------

    word_count = len(
        text.split()
    )

    if word_count >= 150:

        score += 15

    elif word_count >= 75:

        score += 10

    else:

        score += 5

    # --------------------------------------
    # Skills
    # --------------------------------------

    if len(skills) >= 8:

        score += 20

    elif len(skills) >= 5:

        score += 15

    elif len(skills) >= 2:

        score += 10

    # --------------------------------------
    # Sections
    # --------------------------------------

    score += min(
        len(sections) * 5,
        30
    )

    # --------------------------------------
    # Contact information
    # --------------------------------------

    if contact["email"]:

        score += 5

    if contact["phone"]:

        score += 5

    if contact["linkedin"]:

        score += 5

    if contact["github"]:

        score += 5

    # --------------------------------------
    # ATS keywords
    # --------------------------------------

    score += min(
        len(ats_found),
        10
    )

    return min(
        score,
        100
    )


# ==========================================
# SUGGESTIONS
# ==========================================

def generate_suggestions(
    text,
    skills,
    sections,
    contact,
    ats_found
):

    suggestions = []

    word_count = len(
        text.split()
    )

    if word_count < 150:

        suggestions.append(
            "Your resume appears short. Add more detail to projects, experience, and achievements."
        )

    if len(skills) < 5:

        suggestions.append(
            "Add more relevant technical skills that match the roles you are targeting."
        )

    if "Projects" not in sections:

        suggestions.append(
            "Add a Projects section with 2–4 strong technical projects."
        )

    if "Experience" not in sections:

        suggestions.append(
            "Add an Experience section if you have internships, freelance work, or relevant experience."
        )

    if "Education" not in sections:

        suggestions.append(
            "Add a clearly labeled Education section."
        )

    if not contact["linkedin"]:

        suggestions.append(
            "Consider adding your LinkedIn profile."
        )

    if not contact["github"]:

        suggestions.append(
            "Consider adding your GitHub profile for technical roles."
        )

    if len(ats_found) < 4:

        suggestions.append(
            "Use stronger action verbs such as developed, implemented, optimized, automated, and deployed."
        )

    # --------------------------------------
    # Check measurable achievements
    # --------------------------------------

    numbers = re.findall(
        r"\b\d+(?:\.\d+)?%?\b",
        text
    )

    if len(numbers) < 3:

        suggestions.append(
            "Add measurable results to your achievements, such as percentages, time saved, users served, or performance improvements."
        )

    return suggestions[:7]


# ==========================================
# MAIN ANALYZER
# ==========================================

def analyze_resume(text):

    if not text or not text.strip():

        return {
            "score": 0,
            "skills": [],
            "sections": [],
            "job_roles": [],
            "ats_found": [],
            "ats_missing": ATS_KEYWORDS,
            "contact": {},
            "suggestions": [
                "No resume text could be extracted."
            ],
            "word_count": 0
        }

    skills = find_skills(text)

    sections = find_sections(text)

    job_roles = find_job_roles(
        skills
    )

    ats_found, ats_missing = analyze_ats(
        text
    )

    contact = analyze_contact_info(
        text
    )

    score = calculate_score(
        text,
        skills,
        sections,
        contact,
        ats_found
    )

    suggestions = generate_suggestions(
        text,
        skills,
        sections,
        contact,
        ats_found
    )

    return {
        "score": score,
        "skills": skills,
        "sections": sections,
        "job_roles": job_roles,
        "ats_found": ats_found,
        "ats_missing": ats_missing,
        "contact": contact,
        "suggestions": suggestions,
        "word_count": len(text.split())
    }