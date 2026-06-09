<<<<<<< HEAD
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
=======
import os

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from label_compare import ALLOWED_EXTENSIONS, allowed_file, compare_label_files

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.secret_key = "label-qc-checker-secret"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():
    uploaded_files = request.files.getlist("files")

    if len(uploaded_files) != 2:
        flash("Please upload exactly two label files.")
        return redirect(url_for("index"))

    saved_paths = []
    for uploaded_file in uploaded_files:
        if uploaded_file.filename == "":
            flash("One of the files is missing.")
            return redirect(url_for("index"))

        if not allowed_file(uploaded_file.filename):
            flash("Only CSV and Excel files are supported.")
            return redirect(url_for("index"))

        filename = secure_filename(uploaded_file.filename)
        destination = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(destination)
        saved_paths.append(destination)

    summary = compare_label_files(saved_paths[0], saved_paths[1])

    return render_template(
        "results.html",
        summary=summary,
        file_names=[os.path.basename(path) for path in saved_paths],
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
>>>>>>> 018d8f107f87750f6fb7eec948efb60c62d2e72e
