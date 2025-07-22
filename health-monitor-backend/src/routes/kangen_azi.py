from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from src.models.user import db
from src.models.kangen_azi import KangenAziData
from datetime import datetime, timedelta

kangen_bp = Blueprint('kangen', __name__)

def calculate_bmi_info(weight, height):
    """Calculate BMI and return category, status, and diet recommendations"""
    # Convert height from cm to meters
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    
    # Determine BMI category
    if bmi < 18.5:
        category = "Underweight"
        status = "Perlu Peningkatan Berat Badan"
        diet_rec = "Tingkatkan asupan kalori dengan makanan bergizi tinggi: nasi, daging, ikan, telur, susu, kacang-kacangan, dan buah-buahan."
    elif 18.5 <= bmi < 25:
        category = "Normal"
        status = "Performa Optimal"
        diet_rec = "Pertahankan pola makan seimbang: karbohidrat kompleks, protein tanpa lemak, sayuran, dan buah-buahan."
    elif 25 <= bmi < 30:
        category = "Overweight"
        status = "Perlu Penurunan Berat Badan"
        diet_rec = "Kurangi kalori dengan memperbanyak sayuran, protein tanpa lemak, dan mengurangi makanan tinggi lemak dan gula."
    else:
        category = "Obese"
        status = "Risiko Cedera Tinggi"
        diet_rec = "Konsultasi dengan ahli gizi. Diet rendah kalori dengan fokus pada sayuran, protein tanpa lemak, dan olahraga teratur."
    
    return round(bmi, 2), category, status, diet_rec

@kangen_bp.route('/data', methods=['POST'])
@login_required
def create_kangen_data():
    """Create new Kangen Azi data entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['weight', 'height', 'age', 'sport']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        weight = float(data['weight'])
        height = float(data['height'])
        age = int(data['age'])
        sport = data['sport']
        
        # Calculate BMI and related information
        bmi, category, status, diet_recommendations = calculate_bmi_info(weight, height)
        
        new_entry = KangenAziData(
            user_id=current_user.id,
            weight=weight,
            height=height,
            age=age,
            sport=sport,
            bmi=bmi,
            bmi_category=category,
            bmi_status=status,
            diet_recommendations=diet_recommendations
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

@kangen_bp.route('/data', methods=['GET'])
@login_required
def get_kangen_data():
    """Get all Kangen Azi data"""
    try:
        # Get data from last year
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        data = KangenAziData.query.filter(
            KangenAziData.timestamp >= one_year_ago
        ).order_by(KangenAziData.timestamp.desc()).all()
        
        return jsonify({
            'data': [entry.to_dict() for entry in data]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kangen_bp.route('/statistics', methods=['GET'])
@login_required
def get_kangen_statistics():
    """Get global statistics for Kangen Azi data"""
    try:
        # Get data from last year
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        all_data = KangenAziData.query.filter(
            KangenAziData.timestamp >= one_year_ago
        ).all()
        
        total_athletes = len(all_data)
        if total_athletes == 0:
            return jsonify({
                'total_athletes': 0,
                'optimal': {'count': 0, 'percentage': 0},
                'needs_improvement': {'count': 0, 'percentage': 0},
                'injury_risk': {'count': 0, 'percentage': 0},
                'inactive': {'count': 0, 'percentage': 0}
            }), 200
        
        # Categorize athletes based on BMI status
        optimal = 0
        needs_improvement = 0
        injury_risk = 0
        
        for entry in all_data:
            if entry.bmi_status == "Performa Optimal":
                optimal += 1
            elif entry.bmi_status in ["Perlu Peningkatan Berat Badan", "Perlu Penurunan Berat Badan"]:
                needs_improvement += 1
            elif entry.bmi_status == "Risiko Cedera Tinggi":
                injury_risk += 1
        
        # Calculate inactive (simulated as 3% of total expected athletes)
        expected_total = int(total_athletes * 1.03)  # Assume 3% inactive
        inactive = expected_total - total_athletes
        
        return jsonify({
            'total_athletes': expected_total,
            'optimal': {
                'count': optimal,
                'percentage': round((optimal / expected_total) * 100, 1)
            },
            'needs_improvement': {
                'count': needs_improvement,
                'percentage': round((needs_improvement / expected_total) * 100, 1)
            },
            'injury_risk': {
                'count': injury_risk,
                'percentage': round((injury_risk / expected_total) * 100, 1)
            },
            'inactive': {
                'count': inactive,
                'percentage': round((inactive / expected_total) * 100, 1)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kangen_bp.route('/calculate-bmi', methods=['POST'])
@login_required
def calculate_bmi():
    """Calculate BMI without saving to database"""
    try:
        data = request.get_json()
        weight = float(data['weight'])
        height = float(data['height'])
        
        bmi, category, status, diet_recommendations = calculate_bmi_info(weight, height)
        
        return jsonify({
            'bmi': bmi,
            'category': category,
            'status': status,
            'diet_recommendations': diet_recommendations
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

