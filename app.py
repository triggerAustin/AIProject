import os
import io
import json
import requests
import numpy as np
import faiss
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

from gradio_client import Client, handle_file

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


UPLOADS_FOLDER = "Documents"
os.makedirs(UPLOADS_FOLDER, exist_ok=True)

# Define file paths inside dataset folder
INDEX_FILE = os.path.join(UPLOADS_FOLDER, "faiss_index.bin")  # FAISS index file
METADATA_FILE = os.path.join(UPLOADS_FOLDER, "metadata.json")  # Metadata file
filepath = ""

# FAISS index setup
DIM = 768  # Adjust based on the embedding model

client = Client("Penality/pdf-something")
result = client.predict(
		text="Hello!!",
		api_name="/predict_1"
)
print(result)


@app.route("/hello", methods=["GET"], strict_slashes=False)
def hello():
    """to test if api endpoint is exposed"""
    return f"hello Marcella, how is your day going \n"

@app.route("/embeddings", methods=["GET"], strict_slashes=False)
def get_embeddings():
    """get embeddings file from Documents and send to huggingFace"""
    if not os.path.exists(INDEX_FILE):
        return None

    print(INDEX_FILE)

    return send_file(INDEX_FILE, as_attachment=True, mimetype="application/octet-stream")
 
@app.route("/metadata", methods=["GET"], strict_slashes=False)
def get_metadata():
    """get document metadata and and send to hugging face"""
    if not os.path.exists(METADATA_FILE):
        return None
    
    metadata = {}

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    return jsonify({"metadata_file": metadata})


@app.route("/file", methods=["GET"], strict_slashes=False)
def get_document():
    """get document based on document name"""
    print(request.args)

    file = request.args.get("file")  # Get file path from query parameters
    
    if not file:
        print("No file found in request")
        return jsonify({"error": "No file uploaded"}), 400
    
    if not os.path.exists(file):
        return jsonify({"error": "File not found"}), 404
    
    print(file)

    try:
        # Open the file in binary mode and read contents
        with open(file, "rb") as f:
            file_content = f.read()

        # Send file contents as a response
        return file_content, 200, {'Content-Type': 'application/pdf'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/embeddings", methods=["POST"], strict_slashes=False)
def post_embeddings():
    """store embeddings to Documents folder from hugging face"""
    print("File received:", request.files)  # Debug

    if "file" not in request.files:
        print("No file found in request")
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    print(f"Received file: {file.filename}, Size: {len(file.read())} bytes")  # Debug

    file.seek(0)  # Reset cursor
    file.save(INDEX_FILE)

    # Read the FAISS index
    index = faiss.read_index(INDEX_FILE)
    print(index.ntotal)

    # Write index back to the file system (if needed)
    faiss.write_index(index, INDEX_FILE)

    return jsonify({"message": "File successfully uploaded"})

@app.route("/upload", methods=["POST"], strict_slashes=False)
def upload_file():
    """Receive a PDF file, extract content, generate embeddings, and store them."""
    
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOADS_FOLDER, file.filename)
    file.save(filepath)  # Save the file

    # Generate embeddings (calls store_document_data)
    embedding = client.predict(
        PDF_FILE=handle_file(filepath),
        api_name="/predict_2"
    )

    metadata = {}
    print(filepath, embedding)
    doc_index = embedding
    metadata[str(doc_index)] = filepath
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f)

    print(" Saved Metadata")

    # ask the model
    prediction = client.predict(
        user_question="What is the document about",
		api_name="/predict"
    )

    print(prediction)

    return jsonify({"answer" : prediction}), 200

if __name__ == "__main__":
    app.run(debug=True)

