
FROM ubuntu:18.04

LABEL maintainer="tomer.klein@gmail.com"

ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

RUN apt update -yqq

RUN apt -yqq install software-properties-common

RUN add-apt-repository ppa:alex-p/tesseract-ocr-devel -y

RUN apt -yqq install python3-pip && \
    apt -yqq install libffi-dev && \
    apt -yqq install libssl-dev && \
    apt -yqq install tesseract-ocr && \
    apt -yqq install ghostscript && \
    apt -yqq install imagemagick
    
RUN  pip3 install --upgrade pip --no-cache-dir && \
     pip3 install --upgrade setuptools --no-cache-dir && \
     pip3 install flask --no-cache-dir && \
     pip3 install flask_restful --no-cache-dir && \
     pip3 install loguru --no-cache-dir && \
     pip3 install cryptography --no-cache-dir && \
     pip3 install pytesseract --no-cache-dir && \
     pip3 install Pillow --no-cache-dir && \
     pip3 install Image --no-cache-dir && \
     pip3 install pyyaml --no-cache-dir
     
 RUN mkdir -p /opt/ocr/tmp
 
 RUN sed -i_bak 's/rights="none" pattern="PDF"/rights="read | write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml

 COPY ocr /opt/ocr

 #Copy languages files
 COPY traineddata /usr/share/tesseract-ocr/5/tessdata
 
 EXPOSE 8080
 
 ENTRYPOINT ["/usr/bin/python3", "/opt/ocr/ocr.py"]
