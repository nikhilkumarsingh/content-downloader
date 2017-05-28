#!flask/bin/python
from __future__ import print_function
import sys
from flask import Flask, jsonify, request, make_response, abort

import site

def get_main_path():
    test_path = sys.path[0] # sys.path[0] is current path in 'examples' subdirectory
    split_on_char = "/"
    return split_on_char.join(test_path.split(split_on_char)[:-1])
main_path = get_main_path()
site.addsitedir(main_path+'/examples')
site.addsitedir(main_path+'/ctdl')
print ("Imported subfolder: %s" % (main_path+'/examples') )
print ("Imported subfolder: %s" % (main_path+'/ctdl') )

import ctdl
from ctdl.ctdl import main

"""
RESTful web service endpoints using Flask.
"""
app = Flask(__name__)

@app.route('/api/v1.0/query', methods=['GET'])
def get_query():
    """
    Main Examples:
        curl -i "http://localhost:5000/api/v1.0/query?query=None&file_type=pdf&limit=10&directory=None&parallel=False&available=False&threats=False&min_file_size=0&max_file_size=-1&no_redirects=False"
        curl -i "http://localhost:5000/api/v1.0/query?query=dogs,cats&file_type=pdf&limit=5&directory=None&parallel=True&available=False&threats=False&min_file_size=0&max_file_size=-1&no_redirects=True"
    """
    query_params = request.args.to_dict()
    if len(query_params) == 0:
        abort(400)
    print("Query Params: ", query_params, file=sys.stderr)

    def process_ctdl(query_params):
        main(query_params)
    process_ctdl(query_params)

    return jsonify({'success':True}), 200, {'ContentType':'application/json'}

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, use_debugger=False, use_reloader=False)