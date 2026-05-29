"""
COMPLETE Flask Backend - AI Skin Detector
Integrates: enhanced analysis, context-aware chatbot, professional reports
"""
import os
import uuid
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='templates')

# ──────────────────────────────────────────────────────────────────────
#  FOLDER SETUP
# ──────────────────────────────────────────────────────────────────────
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
HISTORY_FOLDER = 'history'

for folder in [UPLOAD_FOLDER, RESULT_FOLDER, HISTORY_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ──────────────────────────────────────────────────────────────────────
#  ROUTES
# ──────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/results/<filename>')
def result_file(filename):
    """Serve result images"""
    return send_from_directory(RESULT_FOLDER, filename)

@app.route('/upload', methods=['POST'])
def upload():
    """
    MAIN ANALYSIS ENDPOINT
    - Accepts image upload
    - Runs enhanced skin analysis
    - Returns detailed results + acne_details for chatbot context
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use JPG, PNG, or WEBP'}), 400
    
    try:
        # Save uploaded file
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = uuid.uuid4().hex + '.' + ext
        upload_path = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(upload_path)
        
        # Run ENHANCED analysis
        from skin_analysis import analyze_skin
        result = analyze_skin(upload_path)
        
        if result is None:
            return jsonify({
                'error': 'Analysis failed. Make sure your face is clearly visible.'
            }), 500
        
        # Save to history
        save_to_history(result, unique_name)
        
        # Return results + detailed acne data for AI context
        return jsonify({
            'skin_score': result['skin_score'],
            'acne_count': result['acne_count'],
            'severity': result['severity'],
            'acne_details': result.get('acne_details', {}),  # NEW: Send detailed data
            'recommendations': result['recommendations'],
            'original_url': '/uploads/' + unique_name,
            'result_url': '/results/' + os.path.basename(result['result_path'])
        })
    
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """
    AI CHATBOT ENDPOINT
    NOW CONTEXT-AWARE based on actual skin analysis
    """
    data = request.get_json()
    question = data.get('question', '').strip()
    skin_score = data.get('skin_score', 0)
    severity = data.get('severity', 'Unknown')
    acne_count = data.get('acne_count', 0)
    acne_details = data.get('acne_details', {})  # NEW: Receive detailed data
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        from ai_advisor import get_ai_advice
        
        # Pass acne_details so the AI can be more specific
        reply = get_ai_advice(
            skin_score=skin_score,
            acne_count=acne_count,
            severity=severity,
            question=question,
            acne_details=acne_details  # NEW: Pass rich context
        )
        return jsonify({'reply': reply})
    
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'reply': 'AI advisor unavailable. Check your ANTHROPIC_API_KEY.'})

@app.route('/report', methods=['POST'])
def report():
    """
    PDF REPORT GENERATION ENDPOINT
    Now includes detailed metrics and professional layout
    """
    data = request.get_json()
    
    try:
        from report_generator import generate_report
        
        pdf_path = generate_report(
            skin_score=data.get('skin_score', 0),
            acne_count=data.get('acne_count', 0),
            severity=data.get('severity', 'Unknown'),
            recommendations=data.get('recommendations', []),
            acne_details=data.get('acne_details', {}),  # NEW
            original_url=data.get('original_url', ''),
            result_url=data.get('result_url', '')
        )
        
        return send_from_directory(
            os.path.dirname(os.path.abspath(pdf_path)),
            os.path.basename(pdf_path),
            as_attachment=True,
            download_name='SkinAI_Report.pdf'
        )
    
    except Exception as e:
        print(f"Report error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def history():
    """Get user's scan history"""
    try:
        hfile = os.path.join(HISTORY_FOLDER, 'history.json')
        if not os.path.exists(hfile):
            return jsonify([])
        with open(hfile, 'r') as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

def save_to_history(result, original_filename):
    """Save scan to history file"""
    try:
        hfile = os.path.join(HISTORY_FOLDER, 'history.json')
        history = []
        
        if os.path.exists(hfile):
            with open(hfile, 'r') as f:
                history = json.load(f)
        
        history.insert(0, {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'skin_score': result['skin_score'],
            'acne_count': result['acne_count'],
            'severity': result['severity'],
            'result_url': '/results/' + os.path.basename(result['result_path']),
            'original_url': '/uploads/' + original_filename
        })
        
        # Keep only last 20 scans
        history = history[:20]
        
        with open(hfile, 'w') as f:
            json.dump(history, f, indent=2)
    
    except Exception as e:
        print(f"History save error: {e}")

# ──────────────────────────────────────────────────────────────────────
#  ERROR HANDLERS
# ──────────────────────────────────────────────────────────────────────

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Max 10MB'}), 413

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

# ──────────────────────────────────────────────────────────────────────
#  RUN
# ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)