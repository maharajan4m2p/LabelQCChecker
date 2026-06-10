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

    sample = request.files.get(
        "sample"
    )

    if not approval or not sample:

        return (
            "Please upload both "
            "Approval and Sample labels."
        )

    approval_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(
            approval.filename
        )
    )

    sample_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(
            sample.filename
        )
    )

    approval.save(
        approval_path
    )

    sample.save(
        sample_path
    )

    results = compare_labels(
        approval_path,
        sample_path
    )

    return render_template(
        "results.html",
        results=results
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