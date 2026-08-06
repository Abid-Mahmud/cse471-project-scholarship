import secrets
from app.models.user import User
from app.models.professor import Professor
from app.extensions import bcrypt

RESTRICTED_BRACU_DOMAIN = "@g.bracu.ac.bd"

def register_user(email, password, full_name, role, institution=None, department=None):
    email = email.strip().lower() if email else ""

    # --- DOMAIN VALIDATION RULES ---
    if role == 'professor' and not email.endswith(RESTRICTED_BRACU_DOMAIN):
        return None, f"Professors must register using an official email ending in '{RESTRICTED_BRACU_DOMAIN}'."

    if role == 'student' and email.endswith(RESTRICTED_BRACU_DOMAIN):
        return None, f"Users with '{RESTRICTED_BRACU_DOMAIN}' emails cannot register as Students. Please register as a Professor."

    # --- STRICT CROSS-ROLE CHECK ---
    if role == 'professor' and User.objects(email=email).first():
        return None, "This email is already registered as a Student. You cannot create a Professor account with it."
    if role == 'student' and Professor.objects(email=email).first():
        return None, "This email is already registered as a Professor. You cannot create a Student account with it."
        
    # --- EXISTING USER CHECK ---
    if User.objects(email=email).first() or Professor.objects(email=email).first():
        return None, "Email already registered."
        
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    if role == 'professor':
        user = Professor(
            email=email,
            password=hashed_password,
            full_name=full_name,
            role='professor',
            institution=institution,
            department=department
        )
    else:
        user = User(
            email=email,
            password=hashed_password,
            full_name=full_name,
            role='student',
            # institution=institution,
            # department=department
        )
        
    user.save()
    return user, None


def authenticate_user(email, password, role='student'):
    email = email.strip().lower() if email else ""

    # --- DOMAIN VALIDATION RULES ---
    if role == 'professor' and not email.endswith(RESTRICTED_BRACU_DOMAIN):
        return None, f"Only official '{RESTRICTED_BRACU_DOMAIN}' emails can log in as a Professor."

    if role == 'student' and email.endswith(RESTRICTED_BRACU_DOMAIN):
        return None, f"'{RESTRICTED_BRACU_DOMAIN}' emails are reserved for Professors. Please select 'I am a Professor' to log in."

    # --- STRICT ROLE CHECK ---
    if role == 'professor':
        if User.objects(email=email).first():
            return None, "This email belongs to a Student account. Please select 'I am a Student' to log in."
        user = Professor.objects(email=email).first()
    else:
        if Professor.objects(email=email).first():
            return None, "This email belongs to a Professor account. Please select 'I am a Professor' to log in."
        user = User.objects(email=email).first()
        
    if user and bcrypt.check_password_hash(user.password, password):
        return user, None
    return None, "Invalid email or password."


def find_or_create_google_user(google_user_info, role='student'):
    email = google_user_info.get('email', '').strip().lower()
    google_id = google_user_info.get('sub')
    
    # --- DOMAIN VALIDATION RULES ---
    if role == 'professor' and not email.endswith(RESTRICTED_BRACU_DOMAIN):
        raise ValueError(f"Access denied. Only official BRACU emails ('{RESTRICTED_BRACU_DOMAIN}') can log in or register as a Professor.")

    if role == 'student' and email.endswith(RESTRICTED_BRACU_DOMAIN):
        raise ValueError(f"Access denied. '{RESTRICTED_BRACU_DOMAIN}' emails are restricted from logging in as Students. Please log in as a Professor.")

    # --- STRICT CROSS-ROLE CHECK ---
    if role == 'professor' and User.objects(email=email).first():
        raise ValueError("This Google account is already registered as a Student. You cannot log in as a Professor.")
    if role == 'student' and Professor.objects(email=email).first():
        raise ValueError("This Google account is already registered as a Professor. You cannot log in as a Student.")
    
    ModelClass = Professor if role == 'professor' else User
    
    # Try finding existing user by google_id
    user = ModelClass.objects(google_id=google_id).first()
    if user:
        return user
        
    # Try finding existing user by email
    user = ModelClass.objects(email=email).first()
    if user:
        user.google_id = google_id
        if not getattr(user, 'avatar_url', None):
            user.avatar_url = google_user_info.get('picture')
        user.save()
        return user
        
    # Create new Google User
    random_password = secrets.token_urlsafe(16)
    hashed_password = bcrypt.generate_password_hash(random_password).decode('utf-8')
    
    user = ModelClass(
        email=email,
        password=hashed_password,
        full_name=google_user_info.get('name', 'Google User'),
        role=role,
        google_id=google_id,
        avatar_url=google_user_info.get('picture')
    )
    user.save()
    return user