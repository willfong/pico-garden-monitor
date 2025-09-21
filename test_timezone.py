#!/usr/bin/env python3
"""
Test script to verify timezone functionality in the Garden Monitor system.
This script simulates sensor data from different timezones to test the system.
"""

import requests
import json
import time
from datetime import datetime, timezone, timedelta

# Configuration
SERVER_URL = "http://localhost:5000"
API_ENDPOINT = f"{SERVER_URL}/api/sensor-data"

def simulate_sensor_data(timezone_offset):
    """Simulate sensor data from a specific timezone"""
    # Current UTC timestamp
    utc_timestamp = time.time()
    local_timestamp = utc_timestamp + (timezone_offset * 3600)

    return {
        "light": 75.5,
        "soil_moisture": 45.2,
        "temperature": 24.5,
        "humidity": 60.8,
        "timestamp": utc_timestamp,
        "local_timestamp": local_timestamp,
        "timezone_offset": timezone_offset
    }

def test_timezone_data():
    """Test sending data from different timezones"""
    print("🧪 Testing Garden Monitor Timezone & Timer Functionality")
    print("=" * 50)

    # Show current minute boundary info
    current_time = time.time()
    current_seconds = int(current_time) % 60
    delay_to_minute = 60 - current_seconds
    print(f"⏰ Current time: {datetime.fromtimestamp(current_time).strftime('%H:%M:%S')}")
    print(f"   Seconds until next minute: {delay_to_minute}")
    print(f"   (Pico would wait this long to sync with minute boundary)")
    print()

    # Test different timezone offsets
    test_zones = [
        (-8, "PST (Pacific Standard Time)"),
        (-5, "EST (Eastern Standard Time)"),
        (0, "UTC (Coordinated Universal Time)"),
        (1, "CET (Central European Time)"),
        (8, "SGT (Singapore Time)"),
        (9, "JST (Japan Standard Time)")
    ]

    for offset, zone_name in test_zones:
        print(f"\n📍 Testing {zone_name} (UTC{offset:+d})")

        # Generate test data
        data = simulate_sensor_data(offset)

        # Display timestamp information
        utc_time = datetime.fromtimestamp(data['timestamp'], tz=timezone.utc)
        local_time = datetime.fromtimestamp(data['local_timestamp'], tz=timezone.utc)

        print(f"   UTC Time: {utc_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"   Local Time: {local_time.strftime('%Y-%m-%d %H:%M:%S')} (simulated)")

        try:
            # Send data to server
            response = requests.post(
                API_ENDPOINT,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )

            if response.status_code == 200:
                print(f"   ✅ Data sent successfully")
            else:
                print(f"   ❌ Failed to send data: HTTP {response.status_code}")
                print(f"      Response: {response.text}")

        except requests.exceptions.ConnectionError:
            print(f"   ⚠️  Could not connect to server at {SERVER_URL}")
            print(f"      Make sure the Flask server is running")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Wait a bit between requests
        time.sleep(1)

    print(f"\n🌐 Test completed! Check the dashboard at {SERVER_URL}")
    print("   The dashboard should display all times in your browser's local timezone.")

def verify_api_response():
    """Verify that API responses include timezone information"""
    print(f"\n🔍 Verifying API response format...")

    try:
        # Test recent data endpoint
        response = requests.get(f"{SERVER_URL}/api/data/recent", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                sample = data[0]
                print(f"   ✅ Recent data endpoint working")
                print(f"   📊 Sample response fields: {list(sample.keys())}")

                # Check for timezone fields
                timezone_fields = ['utc_timestamp', 'local_timestamp', 'timezone_offset']
                for field in timezone_fields:
                    if field in sample:
                        print(f"   ✅ {field}: {sample[field]}")
                    else:
                        print(f"   ⚠️  Missing {field} field")
            else:
                print(f"   ℹ️  No data available yet")
        else:
            print(f"   ❌ Recent data endpoint failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"   ❌ Error testing API: {e}")

if __name__ == "__main__":
    test_timezone_data()
    verify_api_response()

    print(f"\n💡 Tips:")
    print(f"   • Open {SERVER_URL} in different browsers/devices in various timezones")
    print(f"   • All timestamps should display in 24-hour format without seconds")
    print(f"   • Times display correctly in each user's local timezone")
    print(f"   • The Pico W config should be set to TIMEZONE_OFFSET matching your location")
    print(f"   • Pico W will now sync readings to minute boundaries for cleaner data")