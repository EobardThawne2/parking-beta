from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
from functools import wraps
import database
import auth

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Initialize database on startup
database.init_db()
auth.init_auth_tables()

# Decorators for authentication
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If not logged in, return JSON for API calls, otherwise redirect to admin login page
        if 'user_id' not in session:
            # Detect API requests (simple heuristic) and AJAX requests
            wants_json = request.path.startswith('/api/') or request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')
            if wants_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('admin_login'))
        user = auth.get_user_by_id(session['user_id'])
        if not user or user['user_type'] not in ['admin', 'staff']:
            return jsonify({'error': 'Unauthorized access'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Fee calculation functions

def calculate_platform_fee(base_amount):
    """Calculate static platform fee of ₹18"""
    return 18

def is_midnight_to_5am():
    """Check if current time is between midnight (00:00) and 5:00 AM"""
    current_hour = datetime.now().hour
    return 0 <= current_hour < 5

def calculate_night_surcharge(base_amount):
    """Calculate static night surcharge of ₹12 for midnight to 5 AM bookings"""
    if is_midnight_to_5am():
        return 12
    return 0

def calculate_total_fees(base_amount):
    """Calculate all fees and return breakdown"""
    platform_fee = calculate_platform_fee(base_amount)
    night_surcharge = calculate_night_surcharge(base_amount)
    
    fees = {
        'base_amount': base_amount,
        'platform_fee': platform_fee,
        'night_surcharge': night_surcharge,
        'total_fees': platform_fee + night_surcharge,
        'grand_total': base_amount + platform_fee + night_surcharge,
        'is_night_time': is_midnight_to_5am()
    }
    
    return fees

# Main routes
@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = auth.get_user_by_id(session['user_id'])
    return render_template('index.html', user=user)

@app.route('/login')
def login():
    next_url = request.args.get('next', url_for('dashboard'))
    return render_template('login.html', next_url=next_url)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = auth.get_user_by_id(session['user_id'])
    bookings = database.get_user_bookings(session['user_id'])
    return render_template('dashboard.html', user=user, bookings=bookings)

@app.route('/admin-login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/parking')
def parking():
    parking_data = database.get_parking_status()
    user = None
    if 'user_id' in session:
        user = auth.get_user_by_id(session['user_id'])
    return render_template('parking.html', parking_data=parking_data, user=user)

@app.route('/select-seats')
def select_seats():
    parking_data = database.get_parking_status()
    user = None
    if 'user_id' in session:
        user = auth.get_user_by_id(session['user_id'])
    return render_template('select_seats.html', parking_data=parking_data, user=user)

@app.route('/admin')
@admin_required
def admin():
    """Admin panel for database management"""
    user = auth.get_user_by_id(session['user_id'])
    return render_template('admin.html', user=user)

@app.route('/test-fees')
def test_fees():
    """Test page for fee calculation"""
    return render_template('test_fees.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Authentication API routes
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'})
    
    result = auth.authenticate_user(email, password)
    
    if result['success']:
        session['user_id'] = result['user']['id']
        session['user_email'] = result['user']['email']
        session['user_name'] = result['user']['full_name']
        session['user_type'] = result['user']['user_type']
    
    return jsonify(result)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    phone = data.get('phone')
    
    if not email or not password or not full_name:
        return jsonify({'success': False, 'message': 'All required fields must be filled'})
    
    result = auth.create_user(email, password, full_name, phone)
    
    if result['success']:
        # Auto-login after registration
        session['user_id'] = result['user_id']
        user = auth.get_user_by_id(result['user_id'])
        session['user_email'] = user['email']
        session['user_name'] = user['full_name']
        session['user_type'] = user['user_type']
    
    return jsonify(result)

@app.route('/api/admin-login', methods=['POST'])
def api_admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'})
    
    result = auth.authenticate_user(email, password)
    
    if result['success']:
        user = result['user']
        if user['user_type'] in ['admin', 'staff']:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_name'] = user['full_name']
            session['user_type'] = user['user_type']
            return jsonify({'success': True, 'user': user})
        else:
            return jsonify({'success': False, 'message': 'Access denied. Admin or staff access required.'})
    
    return jsonify(result)

# Parking API routes
@app.route('/api/parking-status')
def parking_status():
    parking_data = database.get_parking_status()
    return jsonify(parking_data)

@app.route('/api/book-slots', methods=['POST'])
def book_slots_route():
    # Require login for booking
    if 'user_id' not in session:
        return jsonify({
            'success': False, 
            'message': 'Please login to book parking slots',
            'require_login': True
        }), 401
    
    data = request.get_json()
    slot_type = data.get('type')
    slots = data.get('slots', [])
    
    if not slot_type or not slots:
        return jsonify({'success': False, 'message': 'Invalid booking data'})
    
    # Calculate total amount
    base_price = len(slots) * (500 if slot_type == 'vip' else 350 if slot_type == 'executive' else 320)
    fee_breakdown = calculate_total_fees(base_price)
    total_amount = fee_breakdown['grand_total']
    
    # Book the slots using database with user ID
    result = database.book_slots(slot_type, slots, session['user_id'], total_amount)
    
    if not result['success']:
        return jsonify(result)
    
    # Add user info to response
    user = auth.get_user_by_id(session['user_id'])
    
    return jsonify({
        'success': True, 
        'message': result['message'],
        'booked_slots': slots,
        'pricing': fee_breakdown,
        'booking_reference': result['booking_reference'],
        'user': {
            'name': user['full_name'],
            'email': user['email']
        }
    })

@app.route('/api/calculate-fees', methods=['POST'])
def calculate_fees():
    """API endpoint to calculate fees for frontend display"""
    data = request.get_json()
    base_amount = data.get('base_amount', 0)
    
    fee_breakdown = calculate_total_fees(base_amount)
    
    return jsonify(fee_breakdown)

@app.route('/api/my-bookings')
@login_required
def my_bookings():
    """Get bookings for logged-in user"""
    bookings = database.get_user_bookings(session['user_id'])
    return jsonify(bookings)

@app.route('/api/booking/<booking_reference>')
def get_booking(booking_reference):
    """Get specific booking by reference"""
    booking = database.get_booking_by_reference(booking_reference)
    if booking:
        return jsonify(booking)
    return jsonify({'error': 'Booking not found'}), 404

@app.route('/api/time-info')
def time_info():
    """API endpoint to get current time info for testing"""
    current_time = datetime.now()
    return jsonify({
        'current_hour': current_time.hour,
        'current_time': current_time.strftime('%H:%M'),
        'is_night_time': is_midnight_to_5am(),
        'night_surcharge_applies': is_midnight_to_5am()
    })

@app.route('/api/reset-bookings', methods=['POST'])
@admin_required
def reset_bookings():
    """API endpoint to reset all bookings (admin only)"""
    try:
        result = database.reset_all_bookings()
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
    except Exception as e:
        error_msg = str(e)
        print(f"Error in reset_bookings endpoint: {error_msg}")
        return jsonify({
            'success': False,
            'message': f'Server error: {error_msg}',
            'error': error_msg
        }), 500

@app.route('/api/booking-stats')
def booking_stats():
    """API endpoint to get booking statistics"""
    stats = database.get_booking_stats()
    return jsonify(stats)

@app.route('/api/check-auth')
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        user = auth.get_user_by_id(session['user_id'])
        return jsonify({'authenticated': True, 'user': user})
    return jsonify({'authenticated': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
