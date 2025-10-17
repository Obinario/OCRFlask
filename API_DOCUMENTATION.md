# OCR ML API Documentation

This API provides OCR text extraction and ML document classification services.

## Base URL
```
https://your-app-name.onrender.com
```

## Endpoints

### 1. Process PDF File
**POST** `/api/process`

Upload a PDF file for OCR processing and ML classification.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: PDF file in 'file' field

**Response:**
```json
{
  "success": true,
  "data": {
    "extracted_text": "Extracted text from PDF...",
    "detailed_results": "JSON string with detailed OCR results",
    "processing_stats": "Processing statistics",
    "classification": "Report Card" or "Not Report Card",
    "status_verification": {
      "status": "passed" or "failed" or "unknown",
      "message": "Status message"
    },
    "success": true
  }
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

### 2. Classify Text
**POST** `/api/classify`

Classify text without OCR processing.

**Request:**
```json
{
  "text": "Text to classify"
}
```

**Response:**
```json
{
  "success": true,
  "classification": "Report Card" or "Not Report Card",
  "status_verification": {
    "status": "passed" or "failed" or "unknown",
    "message": "Status message"
  }
}
```

### 3. API Status
**GET** `/api/status`

Check API health and component availability.

**Response:**
```json
{
  "status": "healthy",
  "ocr_api_available": true,
  "ml_classifier_available": true,
  "timestamp": 1234567890.123
}
```

### 4. Health Check
**GET** `/health`

Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "api_available": true,
  "ml_available": true,
  "timestamp": 1234567890.123
}
```

## Usage Examples

### JavaScript/Fetch
```javascript
// Process PDF file
const formData = new FormData();
formData.append('file', pdfFile);

fetch('https://your-app-name.onrender.com/api/process', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Classification:', data.data.classification);
  console.log('Status:', data.data.status_verification);
});

// Classify text
fetch('https://your-app-name.onrender.com/api/classify', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'Your text to classify'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Classification:', data.classification);
});
```

### Python/Requests
```python
import requests

# Process PDF file
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('https://your-app-name.onrender.com/api/process', files=files)
    data = response.json()
    print(f"Classification: {data['data']['classification']}")

# Classify text
response = requests.post('https://your-app-name.onrender.com/api/classify', 
                       json={'text': 'Your text to classify'})
data = response.json()
print(f"Classification: {data['classification']}")
```

### cURL
```bash
# Process PDF file
curl -X POST \
  -F "file=@document.pdf" \
  https://your-app-name.onrender.com/api/process

# Classify text
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"Your text to classify"}' \
  https://your-app-name.onrender.com/api/classify
```

## Error Codes

- **400**: Bad Request (invalid file type, missing data)
- **500**: Internal Server Error (processing error)
- **503**: Service Unavailable (ML classifier not available)

## Rate Limits

- Free tier: 100 requests per hour
- File size limit: 16MB
- Supported formats: PDF only

## CORS

The API supports CORS for web applications. All origins are allowed by default.
