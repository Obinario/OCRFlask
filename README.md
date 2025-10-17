# PDF OCR Text Extractor with ML Classification

A web-based application that extracts text from PDF files using the markobinario/OCRapi and automatically classifies documents using machine learning. This application provides a modern, user-friendly interface for uploading PDF files, extracting text, and performing intelligent document classification.

## Features

- **Modern Web Interface**: Clean, responsive design with drag-and-drop file upload
- **PDF OCR Processing**: Uses the markobinario/OCRapi for accurate text extraction
- **ML Document Classification**: Automatically classifies documents as "Report Card" or "Not Report Card"
- **Report Card Analysis**: For report cards, analyzes pass/fail status with detailed remarks
- **Real-time Results**: Displays extracted text, classification results, and processing statistics
- **File Validation**: Ensures only PDF files up to 16MB are processed
- **Copy to Clipboard**: Easy copying of extracted text and JSON results
- **Error Handling**: Comprehensive error handling and user feedback

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your web browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Upload a PDF file**:
   - Click "Choose PDF File" or drag and drop a PDF file
   - Maximum file size: 16MB
   - Only PDF files are supported

2. **Extract text and classify**:
   - Click "Extract Text" button
   - Wait for processing (may take a few moments)
   - View the results in multiple sections:
     - **Document Classification**: ML-powered classification (Report Card/Not Report Card)
     - **Status Analysis**: For report cards, shows pass/fail status with detailed remarks
     - **Extracted Text**: Plain text output
     - **Detailed OCR Results**: JSON format with detailed information
     - **Processing Statistics**: Performance metrics

3. **Copy results**:
   - Use the "Copy" buttons to copy text or JSON to clipboard

## API Integration

This application uses the `markobinario/OCRapi` through the `gradio_client` library. The API provides:

- **Endpoint**: `/predict_1` (100% success rate)
- **Input**: PDF file
- **Output**: Tuple containing:
  - Extracted text (string)
  - Detailed OCR results (JSON string)
  - Processing statistics (Markdown string)

## ML Classification

The application includes an integrated ML classifier that:

- **Document Classification**: Uses trained models to classify documents as "Report Card" or "Not Report Card"
- **Status Verification**: For report cards, analyzes text to determine pass/fail status
- **Model Loading**: Automatically loads trained models from `models/` directory
- **Fallback Support**: Works with or without ML models (graceful degradation)

## File Structure

```
├── app.py                 # Main Flask application
├── ml_classifier.py      # ML classification module
├── auto_train.py         # Automated training system
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # HTML template
├── static/
│   └── style.css         # CSS styling
├── models/               # ML model files (auto-created)
└── uploads/              # Temporary file storage (auto-created)
```

## Configuration

- **File size limit**: 16MB (configurable in `app.py`)
- **Allowed file types**: PDF only
- **Port**: 5000 (default Flask port)
- **Host**: 0.0.0.0 (accessible from any IP)

## Error Handling

The application includes comprehensive error handling for:

- Invalid file types
- File size limits
- API connectivity issues
- Processing errors
- Network timeouts

## Requirements

- Python 3.7+
- Internet connection (for OCR API)
- Modern web browser

## Troubleshooting

1. **"OCR API Unavailable" message**:
   - Check your internet connection
   - The markobinario/OCRapi service might be temporarily down

2. **File upload issues**:
   - Ensure the file is a PDF
   - Check file size is under 16MB
   - Try refreshing the page

3. **Processing errors**:
   - Wait a few moments and try again
   - Check if the PDF file is corrupted
   - Ensure the file is not password-protected

## API Documentation

The application uses the markobinario/OCRapi with the following specifications:

- **API Name**: `/predict_1`
- **Success Rate**: 100%
- **Average Processing Time**: ~47 seconds
- **Input**: PDF file (FileData object)
- **Output**: Tuple of 3 elements (text, JSON, statistics)

For more information about the API, visit the [API documentation](https://huggingface.co/spaces/markobinario/OCRapi).

## License

This project is open source and available under the MIT License.
