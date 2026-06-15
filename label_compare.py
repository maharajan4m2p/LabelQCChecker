import os
import cv2
import pytesseract

from difflib import SequenceMatcher


# Windows only
if os.name == "nt":

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

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    text = pytesseract.image_to_string(
        gray,
        lang="eng"
    )

    return text.strip()


# --------------------------------------------------
# LOGO COMPARISON
# --------------------------------------------------

def compare_logo(
    approval_path,
    sample_path
):

    try:

        approval_img = cv2.imread(
            approval_path
        )

        sample_img = cv2.imread(
            sample_path
        )

        if approval_img is None or sample_img is None:

            return 0, "FAIL"

        approval_gray = cv2.cvtColor(
            approval_img,
            cv2.COLOR_BGR2GRAY
        )

        sample_gray = cv2.cvtColor(
            sample_img,
            cv2.COLOR_BGR2GRAY
        )

        sample_gray = cv2.resize(

            sample_gray,

            (
                approval_gray.shape[1],
                approval_gray.shape[0]
            )

        )

        result = cv2.matchTemplate(

            sample_gray,
            approval_gray,
            cv2.TM_CCOEFF_NORMED

        )

        _, max_val, _, _ = cv2.minMaxLoc(
            result
        )

        logo_similarity = round(
            max_val * 100,
            2
        )

        logo_status = (
            "PASS"
            if logo_similarity >= 90
            else "FAIL"
        )

        return logo_similarity, logo_status

    except Exception as e:

        print(
            "Logo Compare Error:",
            str(e)
        )

        return 0, "FAIL"


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

    comparison_rows = []

    # Compare Approval vs Sample

    for approval_line in approval_lines:

        best_score = 0

        best_match = ""

        for sample_line in sample_lines:

            score = SequenceMatcher(
                None,
                approval_line.lower(),
                sample_line.lower()
            ).ratio()

            if score > best_score:

                best_score = score
                best_match = sample_line

        if best_score >= 0.80:

            matched_fields.append(
                approval_line
            )

            comparison_rows.append({

                "approval":
                    approval_line,

                "sample":
                    best_match

            })

        else:

            missing_fields.append(
                approval_line
            )

            comparison_rows.append({

                "approval":
                    approval_line,

                "sample":
                    "❌ Missing"

            })

    # Find extra fields

    for sample_line in sample_lines:

        found = False

        for approval_line in approval_lines:

            score = SequenceMatcher(
                None,
                sample_line.lower(),
                approval_line.lower()
            ).ratio()

            if score >= 0.80:

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

    missing_count = len(
        missing_fields
    )

    extra_count = len(
        extra_fields
    )

    if total_fields > 0:

        probability = round(

            (
                matched_count
                /
                total_fields
            ) * 100,

            2

        )

    else:

        probability = 0

    if probability >= 90:

        verdict = "APPROVED"

    elif probability >= 75:

        verdict = "PARTIALLY APPROVED"

    else:

        verdict = "NOT APPROVED"

    # -----------------------------
    # LOGO CHECK
    # -----------------------------

    logo_similarity, logo_status = compare_logo(

        approval_path,
        sample_path

    )

    return {

        "verdict":
            verdict,

        "probability":
            probability,

        "total_fields":
            total_fields,

        "matched_count":
            matched_count,

        "missing_count":
            missing_count,

        "extra_count":
            extra_count,

        "matched_fields":
            matched_fields,

        "missing_fields":
            missing_fields,

        "extra_fields":
            extra_fields,

        "comparison_rows":
            comparison_rows,

        "approval_text":
            approval_text,

        "sample_text":
            sample_text,

        # NEW LOGO RESULTS

        "logo_similarity":
            logo_similarity,

        "logo_status":
            logo_status

    }