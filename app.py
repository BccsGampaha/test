from flask import Flask, request, jsonify

app = Flask(__name__)

write_file_path = "cmds.txt"
read_file_path = "responce.txt"
cmds_updated = False
responce_updated = False

@app.route('/writecmd', methods=['POST'])
def write_to_file():
    global cmds_updated
    data = request.json.get("content")
    if not data:
        return jsonify({"error": "No content provided"}), 400

    try:
        with open(write_file_path, "w", encoding="utf-8") as f:
            f.write(data)
        cmds_updated = True
        return jsonify({"message": "File cmds_updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/writeresponce', methods=['POST'])
def write_the_responce():
    global responce_updated
    data = request.json.get("content")
    if not data:
        return jsonify({"error": "No content provided"}), 400

    try:
        with open("responce.txt", "w", encoding="utf-8") as f:
            f.write(data)
        responce_updated = True
        return jsonify({"message": "File responce_updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/getresponce')
def get_responce():
    global responce_updated
    while not responce_updated:
        if responce_updated:
            break
    with open("responce.txt", "r") as file:
        command = file.readlines()
        # print(command)
    responce_updated = False
    return command


@app.route('/getcmd')
def get_file():
    global cmds_updated
    if cmds_updated:
        with open("cmds.txt", "r") as file:
            command = file.readlines()
            # print(command)
        cmds_updated = False
        return command[-1]
    else:
        return "NOT UPDATED BY THE USER"


if __name__ == "__main__":
    app.run(host='0.0.0.0')
