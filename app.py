from flask import (
    Flask,
    render_template,
    request
)

from werkzeug.utils import (
    secure_filename
)

import os

from label_compare import (
    compare_labels
)

app = Flask(__name__)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = (
    UPLOAD_FOLDER
)


@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route(
    "/compare",
    methods=["POST"]
)
def compare():

    approval = request.files.get(
        "approval"
    )

    samples = request.files.getlist(
        "sample"
    )

    if not approval or len(samples) == 0:

        return (
            "Please upload one Approval "
            "image and at least one "
            "Sample image."
        )

    approval_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(
            approval.filename
        )
    )

    approval.save(
        approval_path
    )

    all_results = []

    for sample in samples:

        if sample.filename == "":
            continue

        sample_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            secure_filename(
                sample.filename
            )
        )

        sample.save(
            sample_path
        )

        result = compare_labels(
            approval_path,
            sample_path
        )

        all_results.append({
            "filename": sample.filename,
            "result": result
        })

    return render_template(
        "results.html",
        results=all_results
    )


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )