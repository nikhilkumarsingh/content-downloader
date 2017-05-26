#!flask/bin/python
from __future__ import print_function
import sys
from flask import Flask, jsonify, request, make_response, abort
import ctdl
from ctdl import main

"""
RESTful web service endpoints using Flask.
"""
app = Flask(__name__)

tasks = [
    {
        'id': 1
    },
    {
        'id': 2
    }
]

@app.route('/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    """
    Demo Examples:
        "curl -i http://localhost:5000/api/v1.0/tasks"
    """
    return jsonify({'tasks': tasks})

@app.route('/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    Demo Examples:
        "curl -i http://localhost:5000/api/v1.0/tasks/1"
        "curl -i http://localhost:5000/api/v1.0/tasks/2"
    """
    query_params = request.args.to_dict()
    print("Specific Task: ", task_id, file=sys.stderr)
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'tasks': task[0]})

@app.route('/api/v1.0/query', methods=['GET'])
def get_query():
    """
    Demo Examples:
        curl -i "http://localhost:5000/api/v1.0/query?id=1"
        curl -i "http://localhost:5000/api/v1.0/query?id=2"

    Main Examples:
        curl -i "http://localhost:5000/api/v1.0/query?query=None&file_type=pdf&limit=10&directory=None&parallel=False&available=False&threats=False&min_file_size=0&max_file_size=-1&no_redirects=False"
    """
    query_params = request.args.to_dict()
    if len(query_params) == 0:
        abort(400)
    print("Query Params: ", query_params, file=sys.stderr)

    def process_ctdl(query_params):
        ctdl.main(query_params)
    process_ctdl(query_params)

    task_match = {}
    for index, elem in enumerate(tasks):
        if len(elem):
            for key, val in elem.items():
                if 'id' in query_params and val == int(query_params['id']):
                    task_match = elem
    print("Matching Task: ", task_match, file=sys.stderr)
    return jsonify({'task_match': task_match})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, use_debugger=False, use_reloader=False)