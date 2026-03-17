from flask import Flask, request, jsonify, render_template
import requests
import os
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename

# Nhập "bộ não" AI từ file ai_vision.py cùng thư mục
from ai_vision import is_actually_water, analyze_water_advanced

app = Flask(__name__)

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
API_TOKEN = '5cc015e8e495db3d1fdd839bafb7084067db387b'
CITY_SLUG = 'hanoi'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DB_FILE = 'eco_data.db'

# ==========================================
# CƠ SỞ DỮ LIỆU (SQLITE)
# ==========================================
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS env_history 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, city TEXT, aqi INTEGER, 
                     temp REAL, humidity REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS water_history 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, quality TEXT, color TEXT, 
                     is_fake_image BOOLEAN, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db() # Khởi tạo bảng ngay khi chạy server

# ==========================================
# API ROUTER
# ==========================================
@app.route('/')
def home():
    return render_template('template.html') 

@app.route('/api/environment', methods=['GET'])
def get_environment():
    url = f"https://api.waqi.info/feed/{CITY_SLUG}/?token={API_TOKEN}"
    try:
        response = requests.get(url, verify=False) 
        data = response.json()
        
        if data['status'] == 'ok':
            result = data['data']
            iaqi = result.get('iaqi', {})
            
            city_name = result.get('city', {}).get('name', 'Chưa rõ')
            aqi_val = result.get('aqi', 0)
            temp_val = iaqi.get('t', {}).get('v', 0)
            hum_val = iaqi.get('h', {}).get('v', 0)
            
            # Lưu lịch sử Không khí
            conn = get_db_connection()
            conn.execute('INSERT INTO env_history (city, aqi, temp, humidity) VALUES (?, ?, ?, ?)',
                         (city_name, aqi_val, temp_val, hum_val))
            conn.commit()
            conn.close()

            return jsonify({
                "status": "success",
                "data": {"city": city_name, "aqi": aqi_val, "temp": temp_val, 
                         "humidity": hum_val, "timestamp": datetime.now().isoformat()}
            })
        return jsonify({"status": "error", "message": "Lỗi API WAQI"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/analyze_water', methods=['POST'])
def analyze_water():
    if 'image' not in request.files: return jsonify({"status": "error"}), 400
    
    file = request.files['image']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(filepath)

    # 1. KIỂM DUYỆT ẢNH BẰNG AI (Lớp 1)
    if not is_actually_water(filepath):
        # Lưu vào lịch sử những kẻ cố tình up ảnh sai
        conn = get_db_connection()
        conn.execute('INSERT INTO water_history (quality, color, is_fake_image) VALUES (?, ?, ?)',
                     ("Ảnh không hợp lệ", "Không xác định", True))
        conn.commit()
        conn.close()
        os.remove(filepath)
        return jsonify({
            "status": "success", 
            "data": {"quality": "AI TỪ CHỐI: Vui lòng chụp mặt nước!", "color": "#ff4757"}
        })

    # 2. PHÂN TÍCH QUANG PHỔ NƯỚC (Lớp 3)
    result = analyze_water_advanced(filepath)
    os.remove(filepath)

    if result:
        # Lưu lịch sử đo nước thành công
        conn = get_db_connection()
        conn.execute('INSERT INTO water_history (quality, color, is_fake_image) VALUES (?, ?, ?)',
                     (result['quality'], result['color'], False))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "data": result})
    return jsonify({"status": "error"}), 500

@app.route('/api/history/aqi', methods=['GET'])
def get_aqi_history():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM env_history ORDER BY id DESC LIMIT 15').fetchall()
    conn.close()
    return jsonify({"status": "success", "data": [dict(row) for row in rows]})

# ==========================================
# KHỞI CHẠY HỆ THỐNG
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)