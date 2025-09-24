from flask import Flask, request, jsonify, render_template
import sqlite3
import json
from datetime import datetime, timedelta, timezone
import os

app = Flask(__name__)

# Database configuration
DATABASE = os.environ.get('DATABASE', 'garden_data.db')

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            utc_timestamp DATETIME,
            local_timestamp DATETIME,
            timezone_offset INTEGER,
            light REAL,
            soil_moisture REAL,
            temperature REAL,
            humidity REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    """Endpoint to receive sensor data from Pico W"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data received'}), 400

        # Validate required fields
        required_fields = ['light', 'soil_moisture', 'temperature', 'humidity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Store server-side UTC timestamp when data is received
        server_utc_timestamp = datetime.now(timezone.utc)

        # Insert data into database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO sensor_readings (utc_timestamp, light, soil_moisture, temperature, humidity)
            VALUES (?, ?, ?, ?, ?)
        ''', (server_utc_timestamp, data['light'], data['soil_moisture'], data['temperature'], data['humidity']))

        conn.commit()
        conn.close()

        print(f"Received sensor data: {data}")
        return jsonify({'status': 'success', 'message': 'Data saved successfully'}), 200

    except Exception as e:
        print(f"Error processing sensor data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/data/recent', methods=['GET'])
def get_recent_data():
    """Get recent sensor data for dashboard"""
    try:
        # Get past hour data
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM sensor_readings
            WHERE utc_timestamp >= datetime('now', '-1 hour')
            ORDER BY utc_timestamp DESC
        ''')

        recent_data = []
        for row in cursor.fetchall():
            recent_data.append({
                'id': row['id'],
                'utc_timestamp': row['utc_timestamp'],
                'light': row['light'],
                'soil_moisture': row['soil_moisture'],
                'temperature': row['temperature'],
                'humidity': row['humidity']
            })

        conn.close()
        return jsonify(recent_data)

    except Exception as e:
        print(f"Error fetching recent data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/data/chart', methods=['GET'])
def get_chart_data():
    """Get sensor data for charts (past 3 days)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                strftime('%Y-%m-%d %H:00:00', utc_timestamp) as utc_timestamp,
                AVG(light) as light,
                AVG(soil_moisture) as soil_moisture,
                AVG(temperature) as temperature,
                AVG(humidity) as humidity
            FROM sensor_readings
            WHERE utc_timestamp >= datetime('now', '-3 days')
            GROUP BY strftime('%Y-%m-%d %H', utc_timestamp)
            ORDER BY utc_timestamp ASC
        ''')

        chart_data = []
        for row in cursor.fetchall():
            chart_data.append({
                'utc_timestamp': row['utc_timestamp'],
                'light': round(row['light'], 2) if row['light'] else 0,
                'soil_moisture': round(row['soil_moisture'], 2) if row['soil_moisture'] else 0,
                'temperature': round(row['temperature'], 2) if row['temperature'] else 0,
                'humidity': round(row['humidity'], 2) if row['humidity'] else 0
            })

        conn.close()
        return jsonify(chart_data)

    except Exception as e:
        print(f"Error fetching chart data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)