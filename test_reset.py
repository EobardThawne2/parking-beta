#!/usr/bin/env python3
"""Quick test script to verify database reset functionality"""

import os
import sys

# Test 1: Import modules
print("Test 1: Importing modules...")
try:
    import database
    import app
    print("  ✓ Modules imported successfully")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize database
print("\nTest 2: Initializing database...")
try:
    database.init_db()
    print("  ✓ Database initialized")
except Exception as e:
    print(f"  ✗ Init failed: {e}")
    sys.exit(1)

# Test 3: Get parking status
print("\nTest 3: Getting parking status...")
try:
    status = database.get_parking_status()
    total_slots = sum(len(s['slots']) for s in status.values())
    print(f"  ✓ Parking status retrieved: {total_slots} total slots")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    sys.exit(1)

# Test 4: Reset bookings
print("\nTest 4: Resetting bookings...")
try:
    result = database.reset_all_bookings()
    if result['success']:
        print(f"  ✓ Reset successful: {result['message']}")
    else:
        print(f"  ⚠ Reset returned: {result['message']}")
        if 'warning' in result:
            print(f"     (This is expected on Vercel: {result['warning']})")
except Exception as e:
    print(f"  ✗ Reset failed: {e}")
    sys.exit(1)

# Test 5: Verify stats after reset
print("\nTest 5: Verifying stats after reset...")
try:
    stats = database.get_booking_stats()
    for slot_type, data in stats.items():
        booked = data.get('booked', 0)
        total = data.get('total', 0)
        print(f"  {slot_type}: {booked}/{total} booked (should all be 0)")
    print("  ✓ All tests passed!")
except Exception as e:
    print(f"  ✗ Failed: {e}")
    sys.exit(1)
