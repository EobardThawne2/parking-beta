import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_FILE = 'parking.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initialize the database and create tables if they don't exist"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create slots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_type TEXT NOT NULL,
                slot_name TEXT NOT NULL UNIQUE,
                price INTEGER NOT NULL,
                is_booked BOOLEAN NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT,
                user_type TEXT DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_id INTEGER NOT NULL,
                user_id INTEGER,
                booking_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                booking_reference TEXT UNIQUE,
                total_amount REAL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (slot_id) REFERENCES slots(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Check if slots table is empty
        cursor.execute('SELECT COUNT(*) FROM slots')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Populate initial slot data
            populate_slots(cursor)
            print("Database initialized and populated with slots.")
        else:
            print("Database already initialized.")
            
        # Create default admin user if no users exist
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # Create default admin user
            import hashlib
            admin_password = hashlib.sha256('admin123'.encode('utf-8')).hexdigest()
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, phone, user_type)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin@parkeasy.com', admin_password, 'System Administrator', '9999999999', 'admin'))
            print("Default admin user created: admin@parkeasy.com / admin123")

def populate_slots(cursor):
    """Populate the database with initial parking slots"""
    slots_to_insert = []
    
    # VIP slots (10 slots)
    for i in range(1, 11):
        slots_to_insert.append(('vip', f'V{i}', 500))
    
    # Executive slots (100 slots - 5 rows x 20 columns)
    for row in range(1, 6):
        for col in range(1, 21):
            slots_to_insert.append(('executive', f'E{row:02d}{col:02d}', 350))
    
    # Normal slots (11 slots)
    for i in range(1, 12):
        slots_to_insert.append(('normal', f'N{i}', 320))
    
    cursor.executemany(
        'INSERT INTO slots (slot_type, slot_name, price) VALUES (?, ?, ?)', 
        slots_to_insert
    )

def get_parking_status():
    """Get the current status of all parking slots"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT slot_type, slot_name, price, is_booked FROM slots ORDER BY slot_type, id')
        rows = cursor.fetchall()
    
    # Format data to match the existing JSON structure
    status = {
        'vip': {'price': 500, 'slots': [], 'booked': []},
        'executive': {'price': 350, 'slots': [], 'booked': []},
        'normal': {'price': 320, 'slots': [], 'booked': []}
    }
    
    for row in rows:
        slot_type = row['slot_type']
        slot_name = row['slot_name']
        status[slot_type]['slots'].append(slot_name)
        if row['is_booked']:
            status[slot_type]['booked'].append(slot_name)
    
    return status

def book_slots(slot_type, slots_to_book, user_id=None, total_amount=0):
    """Book a list of slots of a specific type"""
    if not slots_to_book:
        return {'success': False, 'message': 'No slots provided'}
    
    import secrets
    booking_reference = secrets.token_hex(8).upper()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if any slots are already booked
        placeholders = ','.join('?' * len(slots_to_book))
        query = f'''
            SELECT slot_name FROM slots 
            WHERE slot_name IN ({placeholders}) 
            AND slot_type = ? 
            AND is_booked = 1
        '''
        cursor.execute(query, (*slots_to_book, slot_type))
        already_booked = cursor.fetchall()
        
        if already_booked:
            booked_names = [row['slot_name'] for row in already_booked]
            return {
                'success': False, 
                'message': f'Slots already booked: {", ".join(booked_names)}'
            }
        
        # Get slot IDs and price for the slots to book
        query = f'''
            SELECT id, price FROM slots 
            WHERE slot_name IN ({placeholders}) 
            AND slot_type = ?
        '''
        cursor.execute(query, (*slots_to_book, slot_type))
        slot_data = cursor.fetchall()
        
        if not slot_data:
            return {'success': False, 'message': 'Invalid slots'}
        
        slot_ids = [row['id'] for row in slot_data]
        price = slot_data[0]['price']
        
        # Mark slots as booked
        update_query = f'''
            UPDATE slots 
            SET is_booked = 1 
            WHERE id IN ({','.join('?' * len(slot_ids))})
        '''
        cursor.execute(update_query, slot_ids)
        
        # Add entries to the bookings table
        booking_time = datetime.now()
        bookings_to_insert = [(slot_id, user_id, booking_reference, total_amount, booking_time) for slot_id in slot_ids]
        cursor.executemany(
            'INSERT INTO bookings (slot_id, user_id, booking_reference, total_amount, booking_time) VALUES (?, ?, ?, ?, ?)', 
            bookings_to_insert
        )
        
        return {
            'success': True,
            'message': f'Successfully booked {len(slots_to_book)} slots',
            'booked_count': len(slots_to_book),
            'price': price,
            'booking_reference': booking_reference
        }

def reset_all_bookings():
    """Reset all bookings, marking all slots as available"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Mark all slots as not booked
        cursor.execute('UPDATE slots SET is_booked = 0')
        
        # Clear the bookings table
        cursor.execute('DELETE FROM bookings')
        
        print("All bookings have been reset.")
        return {'success': True, 'message': 'All bookings reset'}

def get_booking_stats():
    """Get statistics about bookings"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                slot_type,
                COUNT(*) as total,
                SUM(CASE WHEN is_booked = 1 THEN 1 ELSE 0 END) as booked,
                SUM(CASE WHEN is_booked = 0 THEN 1 ELSE 0 END) as available
            FROM slots
            GROUP BY slot_type
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            stats[row['slot_type']] = {
                'total': row['total'],
                'booked': row['booked'],
                'available': row['available']
            }
        
        return stats

def get_user_bookings(user_id):
    """Get all bookings for a specific user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                b.id,
                b.booking_reference,
                b.booking_time,
                b.total_amount,
                b.status,
                s.slot_name,
                s.slot_type,
                s.price
            FROM bookings b
            JOIN slots s ON b.slot_id = s.id
            WHERE b.user_id = ?
            ORDER BY b.booking_time DESC
        ''', (user_id,))
        
        bookings = cursor.fetchall()
        
        # Group bookings by reference
        grouped = {}
        for row in bookings:
            ref = row['booking_reference']
            if ref not in grouped:
                grouped[ref] = {
                    'booking_reference': ref,
                    'booking_time': row['booking_time'],
                    'total_amount': row['total_amount'],
                    'status': row['status'],
                    'slots': []
                }
            grouped[ref]['slots'].append({
                'slot_name': row['slot_name'],
                'slot_type': row['slot_type'],
                'price': row['price']
            })
        
        return list(grouped.values())

def get_booking_by_reference(booking_reference):
    """Get booking details by reference number"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                b.id,
                b.booking_reference,
                b.booking_time,
                b.total_amount,
                b.status,
                s.slot_name,
                s.slot_type,
                s.price
            FROM bookings b
            JOIN slots s ON b.slot_id = s.id
            WHERE b.booking_reference = ?
        ''', (booking_reference,))
        
        bookings = cursor.fetchall()
        
        if not bookings:
            return None
        
        first = bookings[0]
        return {
            'booking_reference': first['booking_reference'],
            'booking_time': first['booking_time'],
            'total_amount': first['total_amount'],
            'status': first['status'],
            'slots': [{'slot_name': row['slot_name'], 'slot_type': row['slot_type'], 'price': row['price']} for row in bookings]
        }

# User authentication functions
def get_user_by_email(email):
    """Get user by email address"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'email': row['email'],
                'password_hash': row['password_hash'],
                'full_name': row['full_name'],
                'phone': row['phone'],
                'user_type': row['user_type'],
                'created_at': row['created_at']
            }
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'email': row['email'],
                'full_name': row['full_name'],
                'phone': row['phone'],
                'user_type': row['user_type'],
                'created_at': row['created_at']
            }
        return None

def create_user(email, password_hash, full_name, phone=None, user_type='user'):
    """Create a new user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, phone, user_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, password_hash, full_name, phone, user_type))
            
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("User with this email already exists")

def init_auth_tables():
    """Initialize auth tables (called by auth.py)"""
    # This function is called by auth.py but the tables are already created in init_db()
    pass
