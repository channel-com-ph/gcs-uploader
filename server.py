import os
import uuid
from flask import Flask, request, jsonify
from google.cloud import storage
import datetime
from flask_cors import CORS # Import CORS

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.route('/')
def health_check():
    """A simple route to check if the server is running."""
    return "Health check OK: Service is running.", 200

# --- Configuration ---
# Get this from your GCS bucket page
BUCKET_NAME = "channelcomph_quotation" 

# Initialize the Google Cloud Storage client
# The client will automatically find the credentials from the environment variable
storage_client = storage.Client()

@app.route('/generate-upload-url', methods=['POST'])
def generate_upload_url():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Filename is required"}), 400

    original_filename = data['filename']

    # Create a secure, unique name for the object in GCS
    unique_id = str(uuid.uuid4())
    object_name = f"uploads/{unique_id}-{original_filename}"

    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)

    # Generate the signed URL, allowing a PUT request for 15 minutes
    url = blob.generate_v4_put_object_presigned_url(
        version="v4",
        expiration=datetime.timedelta(minutes=15),
        content_type=data.get('contentType', 'application/octet-stream')
    )

    # Return both the URL for uploading and the object_name for reference
    return jsonify({"url": url, "objectName": object_name})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Trivial change to force a new build
