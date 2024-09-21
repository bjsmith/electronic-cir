

from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import uuid
from PIL import Image, ImageDraw, ImageFont
import base64
import re
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Route to display the form
@app.route('/')
def index():
    petition_question = "Do you support the proposed initiative to improve community parks?"
    return render_template('form.html', petition_question=petition_question)

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    address = request.form.get('address')
    dob = request.form.get('dob')
    petition_question = request.form.get('petition_question')

    # Generate image with the information
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    # Load a font
    font_path = '/Users/benjaminsmith/anaconda/envs/openai_chatbot/lib/python3.11/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSerifDisplay.ttf'
    
    font = ImageFont.truetype(font_path, 24)
    font = ImageFont.load_default()

    # Write the petition question and user information
    d.text((50, 50), "Petition:", font=font, fill=(0, 0, 0))
    d.text((50, 100), petition_question, font=font, fill=(0, 0, 0))
    d.text((50, 150), f"Name: {name}", font=font, fill=(0, 0, 0))
    d.text((50, 200), f"Address: {address}", font=font, fill=(0, 0, 0))
    d.text((50, 250), f"Date of Birth: {dob}", font=font, fill=(0, 0, 0))
    d.text((50, 300), "Signature:", font=font, fill=(0, 0, 0))
    d.rectangle([(50, 350), (750, 500)], outline=(0, 0, 0))

    # Generate a unique ID for the image
    image_id = str(uuid.uuid4())
    image_folder = 'static/images/signatures'
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    image_path = os.path.join(image_folder, image_id + '.png')

    # Save the image
    img.save(image_path, 'PNG')

    # Read the image and encode to base64 to embed in HTML
    with open(image_path, 'rb') as f:
        img_base64 = base64.b64encode(f.read()).decode('ascii')

    return render_template('signature.html', img_data=img_base64, image_id=image_id)

# Route to handle signature saving
@app.route('/save_signature', methods=['POST'])
def save_signature():
    data = request.get_json()
    img_data = data['img_data']
    image_id = data['image_id']

    image_folder = 'static/images'
    image_path = os.path.join(image_folder, image_id + '.png')
    signed_image_path = os.path.join(image_folder, image_id + '_signed.png')

    # Load the original image from file
    try:
        original_img = Image.open(image_path).convert('RGBA')
    except FileNotFoundError:
        return 'Original image not found.', 400

    # Process the signature image
    img_str = re.sub('^data:image/.+;base64,', '', img_data)
    img_bytes = base64.b64decode(img_str)
    signature_img = Image.open(io.BytesIO(img_bytes)).convert('RGBA')

    # Resize signature image to fit into the signature area
    signature_img = signature_img.resize((700, 150))

    # Paste the signature onto the original image at (50, 350) using the signature image as a mask
    original_img.paste(signature_img, (50, 350), signature_img)

    # Save the combined image
    original_img.save(signed_image_path, 'PNG')

    # Optionally, delete the original image
    os.remove(image_path)

    # Return success response
    return 'Signature saved successfully!', 200



# Route to display the signed petition image
@app.route('/signed_petition')
def signed_petition():
    image_id = request.args.get('image_id')
    image_folder = 'static/images'
    signed_image_path = os.path.join(image_folder, image_id + '_signed.png')
    try:
        return send_file(signed_image_path, mimetype='image/png')
    except FileNotFoundError:
        return 'Signed petition not found.', 404

if __name__ == '__main__':
    app.run(debug=True)
