import os
import json
import uuid
import datetime
import threading
import smtplib
from email.message import EmailMessage
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.scholarship import Scholarship
from app.models.timeline import ApplicationTimeline, TimelineTask
from . import student_bp, groq_client

def send_timeline_email_async(user_email, user_name, scholarship_title, university, timeline_tasks):
    try:
        if not groq_client:
            return

        tasks_str = "\n".join([f"- {t['title']} (Deadline: {t['deadline']})" for t in timeline_tasks])
        
        prompt = f"""
        Write a highly professional and encouraging email to a student named {user_name}.
        They just generated a customized application timeline for the "{scholarship_title}" at {university}.
        
        Here are their specific deadlines:
        {tasks_str}
        
        Format the email entirely in clean, modern HTML with inline CSS.
        Include:
        - A professional, warm greeting.
        - A well-structured list or table of their deadlines.
        - 2-3 brief, highly actionable study/preparation tips for this specific type of application.
        - A professional sign-off from "The ScholarMatch AI Team".
        
        DO NOT wrap the output in ```html blocks. Output ONLY raw HTML code.
        """
        
        completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        html_content = completion.choices[0].message.content.strip()
        
        if html_content.startswith("```html"):
            html_content = html_content[7:]
        if html_content.endswith("```"):
            html_content = html_content[:-3]

        sender_email = os.environ.get('MAIL_USERNAME')
        sender_password = os.environ.get('MAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            print("Email failed: MAIL_USERNAME or MAIL_PASSWORD missing in .env")
            return

        msg = EmailMessage()
        msg['Subject'] = f"Your Application Timeline: {scholarship_title}"
        msg['From'] = f"Scholarship Matcher <{sender_email}>"
        msg['To'] = user_email
        msg.set_content("Please enable HTML to view this email.")
        msg.add_alternative(html_content, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
            print(f"Timeline email successfully sent to {user_email}")
            
    except Exception as e:
        print(f"Background email failed: {e}")

@student_bp.route('/track_scholarship/<scholarship_id>', methods=['GET', 'POST'])
@login_required
def track_scholarship(scholarship_id):
    try:
        user = User.objects(id=current_user.id).first()
        scholarship = Scholarship.objects(id=scholarship_id).first()
        
        if not scholarship:
            return jsonify({"status": "error", "message": "Scholarship not found."}), 404
            
        if scholarship and scholarship not in user.tracked_scholarships:
            user.tracked_scholarships.append(scholarship)
            user.save()
            return jsonify({"status": "success", "message": "Added to Application Tracker!"}), 200
        return jsonify({"status": "info", "message": "Already in your tracker."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@student_bp.route('/untrack_scholarship/<scholarship_id>', methods=['POST'])
@login_required
def untrack_scholarship(scholarship_id):
    try:
        user = User.objects(id=current_user.id).first()
        scholarship = Scholarship.objects(id=scholarship_id).first()
        
        if scholarship in user.tracked_scholarships:
            user.tracked_scholarships.remove(scholarship)
            user.save()
            ApplicationTimeline.objects(user_id=str(current_user.id), scholarship_id=scholarship_id).delete()
            return jsonify({"status": "success", "message": "Removed from Tracker"}), 200
        return jsonify({"status": "error", "message": "Not found in your tracker."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@student_bp.route('/app_tracker', methods=['GET'])
@login_required
def app_tracker():
    user = User.objects(id=current_user.id).first()
    return render_template('dashboard/app_tracker.html', saved_scholarships=user.tracked_scholarships)

@student_bp.route('/api/timeline/<scholarship_id>', methods=['GET'])
@login_required
def get_timeline(scholarship_id):
    timeline = ApplicationTimeline.objects(user_id=str(current_user.id), scholarship_id=scholarship_id).first()
    if timeline:
        return jsonify({"tasks": [{"task_id": t.task_id, "column": t.column, "title": t.title, "deadline": t.deadline} for t in timeline.tasks]})
    return jsonify({"tasks": []})

@student_bp.route('/api/generate_timeline/<scholarship_id>', methods=['POST'])
@login_required
def generate_timeline(scholarship_id):
    scholarship = Scholarship.objects(id=scholarship_id).first()
    if not scholarship:
        return jsonify({"error": "Scholarship not found"}), 404

    today = datetime.datetime.utcnow().strftime('%B %d, %Y')
    real_deadline = scholarship.deadline.strftime('%B %d, %Y') if getattr(scholarship, 'deadline', None) else "December 31, 2026"

    fallback_timeline = {
        "tasks": [
            {"column": "todo", "title": f"Draft Statement of Purpose for {scholarship.university}", "deadline": "1 Month Before"},
            {"column": "todo", "title": "Obtain Official Academic Transcripts", "deadline": "3 Weeks Before"},
            {"column": "in_progress", "title": "Contact Professors for Reference Letters", "deadline": "2 Weeks Before"},
            {"column": "done", "title": "Create Portal Account & Register", "deadline": today}
        ]
    }

    generated_data = fallback_timeline
    if groq_client:
            prompt = f"""
            Act as an expert scholarship application planner.
            The user wants to apply to "{scholarship.title}" at "{scholarship.university}".
            The target deadline is: {real_deadline}. Today's date is: {today}.
            
            Generate a Kanban timeline working backwards from the deadline.
            Return ONLY a raw valid JSON object in this exact structure:
            {{
                "tasks": [
                    {{"column": "todo", "title": "Draft Statement of Purpose", "deadline": "Oct 1"}},
                    {{"column": "todo", "title": "Contact Recommenders", "deadline": "Sep 15"}},
                    {{"column": "done", "title": "Create Application Account", "deadline": "Aug 1"}}
                ]
            }}
            
            CRITICAL RULES:
            1. Columns must be exactly: 'todo', 'in_progress', or 'done'.
            2. Provide 5-7 tasks.
            3. NEVER put a task in the 'done' or 'in_progress' column if its deadline is in the future (after {today}).
            4. By default, assign all future tasks to the 'todo' column so the student can track their own progress manually.
            """
            try:
                completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                generated_data = json.loads(completion.choices[0].message.content.strip())
            except Exception as e:
                print(f"Timeline generation error: {e}")

    tasks = []
    for item in generated_data.get('tasks', []):
        tasks.append(TimelineTask(
            task_id=str(uuid.uuid4()),
            column=item.get('column', 'todo'),
            title=item.get('title', 'Task'),
            deadline=item.get('deadline', '')
        ))

    existing = ApplicationTimeline.objects(user_id=str(current_user.id), scholarship_id=scholarship_id).first()
    if existing:
        existing.tasks = tasks
        existing.save()
    else:
        ApplicationTimeline(user_id=str(current_user.id), scholarship_id=scholarship_id, tasks=tasks).save()

    threading.Thread(
        target=send_timeline_email_async, 
        args=(current_user.email, current_user.full_name, scholarship.title, scholarship.university, generated_data.get('tasks', []))
    ).start()

    return jsonify({"tasks": [{"task_id": t.task_id, "column": t.column, "title": t.title, "deadline": t.deadline} for t in tasks]})

@student_bp.route('/api/update_timeline_task/<scholarship_id>', methods=['POST'])
@login_required
def update_timeline_task(scholarship_id):
    data = request.json
    task_id = data.get('task_id')
    new_column = data.get('column')
    
    timeline = ApplicationTimeline.objects(user_id=str(current_user.id), scholarship_id=scholarship_id).first()
    if timeline:
        for t in timeline.tasks:
            if t.task_id == task_id:
                t.column = new_column
                break
        timeline.save()
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 404