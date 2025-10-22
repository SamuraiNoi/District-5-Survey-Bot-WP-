#!/usr/bin/env python3
"""
District 5 Survey Backend Server
Flask application to serve survey form and collect responses
"""

import os
import json
import csv
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3


app = Flask(__name__)
CORS(app)

# Database configuration
DB_FILE = 'survey_responses.db'
DATA_DIR = 'data'


def init_database():
    """Initialize SQLite database with survey responses table"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    db_path = os.path.join(DATA_DIR, DB_FILE)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            neighborhood TEXT NOT NULL,
            age_group TEXT NOT NULL,
            voting_frequency TEXT NOT NULL,
            issues TEXT NOT NULL,
            engagement TEXT NOT NULL,
            additional_comments TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")


def save_to_database(data):
    """Save survey response to SQLite database"""
    db_path = os.path.join(DATA_DIR, DB_FILE)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO responses (
            phone_number, name, email, neighborhood, age_group,
            voting_frequency, issues, engagement, additional_comments, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['phoneNumber'],
        data['name'],
        data.get('email', ''),
        data['neighborhood'],
        data['ageGroup'],
        data['votingFrequency'],
        json.dumps(data['issues']),  # Store array as JSON string
        data['engagement'],
        data.get('additionalComments', ''),
        data['timestamp']
    ))
    
    conn.commit()
    response_id = cursor.lastrowid
    conn.close()
    
    return response_id


def save_to_json(data):
    """Save survey response to JSON file for backup"""
    json_file = os.path.join(DATA_DIR, 'responses.json')
    
    # Load existing responses or create empty list
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            responses = json.load(f)
    else:
        responses = []
    
    # Add new response
    responses.append(data)
    
    # Save back to file
    with open(json_file, 'w') as f:
        json.dump(responses, f, indent=2)


@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'survey.html')


@app.route('/survey.html')
def survey():
    """Serve the survey page"""
    return send_from_directory('.', 'survey.html')


@app.route('/api/submit-survey', methods=['POST'])
def submit_survey():
    """Handle survey submission"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'phoneNumber', 'name', 'neighborhood', 
            'ageGroup', 'votingFrequency', 'engagement'
        ]
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate issues array
        if not data.get('issues') or len(data['issues']) == 0:
            return jsonify({
                'error': 'At least one issue must be selected'
            }), 400
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        # Save to database
        response_id = save_to_database(data)
        
        # Also save to JSON for backup
        save_to_json(data)
        
        print(f"Survey response saved (ID: {response_id}) from {data['name']}")
        
        return jsonify({
            'success': True,
            'message': 'Survey response saved successfully',
            'id': response_id
        }), 200
    
    except Exception as e:
        print(f"Error saving survey response: {str(e)}")
        return jsonify({
            'error': 'Failed to save survey response',
            'details': str(e)
        }), 500


@app.route('/api/responses', methods=['GET'])
def get_responses():
    """Get all survey responses (for admin/analysis)"""
    try:
        db_path = os.path.join(DATA_DIR, DB_FILE)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM responses ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        
        responses = []
        for row in rows:
            response = dict(row)
            # Parse issues JSON string back to array
            response['issues'] = json.loads(response['issues'])
            responses.append(response)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(responses),
            'responses': responses
        }), 200
    
    except Exception as e:
        print(f"Error fetching responses: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch responses',
            'details': str(e)
        }), 500


@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    """Export survey responses to CSV format"""
    try:
        db_path = os.path.join(DATA_DIR, DB_FILE)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM responses ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        
        csv_file = os.path.join(DATA_DIR, f'responses_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        with open(csv_file, 'w', newline='') as f:
            if rows:
                # Get column names
                columns = rows[0].keys()
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                
                for row in rows:
                    writer.writerow(dict(row))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'CSV exported successfully',
            'filename': csv_file
        }), 200
    
    except Exception as e:
        print(f"Error exporting CSV: {str(e)}")
        return jsonify({
            'error': 'Failed to export CSV',
            'details': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get survey statistics"""
    try:
        db_path = os.path.join(DATA_DIR, DB_FILE)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Total responses
        cursor.execute('SELECT COUNT(*) as total FROM responses')
        total = cursor.fetchone()[0]
        
        # Responses by neighborhood
        cursor.execute('''
            SELECT neighborhood, COUNT(*) as count 
            FROM responses 
            GROUP BY neighborhood
        ''')
        by_neighborhood = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Responses by age group
        cursor.execute('''
            SELECT age_group, COUNT(*) as count 
            FROM responses 
            GROUP BY age_group
        ''')
        by_age = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Responses by voting frequency
        cursor.execute('''
            SELECT voting_frequency, COUNT(*) as count 
            FROM responses 
            GROUP BY voting_frequency
        ''')
        by_voting = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'by_neighborhood': by_neighborhood,
                'by_age_group': by_age,
                'by_voting_frequency': by_voting
            }
        }), 200
    
    except Exception as e:
        print(f"Error fetching stats: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch statistics',
            'details': str(e)
        }), 500


if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 5000))
    
    print(f"\n{'='*60}")
    print(f"District 5 Survey Backend Server")
    print(f"{'='*60}")
    print(f"Server starting on http://localhost:{port}")
    print(f"Survey available at http://localhost:{port}/survey.html")
    print(f"{'='*60}\n")
    
    # Run the server
    app.run(host='0.0.0.0', port=port, debug=True)
