"""
AI Track Masterer - Flask Web Application
Professional audio mastering powered by AI algorithms
"""

import os
import uuid
import shutil
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

import config
from audio_engine import AIMasterer, load_audio, save_audio, AudioAnalyzer

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = config.OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html',
                          presets=config.MASTERING_PRESETS,
                          formats=config.OUTPUT_FORMATS)


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)


@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Get available mastering presets"""
    return jsonify(config.MASTERING_PRESETS)


@app.route('/api/formats', methods=['GET'])
def get_formats():
    """Get available output formats"""
    return jsonify(config.OUTPUT_FORMATS)


@app.route('/api/analyze', methods=['POST'])
def analyze_audio():
    """Analyze uploaded audio file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed: {", ".join(config.ALLOWED_EXTENSIONS)}'}), 400

    # Save file temporarily
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())[:8]
    temp_filename = f"{unique_id}_{filename}"
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

    try:
        file.save(temp_path)

        # Load and analyze
        audio, sr = load_audio(temp_path)
        analyzer = AudioAnalyzer(audio, sr)
        analysis = analyzer.full_analysis()

        # Add file info
        analysis['filename'] = filename
        analysis['file_size_mb'] = os.path.getsize(temp_path) / (1024 * 1024)
        analysis['temp_id'] = unique_id

        return jsonify(analysis)

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500


@app.route('/api/master', methods=['POST'])
def master_audio():
    """Master the uploaded audio file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed: {", ".join(config.ALLOWED_EXTENSIONS)}'}), 400

    # Get options from form
    preset = request.form.get('preset', 'streaming')
    output_format = request.form.get('format', 'wav')
    noise_reduction = request.form.get('noise_reduction', 'false').lower() == 'true'
    noise_strength = float(request.form.get('noise_strength', 0.3))
    custom_output_folder = request.form.get('output_folder', '')

    # Save file temporarily
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())[:8]
    temp_filename = f"{unique_id}_{filename}"
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

    try:
        file.save(temp_path)

        # Load audio
        audio, sr = load_audio(temp_path)

        # Initialize masterer and process
        masterer = AIMasterer(preset=preset)
        analysis = masterer.analyze(audio, sr)

        mastered_audio, report = masterer.master(
            audio, sr,
            analysis=analysis,
            noise_reduction=noise_reduction,
            noise_strength=noise_strength
        )

        # Determine output path
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_mastered_{unique_id}"

        # Use custom output folder if specified and valid
        if custom_output_folder and os.path.isdir(custom_output_folder):
            output_dir = custom_output_folder
        else:
            output_dir = app.config['OUTPUT_FOLDER']

        output_path = os.path.join(output_dir, output_filename)

        # Save mastered audio
        final_path = save_audio(mastered_audio, sr, output_path, output_format)

        # Clean up temp file
        os.remove(temp_path)

        # Get final file info
        final_size = os.path.getsize(final_path) / (1024 * 1024)

        return jsonify({
            'success': True,
            'output_path': final_path,
            'output_filename': os.path.basename(final_path),
            'output_size_mb': round(final_size, 2),
            'preset_used': preset,
            'format': output_format,
            'report': report,
            'download_url': f'/api/download/{os.path.basename(final_path)}'
        })

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download a mastered file"""
    safe_filename = secure_filename(filename)
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], safe_filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)

    return jsonify({'error': 'File not found'}), 404


@app.route('/api/batch-master', methods=['POST'])
def batch_master():
    """Master multiple files at once"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400

    # Get options
    preset = request.form.get('preset', 'streaming')
    output_format = request.form.get('format', 'wav')
    noise_reduction = request.form.get('noise_reduction', 'false').lower() == 'true'
    noise_strength = float(request.form.get('noise_strength', 0.3))
    custom_output_folder = request.form.get('output_folder', '')

    results = []
    masterer = AIMasterer(preset=preset)

    for file in files:
        if file.filename == '' or not allowed_file(file.filename):
            results.append({
                'filename': file.filename,
                'success': False,
                'error': 'Invalid file or file type'
            })
            continue

        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        temp_filename = f"{unique_id}_{filename}"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

        try:
            file.save(temp_path)

            # Load and process
            audio, sr = load_audio(temp_path)
            mastered_audio, report = masterer.master(
                audio, sr,
                noise_reduction=noise_reduction,
                noise_strength=noise_strength
            )

            # Output path
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}_mastered_{unique_id}"

            if custom_output_folder and os.path.isdir(custom_output_folder):
                output_dir = custom_output_folder
            else:
                output_dir = app.config['OUTPUT_FOLDER']

            output_path = os.path.join(output_dir, output_filename)
            final_path = save_audio(mastered_audio, sr, output_path, output_format)

            os.remove(temp_path)

            results.append({
                'filename': filename,
                'success': True,
                'output_path': final_path,
                'output_filename': os.path.basename(final_path),
                'download_url': f'/api/download/{os.path.basename(final_path)}'
            })

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            results.append({
                'filename': filename,
                'success': False,
                'error': str(e)
            })

    successful = sum(1 for r in results if r.get('success'))
    return jsonify({
        'total': len(results),
        'successful': successful,
        'failed': len(results) - successful,
        'results': results
    })


@app.route('/api/list-output', methods=['GET'])
def list_output_files():
    """List all mastered files in output folder"""
    output_folder = app.config['OUTPUT_FOLDER']
    files = []

    for filename in os.listdir(output_folder):
        filepath = os.path.join(output_folder, filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            files.append({
                'filename': filename,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'download_url': f'/api/download/{filename}'
            })

    files.sort(key=lambda x: x['created'], reverse=True)
    return jsonify(files)


@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a mastered file"""
    safe_filename = secure_filename(filename)
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], safe_filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': True, 'message': f'Deleted {filename}'})

    return jsonify({'error': 'File not found'}), 404


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'output_folder': app.config['OUTPUT_FOLDER']
    })


if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    print("\n" + "="*60)
    print("  AI Track Masterer")
    print("  Professional Audio Mastering powered by AI")
    print("="*60)
    print(f"  Server running at: http://localhost:5000")
    print(f"  Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"  Output folder: {app.config['OUTPUT_FOLDER']}")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
