# OCR-Docker
## Extract text from images & pdf files

OCR-Docker is a Python & [Flask](https://flask.palletsprojects.com/en/1.1.x/) powered, easy to use system that helps us to easily extract text from images and pdf files in multiple languages.

## Features

- Extract text from images (png, jpg, tiff).
- Extract text from pdf files (single or multiple pages).

## Components and Frameworks used in TTS-STT
* [tesseract-ocr](https://github.com/tesseract-ocr/) - open source ocr
* [tessdata](https://github.com/tesseract-ocr/tessdata) - tesseract-ocr data models
* [ghostscript](https://www.ghostscript.com/)
* [imagemagick](https://imagemagick.org/index.php)
* [pytesseract](https://pypi.org/project/pytesseract/)
* [Pillow](https://pypi.org/project/Pillow/)
* [Image](https://pypi.org/project/image/)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Loguru](https://pypi.org/project/loguru/)
* [PyYAML](https://pypi.org/project/PyYAML/)

 The OCR (Optical Character Recognition) feature is free thanks to [tesseract-ocr](https://github.com/tesseract-ocr/) which is an Open Source OCR project.
## Installation
#### docker-compose from hub
```yaml
version: "3.7"
services:
  ocr:
    image: techblog/ocr-docker:latest
    ports:
      - "8080:8080"
    container_name: tts-stt
    labels:
      - "com.ouroboros.enable=true"
    networks:
      - default
    restart: unless-stopped
```
Now, run ```docker-compose up -d``` to pull and run your container.
Open your browser and navigate to your container ip address with port 8080, you should see the following screen.

[![OCR](https://github.com/t0mer/ocr-docker/blob/main/screenshot/ocr.png?raw=true "OCR")](https://github.com/t0mer/ocr-docker/blob/main/screenshot/ocr.png?raw=true "OCR")



