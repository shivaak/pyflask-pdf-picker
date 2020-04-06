# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import flask
import io

from flask import Flask, render_template, Response
from PyPDF2 import PdfFileMerger, PageRange, PdfFileReader

app = Flask(__name__)
app.config.update(
    ALLOWED_EXTENSIONS=set(['pdf'])
)

app.debug = False
app.testing = False


@app.route('/')
def home():
    return render_template('list.html')


@app.route('/pick', methods=['POST'])
def uploadpdf():
    # If an image was uploaded, update the data to point to the new image.
    uploaded_file = flask.request.files['file']
    if uploaded_file.filename.endswith((".pdf")):
        pdf = uploaded_file
    else:
        return "Invalid File"

    text = flask.request.form['pages']
    pages = []
    try:
        pages = [x.strip() for x in text.split(',')]
    except:
        return "Invalid Page numbers"

    merger = PdfFileMerger()
    temp = io.BytesIO()
    pdfobj = PdfFileReader(pdf)
    totalPages = pdfobj.getNumPages();
    try:
        for i in pages:
            print(i)
            if '-' in i:
                pageFromTo = i.split('-')
                print(pageFromTo)
                if len(pageFromTo) !=2:
                    raise Exception('Invalid Range {}'.format(i))
                if int(pageFromTo[0])<0 or int(pageFromTo[1])<0:
                    raise Exception('Invalid Page {}'.format(i))
                if int(pageFromTo[0]) > totalPages or int(pageFromTo[1]) > totalPages or int(pageFromTo[0]) > int(pageFromTo[1]):
                    raise Exception('Invalid Page {}'.format(i))
                range = str(int(pageFromTo[0])-1) + ':' + pageFromTo[1]
                merger.append(pdf, pages=PageRange(range))
            else:
                if int(i) <= 0 or int(i) > totalPages:
                    raise Exception('Invalid Page {}'.format(i))
                t = int(i) - 1
                merger.append(pdf, pages=PageRange(str(t)))
    except Exception as e:
        merger.close()
        return str(e)

    print(merger.__sizeof__())
    merger.write(temp)
    merger.close()
    temp.seek(0)
    return Response(temp,
                 mimetype="application/pdf",
                 headers={"Content-Disposition":
                              "attachment; filename=result.pdf"})


@app.route('/errors')
def errors():
    raise Exception('This is an intentional exception.')


# This is only used when running locally. When running live, gunicorn runs
# the application.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
