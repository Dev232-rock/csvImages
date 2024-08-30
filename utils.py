import csv
import os

def parse_csv(file):
    products = []
    reader = csv.DictReader(file)
    for row in reader:
        products.append({
            'product_name': row['Product Name'],
            'input_urls': row['Input_csv'].split(',')
        })
    return products

def generate_output_csv(request_id, product_name, input_urls, output_urls):
    output_dir = 'output_csv'
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f"output_{request_id}.csv")

    with open(output_filename, 'w', newline='') as csvfile:
        fieldnames = ['Serial Number', 'Product Name', 'Input Image Urls', 'Output Image Urls']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, (input_url, output_url) in enumerate(zip(input_urls, output_urls)):
            writer.writerow({
                'Serial Number': i + 1,
                'Product Name': product_name,
                'Input Image Urls': input_url,
                'Output Image Urls': output_url
            })

    return output_filename
