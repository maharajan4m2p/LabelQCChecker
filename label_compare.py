import cv2
import pytesseract
from difflib import SequenceMatcher

# Tesseract OCR Path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return ""

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    text = pytesseract.image_to_string(
        gray,
        lang="eng"
    )

    return text.strip()


def similarity(text1, text2):

    return SequenceMatcher(
        None,
        text1.lower(),
        text2.lower()
    ).ratio()


def compare_labels(
    approval_path,
    sample_path
):

    approval_text = extract_text(
        approval_path
    )

    sample_text = extract_text(
        sample_path
    )

    approval_lines = [
        line.strip()
        for line in approval_text.splitlines()
        if line.strip()
    ]

    sample_lines = [
        line.strip()
        for line in sample_text.splitlines()
        if line.strip()
    ]

    matched_fields = []
    missing_fields = []
    extra_fields = []

    # Find matched and missing fields
    for approval_line in approval_lines:

        found = False

        for sample_line in sample_lines:

            score = similarity(
                approval_line,
                sample_line
            )

            if score >= 0.85:
                matched_fields.append(
                    approval_line
                )
                found = True
                break

        if not found:
            missing_fields.append(
                approval_line
            )

    # Find extra fields
    for sample_line in sample_lines:

        found = False

        for approval_line in approval_lines:

            score = similarity(
                sample_line,
                approval_line
            )

            if score >= 0.85:
                found = True
                break

        if not found:
            extra_fields.append(
                sample_line
            )

    total_fields = len(
        approval_lines
    )

    matched_count = len(
        matched_fields
    )

    if total_fields > 0:
        probability = round(
            (
                matched_count /
                total_fields
            ) * 100,
            2
        )
    else:
        probability = 0

    if probability >= 95:
        verdict = "APPROVED"

    elif probability >= 80:
        verdict = (
            "APPROVED WITH DIFFERENCES"
        )

    else:
        verdict = "NOT APPROVED"

    return {

        "verdict": verdict,

        "probability": probability,

        "total_fields": total_fields,

        "matched_fields": matched_count,

        "missing_fields": missing_fields,

        "extra_fields": extra_fields,

        "approval_text": approval_text,

        "sample_text": sample_text

    }