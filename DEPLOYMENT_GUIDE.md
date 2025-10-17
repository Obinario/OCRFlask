# Render.com Deployment Guide

This guide will help you deploy the OCR ML API to Render.com.

## Prerequisites

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Render.com Account**: Sign up at [render.com](https://render.com)
3. **Model Files**: Ensure your ML models are in the `models/` directory

## Step 1: Prepare Your Repository

Make sure your repository contains:
```
├── app.py                 # Main Flask application
├── ml_classifier.py      # ML classification module
├── auto_train.py         # Automated training system
├── requirements.txt       # Python dependencies
├── render.yaml           # Render configuration
├── Procfile              # Process file
├── wsgi.py              # WSGI entry point
├── models/               # ML model files
│   ├── auto_report_card_model.pkl
│   └── auto_vectorizer.pkl
└── templates/            # HTML templates
    └── index.html
```

## Step 2: Deploy to Render.com

### Option A: Using render.yaml (Recommended)

1. **Push to GitHub**: Commit and push all files to your GitHub repository
2. **Connect to Render**: 
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

### Option B: Manual Configuration

1. **Create New Web Service**:
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Settings**:
   - **Name**: `ocr-ml-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: Free (or upgrade as needed)

3. **Environment Variables**:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: (auto-generated)

## Step 3: Verify Deployment

1. **Check Build Logs**: Ensure all dependencies install successfully
2. **Test Health Endpoint**: Visit `https://your-app-name.onrender.com/health`
3. **Test API**: Use the provided API documentation

## Step 4: API Usage

Once deployed, your API will be available at:
```
https://your-app-name.onrender.com
```

### Test the API:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Process PDF (replace with your actual file)
curl -X POST -F "file=@test.pdf" https://your-app-name.onrender.com/api/process

# Classify text
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"This is a report card"}' \
  https://your-app-name.onrender.com/api/classify
```

## Step 5: Web Integration

Use the API in your web application:

```javascript
// Example: Process PDF file
async function processPDF(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('https://your-app-name.onrender.com/api/process', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log('Classification:', result.data.classification);
    console.log('Status:', result.data.status_verification);
    return result.data;
  } else {
    console.error('Error:', result.error);
  }
}

// Example: Classify text
async function classifyText(text) {
  const response = await fetch('https://your-app-name.onrender.com/api/classify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ text: text })
  });
  
  const result = await response.json();
  return result;
}
```

## Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check `requirements.txt` for version conflicts
   - Ensure all dependencies are compatible
   - Check build logs for specific errors

2. **Model Loading Issues**:
   - Ensure model files are in the `models/` directory
   - Check file permissions
   - Verify model files are committed to Git

3. **API Timeouts**:
   - OCR processing can take 30-120 seconds
   - Consider implementing client-side progress indicators
   - Use the `/api/status` endpoint to check service health

4. **CORS Issues**:
   - CORS is enabled by default
   - If issues persist, check your domain configuration

### Performance Tips:

1. **Free Tier Limitations**:
   - 100 requests per hour
   - Services sleep after 15 minutes of inactivity
   - Consider upgrading for production use

2. **Optimization**:
   - Use smaller PDF files when possible
   - Implement client-side file validation
   - Cache results when appropriate

## Monitoring

1. **Health Checks**: Use `/health` and `/api/status` endpoints
2. **Logs**: Monitor application logs in Render dashboard
3. **Metrics**: Track API usage and performance

## Security Considerations

1. **API Keys**: The OCR API doesn't require authentication
2. **File Uploads**: Files are automatically cleaned up after processing
3. **Rate Limiting**: Implement client-side rate limiting
4. **HTTPS**: All traffic is encrypted by default on Render

## Support

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com)
- **API Documentation**: See `API_DOCUMENTATION.md`
