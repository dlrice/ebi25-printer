#!/usr/bin/env python3
import sys
from flask import Flask, render_template, request
from flask_cors import CORS
from jinja2 import Template
import pdfkit
import os
import uuid
import json
import logging

os.environ["DISPLAY"] = ":0"

app = Flask(__name__)
CORS(app)

TMP = os.path.expanduser("~/ebi25/tmp")
try:
    os.makedirs(TMP)
except OSError:
    if not os.path.isdir(TMP):
        raise

template = Template(
    """
<html>
  <head>
    <style>
      body {
        font-size: 40px;
        padding-left: 18px;
      }
    </style>
  </head>
  <body>
    {{ number }}
  </body>
</html>
"""
)


def send_pdf_to_printer(pdf_path):
    command = "lp {}".format(pdf_path)
    os.system(command)
    app.logger.info("printed with command: {}".format(command))


def generate_pdf(number):
    filename = uuid.uuid4().hex
    html_path = os.path.join(TMP, "{}.html".format(filename))
    pdf_path = os.path.join(TMP, "{}.pdf".format(filename))
    with open(html_path, "w") as f:
        f.write(template.render(number=number))
    app.logger.info("generated HTML file: {}".format(html_path))
    pdfkit.from_file(html_path, pdf_path)
    app.logger.info("generated PDF file: {}".format(pdf_path))
    return html_path, pdf_path


def clean_up(html_path, pdf_path):
    for path in [html_path, pdf_path]:
        os.remove(path)
        app.logger.info("removed {}".format(path))


def success():
    app.logger.info("success")
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


def failure(exception):
    app.logger.info("failure: {}".format(exception))
    return (
        json.dumps({"success": False, "exception": exception}),
        400,
        {"ContentType": "application/json"},
    )


@app.route("/print/<int:number>")
def print_number(number):
    app.logger.info("received request: {}".format(number))
    if number >= 1e6:
        return failure("{} >= 1e6".format(number))
    if number < 1e5:
        return failure("{} < 1e5".format(number))
    number = "{:6d}".format(number)
    try:
        html_path, pdf_path = generate_pdf(number)
        send_pdf_to_printer(pdf_path)
        clean_up(html_path, pdf_path)
    except Exception as e:
        print(e)
        return failure(e)
    else:
        return success()


def test():
    pdf_path = generate_pdf("123456")
    # send_pdf_to_printer(pdf_path)
    print("Just give up hahahaha")


if __name__ == "__main__":
    test()
    #    app.run(host='0.0.0.0', port=8000, debug=True)
