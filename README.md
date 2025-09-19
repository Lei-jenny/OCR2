# OCR Menu Detector

A web application that uses OCR (Optical Character Recognition) to extract menu items from images and provides translation capabilities. Built with Flask, OpenCV, and Tesseract OCR.

## Features

- 📷 **Camera Integration**: Take photos directly from your device
- 📁 **File Upload**: Upload menu images from your device
- 🔍 **OCR Processing**: Extract text from menu images using Tesseract
- 🌍 **Language Detection**: Automatically detect the language of menu text
- 🔄 **Translation**: Translate menu items to multiple languages
- 📱 **Responsive Design**: Works on desktop and mobile devices
- ☁️ **Serverless Ready**: Configured for Vercel deployment

## Technology Stack

- **Backend**: Flask (Python)
- **OCR**: Tesseract OCR with pytesseract
- **Image Processing**: OpenCV
- **Translation**: Google Translate API
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Vercel (Serverless)

## Project Structure

```
ocr-menu-detector/
├── api/
│   ├── __init__.py
│   └── ocr.py              # Main Flask application
├── templates/
│   └── index.html          # Frontend interface
├── tests/
│   ├── test_ocr.py         # Unit tests
│   ├── sample_menu.jpg     # Test menu image
│   └── multilingual_menu.jpg
├── create_test_image.py    # Script to generate test images
├── requirements.txt        # Python dependencies
├── package.json           # Node.js configuration
├── vercel.json           # Vercel deployment config
└── README.md             # This file
```

## 🚀 Quick Deploy to Vercel

1. **Upload to GitHub**:
   ```bash
   python setup_git.py  # Run this script to set up Git
   # Follow the instructions to create GitHub repository
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Deploy automatically!

📖 **Detailed instructions**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## Installation & Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ocr-menu-detector
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**
   
   **Windows:**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH or set TESSDATA_PREFIX environment variable
   
   **macOS:**
   ```bash
   brew install tesseract
   ```
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get install tesseract-ocr
   ```

4. **Run the application**
   ```bash
   python api/ocr.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**
   ```bash
   vercel
   ```

3. **Configure environment variables** (if needed)
   - Go to your Vercel dashboard
   - Add any required environment variables

## API Endpoints

### POST /api/ocr
Process a menu image and return extracted menu items with translations.

**Request:**
- `file`: Image file (multipart/form-data)
- `target_lang`: Target language code (optional, default: 'en')

**Response:**
```json
{
  "success": true,
  "detected_language": "en",
  "target_language": "es",
  "confidence": 85.5,
  "raw_text": "Caesar Salad $12.99...",
  "menu_items": [
    {
      "name": "Caesar Salad",
      "description": "Fresh romaine lettuce with parmesan cheese",
      "price": "$12.99",
      "name_translated": "Ensalada César",
      "description_translated": "Lechuga romana fresca con queso parmesano",
      "full_text": "Caesar Salad - Fresh romaine lettuce with parmesan cheese $12.99"
    }
  ],
  "total_items": 1
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "OCR Menu Detector"
}
```

## Usage

1. **Upload an Image**
   - Click "Choose File" or drag and drop a menu image
   - Supported formats: JPG, PNG, GIF, BMP, TIFF

2. **Take a Photo**
   - Click "Start Camera" to access your device camera
   - Click "Capture Photo" to take a picture
   - Click "Stop Camera" when done

3. **Select Target Language**
   - Choose the language you want to translate to
   - Default is English

4. **Process Image**
   - Click "Process Image" to analyze the menu
   - Wait for the OCR processing to complete

5. **View Results**
   - See detected language and confidence score
   - Browse extracted menu items with translations
   - View original and translated text

## Testing

Run the unit tests:

```bash
python -m pytest tests/
```

Or run specific test file:

```bash
python tests/test_ocr.py
```

## Configuration

### Environment Variables

- `TESSDATA_PREFIX`: Path to Tesseract data files (if not in PATH)
- `UPLOAD_FOLDER`: Directory for temporary file uploads (default: `/tmp/uploads`)

### OCR Configuration

The application uses multiple OCR configurations for better accuracy:
- `--oem 3 --psm 6`: Uniform block of text
- `--oem 3 --psm 4`: Single column of text  
- `--oem 3 --psm 3`: Fully automatic page segmentation

## Supported Languages

The application can detect and translate between:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)
- Arabic (ar)
- Hindi (hi)

## Troubleshooting

### Common Issues

1. **Tesseract not found**
   - Ensure Tesseract is installed and in your PATH
   - Set TESSDATA_PREFIX environment variable

2. **Poor OCR results**
   - Use high-quality, well-lit images
   - Ensure text is clearly visible and not rotated
   - Try different image formats

3. **Translation errors**
   - Check internet connection
   - Verify target language code is supported

4. **Camera not working**
   - Ensure HTTPS is enabled (required for camera access)
   - Check browser permissions for camera access

### Performance Tips

- Use images with high contrast between text and background
- Ensure text is horizontal and not rotated
- Crop images to focus on menu content
- Use images with resolution between 300-600 DPI

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [OpenCV](https://opencv.org/)
- [Google Translate](https://translate.google.com/)
- [Flask](https://flask.palletsprojects.com/)
- [Vercel](https://vercel.com/)
