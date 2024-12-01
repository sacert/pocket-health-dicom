import io
import os
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.utils import secure_filename
import pydicom
from pydicom.errors import InvalidDicomError
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

SWAGGER_URL = os.environ.get("SWAGGER_URL")
SWAGGER_CONFIG_FILE_URL = os.environ.get("SWAGGER_CONFIG_FILE_URL")

DICOM_FOLDER = os.environ.get("DICOM_FOLDER", "/tmp/dicom_files")
Path(DICOM_FOLDER).mkdir(parents=True, exist_ok=True)

if SWAGGER_URL and SWAGGER_CONFIG_FILE_URL:
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        SWAGGER_CONFIG_FILE_URL,
        config={"app_name": "PocketHealth DICOM"},
    )
    app.register_blueprint(swaggerui_blueprint)
else:
    logger.warning("Swagger environment variables are not set.")


def parse_tag(tag):
    try:
        return tuple(int(x, 16) for x in tag.split(","))
    except:
        raise ValueError(
            "Invalid structure for tag, it should be (XXXX, XXXX) where each element is a hexademical value"
        )


@app.route("/upload", methods=["POST"])
def upload_dicom_file():

    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file.save(os.path.join(DICOM_FOLDER, filename))

    try:
        pydicom.dcmread(os.path.join(DICOM_FOLDER, filename))
    except InvalidDicomError as e:
        os.remove(os.path.join(DICOM_FOLDER, filename))
        return jsonify({"error": f"Error processing DICOM file; {str(e)}"}), 400

    return jsonify({"message": "Sucessfully uploaded"}), 200


@app.route("/dicom-header-attribute", methods=["GET"])
def get_dicom_header_attribute():
    tag = request.args.get("tag")
    filename = request.args.get("filename")

    if not filename:
        return jsonify({"error": "Please specify filename"}), 400

    if not tag:
        return jsonify({"error": "Please specify tag"}), 400

    if not os.path.exists(os.path.join(DICOM_FOLDER, filename)):
        return jsonify({"error": f"{filename} not found"}), 404

    try:
        dicom_file = pydicom.dcmread(os.path.join(DICOM_FOLDER, filename))

        if not dicom_file:
            return jsonify({"error": "Invalid DICOM file"}), 400

        tag = parse_tag(tag)

        if not tag in dicom_file:
            return jsonify({"error": f"Tag not found: {tag}"}), 404

        return jsonify({"attribute": str(dicom_file[tag])}), 200
    except InvalidDicomError as e:
        return jsonify({"error": f"Error processing DICOM file; {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/convert-to-png", methods=["GET"])
def convert_to_png():
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    file_path = os.path.join(DICOM_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        dicom_file = pydicom.dcmread(os.path.join(DICOM_FOLDER, filename))

        if not dicom_file:
            return jsonify({"error": "Invalid DICOM file"}), 400

        pixel_array_numpy = dicom_file.pixel_array

        image = Image.fromarray(
            (pixel_array_numpy / np.max(pixel_array_numpy) * 255).astype("uint8")
        )

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")

        img_byte_arr.seek(0)
        return send_file(img_byte_arr, mimetype="image/png")
    except InvalidDicomError as e:
        return jsonify({"error": f"Error processing DICOM file; {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to convert to PNG: {str(e)}"}), 500


if __name__ == "__main__":
    logger.info("Starting DICOM handling service")
    app.run(host="0.0.0.0", debug=True)
