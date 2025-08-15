import os
import uuid
import traceback
from flask import Flask, request, jsonify
from google.cloud import storage
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def health_check():
    """A simple route to check if the server is running."""
    return "Health check OK: Final version is running.", 200

# --- Configuration ---
BUCKET_NAME = "channelcomph_quotation"
storage_client = storage.Client()

@app.route('/generate-upload-url', methods=['POST'])
def generate_upload_url():
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({"error": "Filename is required"}), 400

        original_filename = data['filename']
        unique_id = str(uuid.uuid4())
        object_name = f"uploads/{unique_id}-{original_filename}"

        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)

        # --- THIS IS THE CORRECTED FUNCTION ---
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=15),
            method="PUT",
            content_type=data.get('contentType', 'application/octet-stream')
        )
        
        return jsonify({"url": url, "objectName": object_name})

    except Exception as e:
        print("!!! AN EXCEPTION OCCURRED !!!")
        traceback.print_exc()
        return jsonify({"error": f"Server exception: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
