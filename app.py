import os
import uuid

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from label_compare import compare_label_images

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tif",
    "tiff"
}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compare", methods=["POST"])
def compare():

    approval = request.files.get("approval")
    samples = request.files.getlist("sample")

    if not approval or approval.filename == "":
        return "Approval file missing", 400

    if not samples or len(samples) == 0 or all(s.filename == "" for s in samples):
        return "Sample file missing", 400

    if not allowed_file(approval.filename):
        return "Unsupported approval file type", 400

    approval_filename = (
        str(uuid.uuid4())
        + "_"
        + secure_filename(approval.filename)
    )

    approval_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        approval_filename
    )
    approval.save(approval_path)

    sample_results = []

    for sample in samples:
        if not sample or sample.filename == "":
            continue
        if not allowed_file(sample.filename):
            continue

        sample_filename = (
            str(uuid.uuid4())
            + "_"
            + secure_filename(sample.filename)
        )

        sample_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            sample_filename
        )

        sample.save(sample_path)

        result = compare_label_images(
            approval_path,
            sample_path
        )
        result["filename"] = sample.filename
        sample_results.append(result)

    if not sample_results:
        return "No valid sample files provided.", 400

    comparison = {
        "approval_filename": approval.filename,
        "samples": sample_results
    }

    return render_template(
        "results.html",
        comparison=comparison
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )