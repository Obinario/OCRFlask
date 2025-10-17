from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
from gradio_client import Client
import json
import time
import concurrent.futures
from contextlib import contextmanager
from ml_classifier import MLClassifier

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Enable CORS for all routes
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size
OCR_TIMEOUT = 120  # 2 minutes timeout for OCR processing

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the OCR API client
try:
    ocr_client = Client("markobinario/OCRapi")
    api_available = True
    print("✅ Gradio client initialized successfully!")
except Exception as e:
    print(f"Warning: Could not initialize Gradio client: {e}")
    ocr_client = None
    api_available = False
    
    # Try fallback method
    try:
        import requests
        print("✅ Fallback requests method available")
        api_available = True
    except ImportError:
        print("❌ No OCR method available")
        api_available = False

# Initialize the ML classifier
try:
    ml_classifier = MLClassifier()
    ml_available = ml_classifier.is_model_available()
    if ml_available:
        print("✅ ML Classifier loaded successfully!")
    else:
        print("⚠️ ML Classifier not available - classification features disabled")
except Exception as e:
    print(f"Warning: Could not initialize ML classifier: {e}")
    ml_classifier = None
    ml_available = False

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def run_with_timeout(func, timeout_seconds):
    """Run a function with a timeout using concurrent.futures."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func)
        try:
            return future.result(timeout=timeout_seconds)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")

def process_pdf_with_ocr(file_path):
    """Process PDF file using the OCR API with timeout handling."""
    try:
        if not api_available:
            return None, "OCR API is not available. Please check your internet connection."
        
        # Define the OCR processing function
        def ocr_process():
            if ocr_client:
                # Use gradio client
                try:
                    # Try the direct file path approach first
                    return ocr_client.predict(
                        pdf_file=file_path,
                        api_name="/predict_1"
                    )
                except Exception as e:
                    # Fallback: try with file object
                    try:
                        with open(file_path, 'rb') as f:
                            return ocr_client.predict(
                                pdf_file=f,
                                api_name="/predict_1"
                            )
                    except Exception as e2:
                        # If both fail, raise the original error
                        raise e
            else:
                # Use requests fallback
                import requests
                try:
                    with open(file_path, 'rb') as f:
                        files = {'pdf_file': f}
                        response = requests.post(
                            "https://markobinario-ocrapi.hf.space/api/predict", 
                            files=files, 
                            timeout=OCR_TIMEOUT
                        )
                    
                    if response.status_code == 200:
                        result = response.json()
                        # Convert to expected format
                        if 'data' in result and len(result['data']) >= 3:
                            return result['data']
                        else:
                            raise Exception("Unexpected API response format")
                    else:
                        raise Exception(f"API request failed with status {response.status_code}")
                        
                except Exception as e:
                    raise Exception(f"Requests fallback failed: {str(e)}")
        
        # Run OCR processing with timeout
        result = run_with_timeout(ocr_process, OCR_TIMEOUT)
        
        # Extract results from the tuple
        extracted_text = result[0] if len(result) > 0 else ""
        detailed_results = result[1] if len(result) > 1 else "{}"
        processing_stats = result[2] if len(result) > 2 else ""
        
        # Perform ML classification if available
        classification_result = None
        status_verification = None
        
        if ml_available and ml_classifier and extracted_text:
            try:
                # Prepare text for classification (format expected by ML classifier)
                text_data = [{'text': extracted_text, 'confidence': 1.0}]
                
                # Classify the document
                classification_result = ml_classifier.classify_text(text_data)
                
                # If it's classified as a report card, verify the status
                if classification_result == "Report Card":
                    status_verification = ml_classifier.verify_report_card_status(text_data)
                
            except Exception as e:
                print(f"ML classification error: {e}")
                classification_result = "Classification error"
        
        return {
            'extracted_text': extracted_text,
            'detailed_results': detailed_results,
            'processing_stats': processing_stats,
            'classification': classification_result,
            'status_verification': status_verification,
            'success': True
        }, None
        
    except TimeoutError as e:
        return None, f"OCR processing timed out after {OCR_TIMEOUT} seconds. The PDF might be too large or complex. Please try with a smaller file."
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            return None, f"OCR processing timed out. The PDF might be too large or complex. Please try with a smaller file."
        elif "connection" in error_msg.lower():
            return None, "Connection to OCR API failed. Please check your internet connection and try again."
        else:
            return None, f"Error processing PDF: {error_msg}"

@app.route('/')
def index():
    """Main page with file upload form."""
    return render_template('index.html', api_available=api_available, ml_available=ml_available)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and OCR processing."""
    if 'file' not in request.files:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'No file selected'}), 400
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'No file selected'}), 400
        flash('No file selected')
        return redirect(request.url)
    
    if not allowed_file(file.filename):
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400
        flash('Invalid file type. Please upload a PDF file.')
        return redirect(request.url)
    
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 400
        flash('File too large. Maximum size is 16MB.')
        return redirect(request.url)
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Process with OCR
        result, error = process_pdf_with_ocr(file_path)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        if error:
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'error': error}), 500
            flash(f'Error: {error}')
            return redirect(url_for('index'))
        
        # Return results as JSON for API requests
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify(result)
        
        # For regular form submission, render with results
        return render_template('index.html', 
                             result=result, 
                             api_available=api_available,
                             ml_available=ml_available)
        
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        flash(f'Error processing file: {str(e)}')
        return redirect(url_for('index'))

@app.route('/api/process', methods=['POST'])
def api_process_pdf():
    """API endpoint for processing PDF files."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are supported.'}), 400
    
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Process with OCR
        result, error = process_pdf_with_ocr(file_path)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/api/classify', methods=['POST'])
def api_classify_text():
    """API endpoint for classifying text without OCR."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        if not text.strip():
            return jsonify({'error': 'Empty text provided'}), 400
        
        if not ml_available or not ml_classifier:
            return jsonify({'error': 'ML classifier not available'}), 503
        
        # Prepare text for classification
        text_data = [{'text': text, 'confidence': 1.0}]
        
        # Classify the text
        classification_result = ml_classifier.classify_text(text_data)
        
        # If it's classified as a report card, verify the status
        status_verification = None
        if classification_result == "Report Card":
            status_verification = ml_classifier.verify_report_card_status(text_data)
        
        return jsonify({
            'success': True,
            'classification': classification_result,
            'status_verification': status_verification
        })
        
    except Exception as e:
        return jsonify({'error': f'Error classifying text: {str(e)}'}), 500

@app.route('/api/status')
def api_status():
    """API status endpoint."""
    return jsonify({
        'status': 'healthy',
        'ocr_api_available': api_available,
        'ml_classifier_available': ml_available,
        'timestamp': time.time()
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'api_available': api_available,
        'ml_available': ml_available,
        'timestamp': time.time()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
