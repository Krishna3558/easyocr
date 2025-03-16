from flask import jsonify , request , Flask
from flask_cors import CORS
from pdf2image import convert_from_path
import os
from PIL import Image
import easyocr
import tempfile
import numpy as np

app = Flask(__name__)
CORS(app)

reader = easyocr.Reader(['en', 'hi'])

@app.route('/extract-text' , methods=['GET'])
def extract_text():
    if "file" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected files"}), 400
    try:
        extracted_text = ""
        if file.filename.lower().endswith(".pdf"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                file.save(temp_pdf.name)

            # Convert PDF to images
            images = convert_from_path(temp_pdf.name , poppler_path=r"C:\Users\mkitt\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin")
            for page_num, image in enumerate(images, start=1):
                image_np = np.array(image)
                page_text = reader.readtext(image_np, detail=0)
                extracted_text += f"\n--- Page {page_num} ---\n" + " ".join(page_text)

            os.remove(temp_pdf.name) 
        else:
            img = Image.open(file)
            page_text = reader.readtext(img, detail=0)
            extracted_text = " ".join(page_text)
        
        return jsonify({"extracted_text": extracted_text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/')
def home():
    return "EasyOCR API is running!"

if __name__ == "__main__":
    app.run(debug=True)