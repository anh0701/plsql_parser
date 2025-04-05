from flask import Flask, request, jsonify, render_template
from SQLAnalyzer import SQLAnalyzer
import json

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    analyzer = SQLAnalyzer()
    result_table = []
    parse_tree_json = "{}"  

    if request.method == "POST":
        sql_query = request.form["sql"]
        analysis_result = analyzer.analyze(sql_query)
        result_table = analysis_result["results"]
        parse_tree_json = analysis_result["parse_tree"]

    return render_template("index.html", results=result_table, parse_tree_json=parse_tree_json)


