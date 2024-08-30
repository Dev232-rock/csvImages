from celery import Celery
from models import db, ProcessingRequest
from utils import generate_output_csv
from PIL import Image
import requests
from io import BytesIO
import os

celery = Celery(__name__, backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')

@celery.task
def process_images(request_id, products):
    for product in products:
        output_urls = []

        for url in product['input_urls']:
            try:
                # Download the image
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                
                # Compress the image (reduce quality to 50%)
                output = BytesIO()
                img.save(output, format='JPEG', quality=50)
                
                # Save the compressed image to disk (or upload to cloud storage)
                output_dir = 'output_images'
                os.makedirs(output_dir, exist_ok=True)
                output_filename = f"processed_image_{request_id}_{product['product_name']}_{url.split('/')[-1]}"
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(output.getvalue())
                
                output_urls.append(output_path)
            except Exception as e:
                print(f"Error processing image {url}: {e}")
                output_urls.append('Failed to process')

        # Update the database with the output URLs
        processing_request = ProcessingRequest.query.filter_by(id=request_id).first()
        if processing_request:
            processing_request.status = 'Completed'
            processing_request.output_urls = ','.join(output_urls)
            db.session.commit()
        
        # Generate the output CSV file
        generate_output_csv(request_id, product['product_name'], product['input_urls'], output_urls)

    return 'Processing completed'
