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

# --- NEW ENDPOINT FOR SECURE DOWNLOADS ---
# This is the new function you are adding.
@app.route('/generate-download-url', methods=['POST'])
def generate_download_url():
    """Generates a signed URL for reading a private GCS object."""
    json_data = request.get_json()
    if not json_data or 'objectName' not in json_data:
        return jsonify({'error': 'Missing objectName'}), 400

    object_name = json_data['objectName']
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)

    try:
        # The expiration time for the URL
        expiration_time = datetime.timedelta(days=7)

        # Generate the signed URL for a GET request (read)
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration_time,
            method="GET",
        )
        return jsonify({'url': url}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to generate download URL: {str(e)}'}), 500
# --- END OF NEW ENDPOINT ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
