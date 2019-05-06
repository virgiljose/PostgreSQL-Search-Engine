from flask import Flask, render_template, request

import search

application = app = Flask(__name__)
app.debug = True

@app.route('/search', methods=["GET"])
def dosearch():
    query = request.args['query']
    qtype = 'and' if 'query_type' not in request.args else request.args['query_type']
    offset = 1 if 'offset' not in request.args else request.args['offset']

    search_results, qlen = search.search(query, qtype, offset)
    return render_template('results.html',
            query=query,
            offset=int(offset),
            qtype=qtype,
            results=qlen,
            search_results=search_results)

@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        pass
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
