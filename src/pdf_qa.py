import re
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_pdf_text(file_path):

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def split_into_chunks(text, max_words=120):

    words = text.split()

    chunks = []

    for i in range(0, len(words), max_words):

        chunk = " ".join(
            words[i:i + max_words]
        )

        if chunk.strip():
            chunks.append(chunk)

    return chunks


def find_relevant_chunks(question, chunks, top_k=3):

    if not chunks:
        return []

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    documents = chunks + [question]

    matrix = vectorizer.fit_transform(documents)

    similarities = cosine_similarity(
        matrix[-1],
        matrix[:-1]
    )[0]

    ranked = similarities.argsort()[::-1]

    relevant = []

    for index in ranked[:top_k]:

        if similarities[index] > 0:

            relevant.append(
                chunks[index]
            )

    return relevant


def generate_answer(question, chunks):

    relevant_chunks = find_relevant_chunks(
        question,
        chunks
    )

    if not relevant_chunks:

        return (
            "I couldn't find relevant information "
            "in the uploaded PDF."
        )

    # Combine the most relevant sections
    context = " ".join(
        relevant_chunks
    )

    # Split context into sentences
    sentences = re.split(
        r"(?<=[.!?])\s+",
        context
    )

    question_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            question.lower()
        )
    )

    scored_sentences = []

    for sentence in sentences:

        sentence_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                sentence.lower()
            )
        )

        overlap = len(
            question_words & sentence_words
        )

        if overlap > 0:

            scored_sentences.append(
                (
                    overlap,
                    sentence.strip()
                )
            )

    scored_sentences.sort(
        key=lambda x: x[0],
        reverse=True
    )

    if scored_sentences:

        answer_sentences = [
            sentence
            for score, sentence
            in scored_sentences[:3]
        ]

        return " ".join(
            answer_sentences
        )

    return relevant_chunks[0]


def answer_pdf_question(
    file_path,
    question
):

    text = extract_pdf_text(
        file_path
    )

    if not text.strip():

        return {
            "answer": (
                "No readable text could be "
                "extracted from this PDF."
            ),
            "chunks": 0,
            "word_count": 0
        }

    chunks = split_into_chunks(
        text
    )

    answer = generate_answer(
        question,
        chunks
    )

    return {
        "answer": answer,
        "chunks": len(chunks),
        "word_count": len(text.split())
    }