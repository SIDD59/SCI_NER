from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query, Path
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from pathlib import Path
import os

app = FastAPI()

cur_dir = os.path.abspath(os.path.dirname(__file__))
print("Current path: ", cur_dir)
CONTENT_PATH = os.path.join(cur_dir, 'static')
os.environ["CONTENT_PATH"] = CONTENT_PATH
print(f'CONTENT_PATH: {os.environ["CONTENT_PATH"]}')

import ner as ner

# Define your API keys (replace with your actual keys)
API_KEYS = {
    "key1": "secretkey1",
    "key2": "secretkey2"
}

# Define the API key security header
api_key_header = APIKeyHeader(name="X-API-Key")

# Dependency to validate API key
async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key in API_KEYS.values():
        #print(api_key)
        return api_key
    else:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.post("/ner")
async def upload_pdf(pdf_file: UploadFile =  File(..., media_type='application/pdf'), api_key: str = Depends(get_api_key) , accuracy_ratio: int = Query(..., title="Accuracy Ratio to combine entities", ge=0, le=100)):
    """
    This API accepts a pdf file, api key and accuracy ratio an integer between 0-100 as inputs and outputs the combined entities and the page numbers the entities are found on in a json format.
    """
    extension = os.path.splitext(pdf_file.filename)[1].lower()

    if extension != '.pdf':
       raise HTTPException(status_code=401, detail="In valid File Format. File Type should be PDF")
    else:
        print("Started API Execution")
        # Save the uploaded PDF
        pdf_path = Path("static/input") /pdf_file.filename
        print(pdf_path)
        with pdf_path.open("wb") as pdf    :
            pdf.write(pdf_file.file.read())

        # Save the uploaded file directly to the input folder
        inputfile_path = os.path.join(CONTENT_PATH, "input", pdf_file.filename)
        #pdf_file.save(inputfile_path)
        #print("Uploaded file:", pdf_file.filename)

        processedfile_name = pdf_file.filename.replace('.pdf', '_processed.pdf')
        processedfile_path = os.path.join(CONTENT_PATH, "output", processedfile_name)
        #print("Processed file:", processedfile_path)

        outputfile_name = 'ner_output.pdf'
        outputfile_path = os.path.join(CONTENT_PATH, "output", outputfile_name)
        #print("Output filepath:", outputfile_path)

        # Consolidate entities page numbers, Convert and highlight PDF
        final_formatted_data = ner.convert_and_highlight_pdf(inputfile_path, processedfile_path, outputfile_path, accuracy_ratio)

        return final_formatted_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)