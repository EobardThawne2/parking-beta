# database_postgres.py
# PostgreSQL adapter for Vercel deployment
# Uncomment and complete this file to migrate from SQLite to PostgreSQL

"""
PostgreSQL Database Adapter for ParkEasy on Vercel

To use this:
1. Provision a PostgreSQL database (Vercel Postgres, Supabase, Railway, etc.)
2. Set the DATABASE_URL environment variable
3. Replace 'import database' with 'import database_postgres as database' in app.py
4. Run the app to initialize tables
"""

import os
import hashlib
import secrets
from datetime import datetime
from contextlib import contextmanager

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("WARNING: psycopg2 not installed. Install with: pip install psycopg2-binary")

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable not set. "
        "Set it in Vercel Dashboard → Settings → Environment Variables"
    )

@contextmanager
def get_db_connection():
    """Context manager for PostgreSQL connections"""
    if not POSTGRES_AVAILABLE:
        raise ImportError("psycopg2 is not available")
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize database tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create slots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS slots (
                id SERIAL PRIMARY KEY,
                slot_type VARCHAR(50) NOT NULL,
                slot_name VARCHAR(50) NOT NULL UNIQUE,
                price INTEGER NOT NULL,
                is_booked BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                user_type VARCHAR(50) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                slot_id INTEGER NOT NULL REFERENCES slots(id),
                user_id INTEGER REFERENCES users(id),
                booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                booking_reference VARCHAR(255) UNIQUE,
                total_amount DECIMAL(10, 2),
                status VARCHAR(50) DEFAULT 'active'
            )
        ''')
        
        cursor.execute('SELECT COUNT(*) FROM slots')
        count = cursor.fetchone()[0]
        if count == 0:
            populate_slots(cursor)
            print("Database initialized with initial slots")
        
        # Create default admin user
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        if user_count == 0:
            admin_password = hashlib.sha256('admin123'.encode('utf-8')).hexdigest()
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, phone, user_type)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('admin@parkeasy.com', admin_password, 'System Administrator', '9999999999', 'admin'))
            print("Default admin user created: admin@parkeasy.com / admin123")
        
        conn.commit()

def populate_slots(cursor):
    """Populate initial slots"""
    slots_to_insert = []
    
    # VIP slots (10)
    for i in range(1, 11):
        slots_to_insert.append(('vip', f'V{i}', 500))
    
    # Executive slots (100)
    for row in range(1, 6):
        for col in range(1, 21):
            slots_to_insert.append(('executive', f'E{row:02d}{col:02d}', 350))
    
    # Normal slots (11)
    for i in range(1, 12):
        slots_to_insert.append(('normal', f'N{i}', 320))
    
    cursor.executemany(
        'INSERT INTO slots (slot_type, slot_name, price) VALUES (%s, %s, %s)',
        slots_to_insert
    )

def get_parking_status():
    """Get parking status for all slots"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT slot_type, slot_name, price, is_booked FROM slots ORDER BY slot_type, slot_name')
        rows = cursor.fetchall()
    
    status = {
        'vip': {'price': 500, 'slots': [], 'booked': []},
        'executive': {'price': 350, 'slots': [], 'booked': []},
        'normal': {'price': 320, 'slots': [], 'booked': []}
    }
    
    for row in rows:
        slot_type, slot_name, price, is_booked = row
        status[slot_type]['slots'].append(slot_name)
        if is_booked:
            status[slot_type]['booked'].append(slot_name)
    
    return status

def book_slots(slot_type, slots_to_book, user_id=None, total_amount=0):
    """Book parking slots"""
    if not slots_to_book:
        return {'success': False, 'message': 'No slots provided'}
    
    booking_reference = secrets.token_hex(8).upper()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if any slots already booked
        placeholders = ','.join(['%s'] * len(slots_to_book))
        query = f'SELECT slot_name FROM slots WHERE slot_name IN ({placeholders}) AND slot_type = %s AND is_booked = TRUE'
        cursor.execute(query, (*slots_to_book, slot_type))
        already_booked = cursor.fetchall()
        
        if already_booked:
            booked_names = [row[0] for row in already_booked]
            return {'success': False, 'message': f'Slots already booked: {", ".join(booked_names)}'}
        
        # Get slot IDs
        query = f'SELECT id, price FROM slots WHERE slot_name IN ({placeholders}) AND slot_type = %s'
        cursor.execute(query, (*slots_to_book, slot_type))
        slot_data = cursor.fetchall()
        
        if not slot_data:
            return {'success': False, 'message': 'Invalid slots'}
        
        slot_ids = [row[0] for row in slot_data]
        price = slot_data[0][1]
        
        # Mark slots as booked
        placeholders = ','.join(['%s'] * len(slot_ids))
        cursor.execute(f'UPDATE slots SET is_booked = TRUE WHERE id IN ({placeholders})', slot_ids)
        
        # Add bookings
        booking_time = datetime.now()
        for slot_id in slot_ids:
            cursor.execute('''
                INSERT INTO bookings (slot_id, user_id, booking_reference, total_amount, booking_time)
                VALUES (%s, %s, %s, %s, %s)
            ''', (slot_id, user_id, booking_reference, total_amount, booking_time))
        
        conn.commit()
        return {
            'success': True,
            'message': f'Successfully booked {len(slots_to_book)} slots',
            'booked_count': len(slots_to_book),
            'price': price,
            'booking_reference': booking_reference
        }

def reset_all_bookings():
    """Reset all bookings"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE slots SET is_booked = FALSE')
            cursor.execute('DELETE FROM bookings')
            conn.commit()
            return {'success': True, 'message': 'All bookings reset'}
    except Exception as e:
        return {'success': False, 'message': f'Failed to reset bookings: {str(e)}', 'error': str(e)}

def get_booking_stats():
    """Get booking statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                slot_type,
                COUNT(*) as total,
                SUM(CASE WHEN is_booked THEN 1 ELSE 0 END) as booked,
                SUM(CASE WHEN NOT is_booked THEN 1 ELSE 0 END) as available
            FROM slots
            GROUP BY slot_type
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {'total': row[1], 'booked': row[2] or 0, 'available': row[3] or 0}
        return stats

def get_user_bookings(user_id):
    """Get user bookings"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                b.id, b.booking_reference, b.booking_time, b.total_amount, b.status,
                s.slot_name, s.slot_type, s.price
            FROM bookings b
            JOIN slots s ON b.slot_id = s.id
            WHERE b.user_id = %s
            ORDER BY b.booking_time DESC
        ''', (user_id,))
        
        bookings = cursor.fetchall()
        grouped = {}
        for row in bookings:
            ref = row[1]
            if ref not in grouped:
                grouped[ref] = {
                    'booking_reference': ref,
                    'booking_time': row[2],
                    'total_amount': row[3],
                    'status': row[4],
                    'slots': []
                }
            grouped[ref]['slots'].append({
                'slot_name': row[5],
                'slot_type': row[6],
                'price': row[7]
            })
        return list(grouped.values())

def get_booking_by_reference(booking_reference):
    """Get booking by reference"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                b.booking_reference, b.booking_time, b.total_amount, b.status,
                s.slot_name, s.slot_type, s.price
            FROM bookings b
            JOIN slots s ON b.slot_id = s.id
            WHERE b.booking_reference = %s
        ''', (booking_reference,))
        
        bookings = cursor.fetchall()
        if not bookings:
            return None
        
        first = bookings[0]
        return {
            'booking_reference': first[0],
            'booking_time': first[1],
            'total_amount': first[2],
            'status': first[3],
            'slots': [{'slot_name': row[4], 'slot_type': row[5], 'price': row[6]} for row in bookings]
        }

# User authentication functions
def get_user_by_email(email):
    """Get user by email"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0], 'email': row[1], 'password_hash': row[2],
                'full_name': row[3], 'phone': row[4], 'user_type': row[5], 'created_at': row[6]
            }
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0], 'email': row[1], 'full_name': row[3],
                'phone': row[4], 'user_type': row[5], 'created_at': row[6]
            }
    return None

def create_user(email, password_hash, full_name, phone=None, user_type='user'):
    """Create user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, phone, user_type)
                VALUES (%s, %s, %s, %s, %s)
            ''', (email, password_hash, full_name, phone, user_type))
            conn.commit()
            cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
            return cursor.fetchone()[0]
        except psycopg2.IntegrityError:
            raise ValueError("User with this email already exists")

def init_auth_tables():
    """Auth tables already created by init_db()"""
    pass
