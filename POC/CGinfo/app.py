from flask import Flask, request, jsonify, render_template
import sys
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(root_path)

from AI.CodeGuard_AI import CodeGuard
from API.CodeGuard_Similarity import get_similarity

app = Flask(__name__)

guard = CodeGuard()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    data = request.json
    previous_code = data.get('previous_code', [])
    current_code = data.get('current_code', "")
    method = data.get('method', 'AI')
    
    if not current_code:
        return jsonify({"error": "No current code provided"}), 400
        
    weird_percent = 0
    if len(previous_code) > 0:
        if method == 'AI':
            similarity = guard.checkSubmission(previous_code, current_code)
            weird_percent = similarity
        elif method == 'Similarity':
            solutions_list = previous_code + [current_code]
            sim_scores = get_similarity(solutions_list)
            weird_percent = sim_scores[-1]
            
    return str(weird_percent)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
