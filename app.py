import os
import uuid
import traceback

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from label_compare import compare_label_images

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tif", "tiff"}

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
    try:
        approval = request.files.get("approval")
        samples = request.files.getlist("sample")

        if not approval or approval.filename == "":
            return render_template(
                "results.html",
                error="Approval file missing.",
                comparison=None
            ), 400

        if not samples or all(s.filename == "" for s in samples):
            return render_template(
                "results.html",
                error="At least one sample file is required.",
                comparison=None
            ), 400

        if not allowed_file(approval.filename):
            return render_template(
                "results.html",
                error="Unsupported approval file type.",
                comparison=None
            ), 400

        approval_filename = (
            str(uuid.uuid4()) + "_" + secure_filename(approval.filename)
        )
        approval_path = os.path.join(
            app.config["UPLOAD_FOLDER"], approval_filename
        )
        approval.save(approval_path)
        print(f"Approval saved: {approval_path}")

        sample_results = []

        for sample in samples:
            if not sample:
                continue
            if sample.filename == "":
                continue
            if not allowed_file(sample.filename):
                continue

            sample_filename = (
                str(uuid.uuid4()) + "_" + secure_filename(sample.filename)
            )
            sample_path = os.path.join(
                app.config["UPLOAD_FOLDER"], sample_filename
            )
            sample.save(sample_path)
            print(f"Sample saved: {sample_path}")

            result = compare_label_images(approval_path, sample_path)
            result["filename"] = sample.filename
            sample_results.append(result)

        if not sample_results:
            return render_template(
                "results.html",
                error="No valid sample files were uploaded.",
                comparison=None
            ), 400

        comparison = {
            "approval_filename": approval.filename,
            "samples": sample_results
        }

        return render_template(
            "results.html",
            comparison=comparison,
            error=None
        ), 200

    except Exception as e:
        traceback.print_exc()
        return render_template(
            "results.html",
            error=f"Server error: {str(e)}",
            comparison=None
        ), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)