import easyocr
import re

# Initialize OCR reader once
reader = easyocr.Reader(['en'], gpu=False)


def extract_text(image_path):
    """
    Extract text from image using EasyOCR.
    """
    try:
        results = reader.readtext(image_path)

        text_lines = []

        for result in results:
            text = result[1].strip()

            if text:
                text_lines.append(text)

        return text_lines

    except Exception as e:
        print(f"OCR Error: {e}")
        return []


def clean_text(lines):
    """
    Clean OCR output.
    """
    cleaned = []

    for line in lines:

        line = line.strip()

        line = re.sub(r'\s+', ' ', line)

        if line:
            cleaned.append(line)

    return cleaned


def compare_label_images(approval_image, sample_image):
    """
    Compare approval label with sample label.
    """

    approval_text = extract_text(approval_image)
    sample_text = extract_text(sample_image)

    approval_text = clean_text(approval_text)
    sample_text = clean_text(sample_text)

    approval_set = set(
        item.lower().strip()
        for item in approval_text
    )

    sample_set = set(
        item.lower().strip()
        for item in sample_text
    )

    missing_data = sorted(
        list(approval_set - sample_set)
    )

    extra_data = sorted(
        list(sample_set - approval_set)
    )

    matched_data = sorted(
        list(approval_set & sample_set)
    )

    total_required = len(approval_set)

    total_found = len(matched_data)

    match_percentage = 0

    if total_required > 0:
        match_percentage = round(
            (total_found / total_required) * 100,
            2
        )

    status = "PASS"

    if missing_data:
        status = "FAIL"

    return {
        "status": status,
        "approval_text": approval_text,
        "sample_text": sample_text,
        "missing_data": missing_data,
        "extra_data": extra_data,
        "matched_data": matched_data,
        "match_percentage": match_percentage,
        "total_required": total_required,
        "total_found": total_found
    }