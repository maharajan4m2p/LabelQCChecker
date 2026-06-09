import os

import pandas as pd

ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_label_frame(file_path: str) -> pd.DataFrame:
    extension = os.path.splitext(file_path)[1].lower().lstrip(".")

    if extension == "csv":
        frame = pd.read_csv(file_path)
    else:
        frame = pd.read_excel(file_path)

    return frame


def extract_label_value(row: pd.Series) -> str:
    for candidate in ("label", "text", "value", "annotation"):
        if candidate in row.index:
            return str(row[candidate]).strip()

    if len(row.index) > 0:
        return str(row.iloc[-1]).strip()

    return ""


def compare_label_files(file_a: str, file_b: str) -> dict:
    frame_a = load_label_frame(file_a)
    frame_b = load_label_frame(file_b)

    labels_a = [extract_label_value(row) for _, row in frame_a.iterrows()]
    labels_b = [extract_label_value(row) for _, row in frame_b.iterrows()]

    total_rows_a = len(labels_a)
    total_rows_b = len(labels_b)
    common_rows = min(total_rows_a, total_rows_b)

    mismatches = []
    for index in range(common_rows):
        left = labels_a[index]
        right = labels_b[index]
        if left != right:
            mismatches.append({
                "row": index + 1,
                "file_a": left,
                "file_b": right,
            })

    if total_rows_a > total_rows_b:
        for index in range(total_rows_b, total_rows_a):
            mismatches.append({
                "row": index + 1,
                "file_a": labels_a[index],
                "file_b": "<missing>",
            })
    elif total_rows_b > total_rows_a:
        for index in range(total_rows_a, total_rows_b):
            mismatches.append({
                "row": index + 1,
                "file_a": "<missing>",
                "file_b": labels_b[index],
            })

    return {
        "file_a_rows": total_rows_a,
        "file_b_rows": total_rows_b,
        "common_rows": common_rows,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }
