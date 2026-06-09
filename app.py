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
