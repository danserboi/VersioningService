from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import os
import re
from constants import VERSIONING_SERVICE_PORT, CREATE_FILE_ENDPOINT, UPDATE_FILE_ENDPOINT, DOWNLOAD_FILE_ENDPOINT, DELETE_FILE_ENDPOINT, NUMBER_OF_FILES_ENDPOINT, MATCH_FILENAME_ENDPOINT

app = Flask(__name__)
filepath_no_versions_dict = {}
storage_item_extension = ".extension"

@app.route(CREATE_FILE_ENDPOINT, methods=['POST'])
def create_file():
    try:
        filepath = request.args.get('filename')
        new_file = request.files['file']

        if filepath and new_file:
            secure_filename(filepath)
            
            if filepath in filepath_no_versions_dict:
                return jsonify({"error": "file already exists"}), 400
            else:
                filepath_no_versions_dict[filepath] = 0
                os.makedirs(os.getcwd() + "/" + filepath.rsplit("/", 1)[0], exist_ok=True)
                new_file.save(filepath + "_" + str(filepath_no_versions_dict[filepath]))

            return jsonify({"version": filepath_no_versions_dict[filepath]}), 201
        else:
            return jsonify({"error": "bad parameters"}), 400

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@app.route(UPDATE_FILE_ENDPOINT, methods=['PUT'])
def update_file():
    try:
        filepath = request.args.get('filename')
        updated_file = request.files['file']
        if filepath and updated_file:
            secure_filename(filepath)
            if filepath in filepath_no_versions_dict:
                filepath_no_versions_dict[filepath] += 1
                updated_file.save(filepath + "_" + str(filepath_no_versions_dict[filepath]))
            else:
                return jsonify({"error": "file haven't been created"}), 400
            
            return jsonify({"version": filepath_no_versions_dict[filepath]}), 200
        else:
            return jsonify({"error": "bad parameters"}), 400

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@app.route(DOWNLOAD_FILE_ENDPOINT, methods=['GET'])
def read_file():
    try:
        filepath = request.args.get('filename')
        version  = request.args.get('version')
        if filepath and version:
            return send_file(os.getcwd() + "/" + filepath + "_" + version)
        else:
            return jsonify({"error": "bad parameters"}), 400

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@app.route(DELETE_FILE_ENDPOINT, methods=['DELETE'])
def delete_file():
    try:
        filepath = request.args.get('filename')
        if filepath:
            for i in range(filepath_no_versions_dict[filepath] + 1):
                os.remove(os.getcwd() + "/" + filepath + "_" + str(i))
            del filepath_no_versions_dict[filepath]
            return jsonify({"message": f"File {filepath} deleted successfully."}), 200
        else:
            return jsonify({"error": "bad parameter"}), 400

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500


@app.route(NUMBER_OF_FILES_ENDPOINT, methods=['GET'])
def get_number_of_files():
    try:
        return jsonify({"number_of_files": len(filepath_no_versions_dict)}), 200

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

@app.route(MATCH_FILENAME_ENDPOINT, methods=['GET'])
def get_files_matching_regex():
    try:
        regexp = request.args.get('regexp')
        matches = []
        if regexp:
            for key in list(filepath_no_versions_dict.keys()):
                key = key.rsplit("/", 1)[1]
                key = key[:-len(storage_item_extension)]
                if re.match(regexp, key):
                    matches.append(key)
            return jsonify({"files_matching_regex": matches}), 200
        else:
            return jsonify({"error": "bad parameter"}), 400

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
   app.run(port=VERSIONING_SERVICE_PORT)