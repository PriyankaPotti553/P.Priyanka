import os

def extract_skills_from_resume(resume_path):
    """
    Dummy function to simulate extracting skills from resume text.
    """
    # In a real system, you'd extract and parse the text from PDF
    # For now, we'll just return a sample list
    return ["Python", "SQL", "React", "Node.js", "Docker", "Kubernetes"]

def get_job_recommendations(resume_path):
    """
    Based on extracted skills from resume, return a list of dummy job recommendations.
    """
    skills = extract_skills_from_resume(resume_path)

    jobs = []

    if "React" in skills or "Node.js" in skills:
        jobs.append({
            "title": "Full-Stack Developer",
            "company": "Amazon",
            "location": "Hyderabad",
            "skills": "React, Node.js"
        })

    if "SQL" in skills or "Python" in skills:
        jobs.append({
            "title": "Data Analyst",
            "company": "Infosys",
            "location": "Bangalore",
            "skills": "SQL, Tableau, Python"
        })

    if "Docker" in skills or "Kubernetes" in skills:
        jobs.append({
            "title": "DevOps Engineer",
            "company": "Microsoft",
            "location": "Hyderabad",
            "skills": "Docker, Kubernetes, Azure"
        })

    # Fallback/default job
    jobs.append({
        "title": "UI/UX Designer",
        "company": "Adobe",
        "location": "Remote",
        "skills": "Figma, Adobe XD"
    })

    return jobs
