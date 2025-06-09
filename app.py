import os
from flask import Flask, send_from_directory, render_template, abort, request, redirect, url_for, flash,jsonify
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this for production!

# Configuration
UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

write_file_path = "cmds.txt"
read_file_path = "responce.txt"
cmds_updated = False
responce_updated = False

@app.route('/')
def index():
    return redirect(url_for('list_files'))

@app.route('/uploads', methods=['GET', 'POST'])
def list_files():
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File uploaded successfully')
            return redirect(url_for('list_files'))
        else:
            flash('Invalid file type')
            
    # List all files
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            files.append({
                'name': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'download_url': url_for('download_file', filename=filename)
            })
    
    return render_template('file.html', files=files)

@app.route('/uploads/<filename>')
def download_file(filename):
    try:
        safe_filename = secure_filename(filename)
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            safe_filename,
            as_attachment=True
        )
    except FileNotFoundError:
        abort(404)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    print(os.path.join(UPLOAD_FOLDER, filename))
    print(f"file saved to {os.path.join(UPLOAD_FOLDER,filename)}")
    
    # Immediate response
    return jsonify({
        "status": "success",
        "filename": filename,
        "size": os.path.getsize(os.path.join(UPLOAD_FOLDER, filename))
    })



@app.route('/writecmd', methods=['POST'])
def write_to_file():
    global cmds_updated
    try:
        data = request.json.get("content", "").strip()
        if not data:
            return jsonify({"error": "No content provided"}), 400

        with open(write_file_path, "w", encoding="utf-8") as f:
            f.write(data)
        cmds_updated = True
        return jsonify({"message": "Command written successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/writeresponce', methods=['POST'])
def write_the_responce():
    global responce_updated
    try:
        data = request.json.get("content", "")
        with open(read_file_path, "w", encoding="utf-8") as f:
            f.write(data)
        responce_updated = True
        return jsonify({"message": "Response written successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/getresponce')
def get_responce():
    global responce_updated
    try:
        while not responce_updated:
            pass
        with open(read_file_path, "r") as file:
            content = file.read()
        responce_updated = False
        return content
    except Exception as e:
        return str(e), 500

@app.route('/getcmd')
def get_file():
    global cmds_updated
    try:
        if cmds_updated:
            with open(write_file_path, "r") as file:
                content = file.read().strip()
            cmds_updated = False
            return content
        return "WAITING_FOR_COMMAND"
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":

    if not os.path.exists(write_file_path):
        with open(write_file_path, 'w') as f:
            f.write('')
    if not os.path.exists(read_file_path):
        with open(read_file_path, 'w') as f:
            f.write('')
    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True
    )

if __name__ == '__main__':
    app.run(debug=True)
