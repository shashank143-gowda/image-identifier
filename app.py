from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load the pre-trained MobileNetV2 model
model = MobileNetV2(weights='imagenet')

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML file

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Load and preprocess the image
        image = Image.open(filepath).resize((224, 224))
        image_array = np.array(image)
        if image_array.shape[-1] == 4:  # Convert RGBA to RGB
            image_array = image_array[:, :, :3]
        image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
        image_array = preprocess_input(image_array)  # Preprocess for MobileNetV2
        
        # Predict the class of the image
        predictions = model.predict(image_array)
        decoded_predictions = decode_predictions(predictions, top=3)[0]  # Top 3 predictions
        
        # Format predictions
        result = [{'label': pred[1], 'confidence': float(pred[2])} for pred in decoded_predictions]
        
        return jsonify({'predictions': result, 'image_url': f'/uploads/{file.filename}'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
