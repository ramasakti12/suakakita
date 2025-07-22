from src.models.user import db, User

def create_default_users():
    """Create default users if they don't exist"""
    
    default_users = [
        {'username': 'Entin', 'password': 'Unp_01'},
        {'username': 'Mulazimah', 'password': 'Unp_02'},
        {'username': 'Nur Ahmad', 'password': 'Unp_03'},
        {'username': 'Budiman Agung', 'password': 'Unp_04'},
        {'username': 'Imam mudzakir', 'password': 'Unp_05'},
    ]
    
    # Clear existing users first
    User.query.delete()
    
    for user_data in default_users:
        # Create new user with simple password storage
        new_user = User(
            username=user_data['username'],
            password_hash=user_data['password'],  # Simple storage for demo
            is_active=True
        )
        
        db.session.add(new_user)
    
    try:
        db.session.commit()
        print("Default users created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating default users: {e}")