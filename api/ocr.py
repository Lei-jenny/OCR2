import os
import cv2
import numpy as np
import pytesseract
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import json
import re
from googletrans import Translator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='../templates')

# Configuration
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize translator
translator = Translator()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image):
    """Preprocess image for better OCR results"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Morphological operations to clean up the image
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return cleaned

def detect_language(text):
    """Detect the language of the text"""
    try:
        # Use Google Translate to detect language
        detection = translator.detect(text)
        return detection.lang
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
        return 'unknown'

def extract_menu_items(text):
    """Extract potential menu items from OCR text"""
    # Split text into lines and clean them
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    menu_items = []
    current_item = {}
    
    for line in lines:
        # Skip very short lines (likely noise)
        if len(line) < 3:
            continue
            
        # Check if line contains price (common patterns)
        price_pattern = r'[\$€£¥₹]\s*\d+(?:\.\d{2})?|\d+(?:\.\d{2})?\s*[\$€£¥₹]|\d+(?:\.\d{2})?\s*(?:USD|EUR|GBP|JPY|INR)'
        has_price = bool(re.search(price_pattern, line))
        
        # Check if line looks like a description (longer text, no price)
        is_description = len(line) > 20 and not has_price
        
        if has_price and current_item:
            # This line has a price, complete the current item
            current_item['price'] = re.search(price_pattern, line).group()
            current_item['full_text'] = current_item.get('name', '') + ' ' + line
            menu_items.append(current_item)
            current_item = {}
        elif is_description and not current_item:
            # This looks like a description, start a new item
            current_item = {'description': line}
        elif not has_price and not is_description:
            # This looks like an item name
            if current_item:
                current_item['name'] = line
            else:
                current_item = {'name': line}
    
    # Add the last item if it exists
    if current_item:
        menu_items.append(current_item)
    
    return menu_items

def translate_text(text, target_lang='en'):
    """Translate text to target language"""
    try:
        if target_lang == 'en':
            return text  # Already in English or no translation needed
        
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
        return text

@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    """Main OCR endpoint for processing menu images"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Get target language from request
        target_lang = request.form.get('target_lang', 'en')
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Read and preprocess image
            image = cv2.imread(filepath)
            if image is None:
                return jsonify({'error': 'Could not read image file'}), 400
            
            processed_image = preprocess_image(image)
            
            # Perform OCR with multiple languages
            # Try different OCR configurations for better results
            ocr_configs = [
                '--oem 3 --psm 6',  # Uniform block of text
                '--oem 3 --psm 4',  # Single column of text
                '--oem 3 --psm 3',  # Fully automatic page segmentation
            ]
            
            best_text = ""
            best_confidence = 0
            
            for config in ocr_configs:
                try:
                    # Get OCR data with confidence scores
                    data = pytesseract.image_to_data(processed_image, config=config, output_type=pytesseract.Output.DICT)
                    
                    # Calculate average confidence
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Get text
                    text = pytesseract.image_to_string(processed_image, config=config)
                    
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_text = text
                        
                except Exception as e:
                    logger.warning(f"OCR config {config} failed: {e}")
                    continue
            
            if not best_text.strip():
                return jsonify({'error': 'No text detected in image'}), 400
            
            # Detect language
            detected_lang = detect_language(best_text)
            
            # Extract menu items
            menu_items = extract_menu_items(best_text)
            
            # Translate menu items if target language is specified
            if target_lang != 'en' and detected_lang != target_lang:
                for item in menu_items:
                    for key in ['name', 'description']:
                        if key in item:
                            item[f'{key}_translated'] = translate_text(item[key], target_lang)
            
            # Prepare response
            response = {
                'success': True,
                'detected_language': detected_lang,
                'target_language': target_lang,
                'confidence': best_confidence,
                'raw_text': best_text,
                'menu_items': menu_items,
                'total_items': len(menu_items)
            }
            
            return jsonify(response)
            
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'OCR Menu Detector'})

@app.route('/', methods=['GET'])
def index():
    """Serve the main page"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
