from flask import Flask, render_template, request, redirect
from train_dummy_model import get_job_recommendations
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    resume = request.files['resume']
    filepath = os.path.join(UPLOAD_FOLDER, resume.filename)
    resume.save(filepath)

    # Simulated job recommendation
    recommendations = get_job_recommendations(filepath)

    return render_template('results.html', jobs=recommendations)

@app.route('/apply/<portal>')
def apply(portal):
    if portal == 'linkedin':
        return redirect('https://www.linkedin.com/jobs')
    elif portal == 'naukri':
        return redirect('https://www.naukri.com')
    else:
        return "Unknown portal", 404

if __name__ == '__main__':
    app.run(debug=True)
