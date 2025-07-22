from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db
from src.models.melon_pinter import MelonPinterData
from datetime import datetime, timedelta

melon_bp = Blueprint('melon', __name__)

@melon_bp.route('/data', methods=['POST'])
@login_required
def create_melon_data():
    """Create new Melon Pinter data entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'gender', 'age', 'expression', 'heart_rate', 'respiration_rate', 'temperature']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate warnings based on vital signs
        warnings = []
        hr = int(data['heart_rate'])
        rr = int(data['respiration_rate'])
        temp = float(data['temperature'])
        
        if hr < 60 or hr > 100:
            warnings.append(f"Heart rate abnormal: {hr} bpm")
        if rr < 12 or rr > 20:
            warnings.append(f"Respiration rate abnormal: {rr} per minute")
        if temp < 36.1 or temp > 37.2:
            warnings.append(f"Temperature abnormal: {temp}°C")
        
        new_entry = MelonPinterData(
            user_id=current_user.id,
            name=data['name'],
            gender=data['gender'],
            age=int(data['age']),
            expression=data['expression'],
            complaints=data.get('complaints', ''),
            heart_rate=hr,
            respiration_rate=rr,
            temperature=temp,
            warnings='; '.join(warnings) if warnings else None
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Data saved successfully',
            'data': new_entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@melon_bp.route('/data', methods=['GET'])
@login_required
def get_melon_data():
    """Get all Melon Pinter data"""
    try:
        # Get data from last year
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        data = MelonPinterData.query.filter(
            MelonPinterData.timestamp >= one_year_ago
        ).order_by(MelonPinterData.timestamp.desc()).all()
        
        return jsonify({
            'data': [entry.to_dict() for entry in data]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@melon_bp.route('/statistics', methods=['GET'])
@login_required
def get_melon_statistics():
    """Get global statistics for Melon Pinter data"""
    try:
        # Get data from last year
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        all_data = MelonPinterData.query.filter(
            MelonPinterData.timestamp >= one_year_ago
        ).all()
        
        total_students = len(all_data)
        if total_students == 0:
            return jsonify({
                'total_students': 0,
                'healthy': {'count': 0, 'percentage': 0},
                'needs_attention': {'count': 0, 'percentage': 0},
                'critical': {'count': 0, 'percentage': 0},
                'absent': {'count': 0, 'percentage': 0}
            }), 200
        
        # Categorize students based on vital signs and warnings
        healthy = 0
        needs_attention = 0
        critical = 0
        
        for entry in all_data:
            if entry.warnings:
                # Check severity of warnings
                warning_text = entry.warnings.lower()
                if 'abnormal' in warning_text:
                    # Count number of abnormal readings
                    abnormal_count = warning_text.count('abnormal')
                    if abnormal_count >= 2:
                        critical += 1
                    else:
                        needs_attention += 1
                else:
                    needs_attention += 1
            else:
                healthy += 1
        
        # Calculate absent (simulated as 3% of total expected students)
        expected_total = int(total_students * 1.03)  # Assume 3% absent
        absent = expected_total - total_students
        
        return jsonify({
            'total_students': expected_total,
            'healthy': {
                'count': healthy,
                'percentage': round((healthy / expected_total) * 100, 1)
            },
            'needs_attention': {
                'count': needs_attention,
                'percentage': round((needs_attention / expected_total) * 100, 1)
            },
            'critical': {
                'count': critical,
                'percentage': round((critical / expected_total) * 100, 1)
            },
            'absent': {
                'count': absent,
                'percentage': round((absent / expected_total) * 100, 1)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

