import json
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.saved_checklist import SavedChecklist, ChecklistItem
from . import student_bp, groq_client

@student_bp.route('/document_review', methods=['GET'])
@login_required
def document_review():
    if current_user.role != 'student':
        return redirect(url_for('dashboard'))
    
    checklists = SavedChecklist.objects(user_id=current_user.id).order_by('-created_at')
    return render_template('dashboard/document_review.html', checklists=checklists)

@student_bp.route('/generate_checklist', methods=['POST'])
@login_required
def generate_checklist():
    if current_user.role != 'student':
        return redirect(url_for('dashboard'))
    
    university = request.form.get('university', '').strip()
    country = request.form.get('country', '').strip()
    degree_level = request.form.get('degree_level', '').strip()
    major = request.form.get('major', '').strip()

    if not university or not country or not degree_level or not major:
        flash('Please fill in all fields (University, Country, Degree, and Major).', 'error')
        return redirect(url_for('student.document_review'))

    fallback_data = {
        "isValid": True,
        "checklist": [
            {"name": "Official Academic Transcripts", "description": "Degree certificates & mark sheets"},
            {"name": "Statement of Purpose (SOP)", "description": "Personal essay detailing research goals"},
            {"name": "Letters of Recommendation", "description": "2-3 academic or professional references"},
            {"name": "Proof of Language Proficiency", "description": "IELTS / TOEFL / Duolingo scores"},
            {"name": "Updated Curriculum Vitae (CV)", "description": "Highlighting academic achievements & skills"}
        ]
    }

    data = None
    if groq_client:
        prompt = f"""
        Act as a university admissions officer. Verify if "{university}" exists in "{country}".
        Then output JSON in this exact format:
        {{
          "isValid": true,
          "errorMessage": "",
          "checklist": [
            {{"name": "Official Transcripts", "description": "Degree certificates and mark sheets"}},
            {{"name": "Statement of Purpose", "description": "Personal essay detailing research goals"}}
          ]
        }}
        Degree Level: {degree_level} | Major: {major}
        """
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            data = json.loads(res.choices[0].message.content.strip())
        except Exception as err:
            print(f"Checklist generation error: {err}")
            data = fallback_data
    else:
        data = fallback_data

    if not data.get("isValid", True):
        flash(data.get("errorMessage", "Invalid university or country combination."), "error")
        return redirect(url_for('student.document_review'))

    items = [
        ChecklistItem(
            name=d.get('name', 'Required Document'),
            description=d.get('description', ''),
            is_completed=False
        ) for d in data.get("checklist", [])
    ]

    new_checklist = SavedChecklist(
        user_id=current_user.id,
        university=university,
        country=country,
        degree_level=degree_level,
        major=major,
        items=items
    )
    new_checklist.save()
    flash(f'Successfully generated AI Document Checklist for {university}, {country}!', 'success')
    return redirect(url_for('student.document_review'))

@student_bp.route('/toggle_checklist_item/<checklist_id>/<int:item_idx>', methods=['POST'])
@login_required
def toggle_checklist_item(checklist_id, item_idx):
    try:
        checklist = SavedChecklist.objects(id=checklist_id, user_id=current_user.id).first()
        if checklist and 0 <= item_idx < len(checklist.items):
            checklist.items[item_idx].is_completed = not checklist.items[item_idx].is_completed
            checklist.save()
            flash('Document status updated!', 'success')
    except Exception as e:
        flash(f'Error updating item: {str(e)}', 'error')
    return redirect(url_for('student.document_review'))

@student_bp.route('/delete_checklist/<checklist_id>', methods=['POST'])
@login_required
def delete_checklist(checklist_id):
    try:
        checklist = SavedChecklist.objects(id=checklist_id, user_id=current_user.id).first()
        if checklist:
            checklist.delete()
            flash('Checklist removed successfully.', 'info')
    except Exception as e:
        flash(f'Error deleting checklist: {str(e)}', 'error')
    return redirect(url_for('student.document_review'))