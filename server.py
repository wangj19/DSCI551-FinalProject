# More details at: 
#     https://flask.palletsprojects.com/en/2.2.x/

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/', defaults={'myPath': ''}, )
@app.route('/<path:myPath>', methods=['PUT'])
def catch_all_put(myPath):
    resp = {"database": request.url_root,
        "path": request.path,
        "full path": request.full_path,
        "data": request.get_data().decode('utf-8')}

    print(resp)

    return jsonify(resp)

@app.route('/', defaults={'myPath': ''})
@app.route('/<path:myPath>', methods=['GET'])
def catch_all_get(myPath):
    resp = {"database": request.url_root,
        "path": request.path,
        "full path": request.full_path}

    print(resp)

    return jsonify(resp)


app.run(debug=True)


 