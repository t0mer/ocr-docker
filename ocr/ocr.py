# -*- coding: utf-8 -*-
from flask import Flask, request, make_response, render_template, url_for, g, send_from_directory, jsonify, send_file
from flask_restful import Resource, Api
from json import dumps
from loguru import logger
import yaml, uuid, base64, os, io
import pytesseract
import subprocess
from subprocess import Popen
import time
import mimetypes
import urllib.parse
import urllib.request
import csv

try:
    from PIL import Image
except ImportError:
    import Image


# Validating file extension
def allowed_file(image_file):
    logger.info("Validating file extension")
    return '.' in image_file and \
           image_file.rsplit('.', 1)[1].lower() in {"png", "jpg", "pdf", "tiff"}

# Getting file extension
def getExtention(image_file):
    logger.info("Getting file extension")
    filename, file_extension = os.path.splitext(image_file)
    return filename, file_extension

def perform_ocr(image_file, language, cleanup_paths):
    working_file = image_file

    if working_file.lower().endswith(".pdf"):
        working_file = convert_to_tiff(working_file)
        cleanup_paths.append(working_file)

    if working_file.lower().endswith(".tiff"):
        image = Image.open(working_file)
        config = ("--psm 6")
        txt = ''
        for frame in range(image.n_frames):
            image.seek(frame)
            txt += pytesseract.image_to_string(image, config=config, lang=language) + '\n'
        return txt

    return pytesseract.image_to_string(Image.open(working_file), lang=language)

def convert_to_tiff(image_file):
    logger.info("Converting pdf to tiff")
    converted_file_name = image_file.replace('pdf','tiff')
    p = subprocess.Popen('convert -density 300 '+ image_file +' -background white -alpha Off '+ converted_file_name , stderr=subprocess.STDOUT, shell=True)
    p_status = p.wait()
    time.sleep(5)
    if os.path.exists(image_file):
        os.remove(image_file)
    return converted_file_name


def download_image(image_url, upload_folder):
    logger.info("Downloading image from URL")
    parsed_url = urllib.parse.urlsplit(image_url)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError("Only http and https image URLs are supported")

    file_name = os.path.basename(parsed_url.path)
    _, ext = os.path.splitext(file_name)

    if not ext:
        mime_type = urllib.request.urlopen(image_url, timeout=10).info().get_content_type()
        ext = mimetypes.guess_extension(mime_type) or ""

    if not ext:
        raise ValueError("Image URL must include a file name with an extension")

    candidate_name = f"{uuid.uuid4()}_{(file_name or 'remote').lower()}".split("?")[0]
    if ext and not candidate_name.lower().endswith(ext.lower()):
        candidate_name += ext
    candidate_path = os.path.join(upload_folder, candidate_name)

    if not allowed_file(candidate_path):
        raise ValueError("The file type you uploaded is not supported")

    with urllib.request.urlopen(image_url, timeout=10) as response:
        with open(candidate_path, 'wb') as out_file:
            out_file.write(response.read())

    return candidate_path


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "/opt/ocr/tmp"
api = Api(app)



@app.route('/ocr', methods=['POST'])
def ocr():
    if request.method == 'POST':
        # check if the post request has the file part
        language = str(request.form['languages']) if 'languages' in request.form else ''
        file = request.files.get('file')
        image_url = request.form.get('image_url', '').strip()

        if not file and not image_url:
            return "Data posted does not contains files"

        if not language:
            return "Please select OCR Language"

        filename = file.filename.lower() if file else ''
        _, ext = os.path.splitext(filename)
        is_csv_upload = ext == '.csv'

        if file and not (allowed_file(filename) or is_csv_upload):
            return "The file type you uploaded is not supported"

        cleanup_paths = []
        try:
            if file and allowed_file(file.filename):
                filename = file.filename.lower()
                image_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_file)
                cleanup_paths.append(image_file)
                return perform_ocr(image_file, language, cleanup_paths)
            elif file and is_csv_upload:
                csv_name = f"{uuid.uuid4()}_{filename}"
                csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_name)
                file.save(csv_path)
                cleanup_paths.append(csv_path)

                results = [("code", "url", "ocr_text")]
                with open(csv_path, newline='', encoding='utf-8') as csv_file:
                    reader = csv.DictReader(csv_file)
                    if not reader.fieldnames:
                        raise ValueError("CSV file must include a 'URL' column")

                    header_map = {name.lower(): name for name in reader.fieldnames}
                    if 'url' not in header_map:
                        raise ValueError("CSV file must include a 'URL' column")
                    if 'code' not in header_map:
                        raise ValueError("CSV file must include a 'code' column")

                    for idx, row in enumerate(reader, start=1):
                        url_value = (row.get(header_map['url']) or '').strip()
                        code_value = (row.get(header_map['code']) or '').strip()
                        if not url_value:
                            results.append((code_value, '', 'URL is empty, skipping.'))
                            continue

                        try:
                            downloaded_image = download_image(url_value, app.config['UPLOAD_FOLDER'])
                            cleanup_paths.append(downloaded_image)
                            ocr_text = perform_ocr(downloaded_image, language, cleanup_paths)
                            results.append((code_value, url_value, ocr_text.strip()))
                        except Exception as row_exc:
                            logger.exception("Failed to process row %s", idx)
                            results.append((code_value, url_value, f"Error: {row_exc}"))

                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerows(results)
                csv_content = output.getvalue()

                response = make_response(csv_content)
                response.headers['Content-Type'] = 'text/csv'
                response.headers['Content-Disposition'] = 'attachment; filename=ocr_results.csv'
                return response
            else:
                image_file = download_image(image_url, app.config['UPLOAD_FOLDER'])
                cleanup_paths.append(image_file)
                return perform_ocr(image_file, language, cleanup_paths)
        except Exception as exc:
            logger.exception("OCR processing failed")
            return str(exc)
        finally:
            for path in cleanup_paths:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                        logger.info(f"Deleted temporary file: {path}")
                except Exception:
                    logger.warning(f"Failed to delete temporary file: {path}")



@app.route('/')
def devices():
    return render_template('index.html')


@app.route('/languages')
def languages():
    return jsonify(pytesseract.get_languages())

# Serve Javascript
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)




# Start Application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
