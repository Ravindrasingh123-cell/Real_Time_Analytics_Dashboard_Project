from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import random
import time
import threading
import json
from datetime import datetime, timedelta
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Global data storage
analytics_data = {
    'users': [],
    'sales': [],
    'page_views': [],
    'conversions': [],
    'revenue': []
}

def generate_sample_data():
    """Generate sample analytics data"""
    current_time = datetime.now()
    
    # Generate user data (last 30 days)
    for i in range(30):
        date = current_time - timedelta(days=29-i)
        users = random.randint(800, 1200) + random.randint(-100, 100)
        analytics_data['users'].append({
            'date': date.strftime('%Y-%m-%d'),
            'count': users
        })
    
    # Generate sales data
    for i in range(30):
        date = current_time - timedelta(days=29-i)
        sales = random.randint(50, 150) + random.randint(-20, 20)
        analytics_data['sales'].append({
            'date': date.strftime('%Y-%m-%d'),
            'amount': sales
        })
    
    # Generate page views
    for i in range(30):
        date = current_time - timedelta(days=29-i)
        views = random.randint(2000, 5000) + random.randint(-500, 500)
        analytics_data['page_views'].append({
            'date': date.strftime('%Y-%m-%d'),
            'count': views
        })
    
    # Generate conversion data
    for i in range(30):
        date = current_time - timedelta(days=29-i)
        conversions = random.randint(20, 80) + random.randint(-10, 10)
        analytics_data['conversions'].append({
            'date': date.strftime('%Y-%m-%d'),
            'count': conversions
        })
    
    # Generate revenue data
    for i in range(30):
        date = current_time - timedelta(days=29-i)
        revenue = random.randint(10000, 25000) + random.randint(-2000, 2000)
        analytics_data['revenue'].append({
            'date': date.strftime('%Y-%m-%d'),
            'amount': revenue
        })

def real_time_data_generator():
    """Generate real-time data updates"""
    while True:
        time.sleep(2)  # Update every 2 seconds
        
        # Generate new real-time metrics
        real_time_metrics = {
            'timestamp': datetime.now().isoformat(),
            'active_users': random.randint(150, 300),
            'current_sales': random.randint(5, 25),
            'page_views_per_minute': random.randint(50, 150),
            'conversion_rate': round(random.uniform(2.5, 8.5), 2),
            'revenue_per_hour': random.randint(500, 1500),
            'bounce_rate': round(random.uniform(25, 45), 2),
            'avg_session_duration': random.randint(120, 300)
        }
        
        # Emit real-time data to all connected clients
        socketio.emit('real_time_data', real_time_metrics)
        
        # Update historical data with new data point
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Add new data point to users
        new_users = random.randint(800, 1200)
        analytics_data['users'].append({
            'date': current_date,
            'count': new_users
        })
        
        # Keep only last 30 days of data
        if len(analytics_data['users']) > 30:
            analytics_data['users'] = analytics_data['users'][-30:]
            analytics_data['sales'] = analytics_data['sales'][-30:]
            analytics_data['page_views'] = analytics_data['page_views'][-30:]
            analytics_data['conversions'] = analytics_data['conversions'][-30:]
            analytics_data['revenue'] = analytics_data['revenue'][-30:]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analytics')
def get_analytics():
    """Get historical analytics data"""
    return json.dumps(analytics_data)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('analytics_data', analytics_data)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_data')
def handle_data_request():
    """Handle client request for data"""
    emit('analytics_data', analytics_data)

if __name__ == '__main__':
    # Generate initial sample data
    generate_sample_data()
    
    # Start real-time data generation in a separate thread
    data_thread = threading.Thread(target=real_time_data_generator)
    data_thread.daemon = True
    data_thread.start()
    
    # Run the Flask-SocketIO app
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
