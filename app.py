import os
import json
import re
from flask import Flask, request, jsonify, render_template, Response
import google.generativeai as genai
from dotenv import load_dotenv
import PyPDF2
import docx
from flask_cors import CORS # Import CORS
from flask import Flask, render_template, request, redirect, url_for, session
import os





# --- Load Environment ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app) # Enable CORS for all routes - IMPORTANT for frontend calls
last_job_domains = [] # Stores job domains from the last successful resume upload

# --- Extract Text from Resume ---
def extract_text_from_resume(file):
    ext = file.filename.split('.')[-1].lower()
    try:
        if ext == 'pdf':
            reader = PyPDF2.PdfReader(file)
            return '\n'.join(page.extract_text() or '' for page in reader.pages)
        elif ext == 'docx':
            doc = docx.Document(file)
            return '\n'.join(para.text for para in doc.paragraphs)
        elif ext == 'txt':
            return file.read().decode('utf-8')
    except Exception as e:
        print(f"❌ Error reading file: {e}")
    return None

# --- Clean JSON from Gemini ---
def extract_json_block(text):
    # This regex is more robust to leading/trailing text from Gemini
    match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', text)
    if match:
        return match.group(1)
    # Fallback if Gemini doesn't use ```json block
    match = re.search(r'\{[\s\S]*?\}', text)
    return match.group(0) if match else '{}'

# --- Home Page (main.html) ---
@app.route('/')
def home():
    # Renders the main landing page HTML file
    return render_template('index.html')

# --- Upload Resume Page ---
@app.route('/upload_resume_page.html')
def upload_resume_page():
    # Renders the dedicated resume upload page
    return render_template('upload_resume_page.html')


# --- Upload & Process Resume API Endpoint ---
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    global last_job_domains # Declare global to modify it

    if 'resume' not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "Empty file submitted"}), 400

    resume_text = extract_text_from_resume(file)
    if not resume_text or len(resume_text.strip()) < 10:
        return jsonify({"error": "Resume could not be parsed or was empty"}), 400

    # Prompt: Strict skill extraction
    prompt_skills = f"""
    You are a resume skill extractor. Extract technical skills , tools, or programming languages found in the resume below.
    Do not guess,but you can normalize the format (e.g., "Ms office" as "MS Office").


    Return the result strictly in this valid JSON format within a ```json block:
    ```json
    {{
      "skills": ["Python", "AWS", "Java", "HTML"]
    }}
    ```

    Resume:
    {resume_text}
    """

    try:
        # --- Gemini prompt for skills ---
        response_skills = model.generate_content(prompt_skills)
        raw_json_skills = extract_json_block(response_skills.text)

        # Try parsing, if fails: show raw response for debugging
        try:
            skills_data = json.loads(raw_json_skills)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON from Gemini (skills): {raw_json_skills}")
            return jsonify({"error": f"Invalid JSON from Gemini for skills. Details: {str(e)}", "raw_response": response_skills.text}), 500

        skills_list = skills_data.get("skills", [])
        if not skills_list:
            return jsonify({"error": "No skills found in resume."}), 500

        # --- Prompt for job roles ---
        skills_str = ", ".join(skills_list)
        prompt_jobs = f"""
        Given the following skills: {skills_str}
        Suggest 3-5 common and relevant job roles that fit these skills.
        Ensure these are distinct and widely recognized job titles.

        Respond strictly in valid JSON format within a ```json block:
        ```json
        {{
          "job_roles": ["Frontend Developer", "Cloud Engineer", "Software Developer"]
        }}
        ```
        """

        response_jobs = model.generate_content(prompt_jobs)
        raw_json_jobs = extract_json_block(response_jobs.text)

        try:
            job_roles = json.loads(raw_json_jobs).get("job_roles", [])
        except json.JSONDecodeError as e:
            print(f"❌ Invalid job JSON from Gemini: {raw_json_jobs}")
            return jsonify({"error": f"Invalid JSON from Gemini for job roles. Details: {str(e)}", "raw_response": response_jobs.text}), 500

        last_job_domains = job_roles # Store for subsequent /get_job_recommendations call

        return jsonify({
            "skills": skills_list,
            "suggested_job_roles": job_roles
        })

    except Exception as e:
        print(f"❌ Gemini API or processing error: {e}")
        return jsonify({"error": f"An internal server error occurred during AI processing: {str(e)}"}), 500


# --- Get Job Recommendations (Frontend will fetch this) ---
@app.route('/get_job_recommendations', methods=['GET'])
def get_job_recommendations():
    if not last_job_domains:
        # If no resume was processed yet in this session, or data cleared
        return jsonify({"error": "No job recommendations available. Please upload a resume first."}), 404

    # Build job cards as JSON data
    recommended_jobs_data = []
    for role in last_job_domains:
        role_encoded = role.replace(' ', '%20')
        role_dash = role.replace(' ', '-').lower()

        # Corrected URL formatting: removed Markdown link syntax
        linkedin_url = f"[https://www.linkedin.com/jobs/search/?keywords=](https://www.linkedin.com/jobs/search/?keywords=){role_encoded}&location=India"
        naukri_url = f"[https://www.naukri.com/](https://www.naukri.com/){role_dash}-jobs-in-india"
        indeed_url = f"[https://www.indeed.com/jobs?q=](https://www.indeed.com/jobs?q=){role_encoded}&l=India"

        recommended_jobs_data.append({
            "title": role,
            "platforms": [
                {"name": "LinkedIn", "url": linkedin_url},
                {"name": "Naukri", "url": naukri_url},
                {"name": "Indeed", "url": indeed_url}
            ]
        })
    
    return jsonify({"recommended_jobs": recommended_jobs_data})
@app.route('/find_jobs')


def find_jobs():
    if not last_job_domains:
        return Response("<h3 style='font-family:Segoe UI;'>No job roles found. Please upload a resume first.</h3>", mimetype='text/html')

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Recommended Jobs</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
      <style>
        body {
          background-color: #f2f6fc;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          padding: 40px 20px;
        }
        .container {
          max-width: 900px;
          margin: auto;
        }
        .job-card {
          background-color: #ffffff;
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 20px;
          box-shadow: 0 1px 6px rgba(0, 0, 0, 0.1);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .job-card:hover {
          transform: scale(1.02);
          box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }
        .job-title {
          font-size: 1.3rem;
          font-weight: 600;
          color: #0d6efd;
          margin-bottom: 15px;
          text-align: center;
        }
        .platform-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 10px;
          gap: 10px;
          flex-wrap: wrap;
        }
        .platform-name {
          font-weight: bold;
          color: #333;
          flex: 1;
          padding-left: 20px;  /* 👈 Left padding added */
        }
        .view-btn {
          background-color: #0d6efd;
          color: #fff;
          border: none;
          padding: 8px 18px;
          border-radius: 6px;
          font-size: 14px;
          text-decoration: none;
          transition: background-color 0.3s ease;
        }
        .view-btn:hover {
          background-color: #0b5ed7;
        }
        .back-link {
          display: inline-block;
          margin-top: 30px;
          text-decoration: none;
          padding: 10px 20px;
          background-color: #0d6efd;
          color: white;
          border-radius: 6px;
          transition: background-color 0.3s ease;
        }
        .back-link:hover {
          background-color: #0b5ed7;
        }

        @media (min-width: 768px) {
          .view-btn {
            padding: 10px 24px;
            font-size: 15px;
          }
        }

        @media (max-width: 576px) {
          .platform-row {
            flex-direction: column;
            align-items: flex-start;
          }
          .platform-name {
            margin-bottom: 5px;
          }
          .view-btn {
            width: 100%;
            text-align: center;
          }
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h2 class="text-center mb-5">Recommended Jobs</h2>
    """

    for role in last_job_domains:
        role_encoded = role.replace(' ', '%20')
        role_dash = role.replace(' ', '-').lower()

        linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={role_encoded}&location=India"
        naukri_url = f"https://www.naukri.com/{role_dash}-jobs-in-india"
        indeed_url = f"https://www.indeed.com/jobs?q={role_encoded}&l=India"

        html += f"""
        <div class="job-card">
          <div class="job-title">{role}</div>

          <div class="platform-row">
            <span class="platform-name">LinkedIn</span>
            <a href="{linkedin_url}" target="_blank" class="view-btn">View</a>
          </div>

          <div class="platform-row">
            <span class="platform-name">Naukri</span>
            <a href="{naukri_url}" target="_blank" class="view-btn">View</a>
          </div>

          <div class="platform-row">
            <span class="platform-name">Indeed</span>
            <a href="{indeed_url}" target="_blank" class="view-btn">View</a>
          </div>
        </div>
        """

    html += """
        <div class="text-center">
          <a href="/" class="back-link">⬅ Back</a>
        </div>
      </div>
    </body>
    </html>
    """

    return Response(html, mimetype='text/html')

# --- Run App ---
if __name__ == '__main__':
    # Make sure you have a 'templates' folder and 'index.html' inside it
    # And a '.env' file with GEMINI_API_KEY
    app.run(debug=True, host='0.0.0.0', port=5001)

