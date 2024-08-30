from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ProcessingRequest(db.Model):
    id = db.Column(db.String(36), primary_key=True, unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    input_urls = db.Column(db.Text, nullable=False)
    output_urls = db.Column(db.Text, nullable=True)
