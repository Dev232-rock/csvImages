from flask import Flask, request, jsonify, render_template_string
from models import db, ProcessingRequest
from utils import parse_csv, generate_output_csv
from celery_worker import process_images
import uuid
import os

# Create required directories
output_dirs = ['output_images', 'output_csv']
for dir in output_dirs:
    os.makedirs(dir, exist_ok=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///image_processing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Default route
@app.route('/')
def index():
    return "Welcome to the Image Processing API"

# Route with HTML form for file upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        products = parse_csv(file)
        request_id = str(uuid.uuid4())

        for product in products:
            processing_request = ProcessingRequest(
                id=request_id,
                status='Pending',
                product_name=product['product_name'],
                input_urls=','.join(product['./input_urls/inputcsv.csv'])
            )
            db.session.add(processing_request)
            db.session.commit()

        process_images.delay(request_id, products)

        return jsonify({'request_id': request_id})
    
    # If the request method is GET, show the HTML form
    return render_template_string('''
    <!doctype html>
    <html>
        <head><title>Upload CSV File</title></head>
        <body>
            <h1>Upload CSV File</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit" value="Upload">
            </form>
        </body>
    </html>
    ''')

# Status route
@app.route('/status/<request_id>', methods=['GET'])
def get_status(request_id):
    processing_request = ProcessingRequest.query.get(request_id)
    if not processing_request:
        return jsonify({'error': 'Invalid Request ID'}), 404

    return jsonify({'status': processing_request.status})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
