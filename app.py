from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

write_file_path = "cmds.txt"
read_file_path = "responce.txt"
cmds_updated = False
responce_updated = False

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuration for large files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024  # 16GB max
app.config['UPLOAD_BUFFER_SIZE'] = 16 * 1024 * 1024  # 16MB buffer

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    print(f"file saved to {os.path.join(UPLOAD_FOLDER,filename)}")
    
    # Immediate response
    return jsonify({
        "status": "success",
        "filename": filename,
        "size": os.path.getsize(os.path.join(UPLOAD_FOLDER, filename))
    })


# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
    
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
    
#     filename = secure_filename(file.filename)
#     file.save(os.path.join(UPLOAD_FOLDER, filename))
#     return jsonify({
#         "success": True,
#         "filename": filename,
#         "size": os.path.getsize(os.path.join(UPLOAD_FOLDER, filename))
#     })
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file provided"}), 400
    
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
    
#     if file:
#         file.save(os.path.join(UPLOAD_FOLDER, file.filename))
#         return jsonify({"message": "File uploaded successfully", "filename": file.filename}), 200


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
