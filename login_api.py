from flask import Flask, request, jsonify
import psycopg2
from flask_cors import CORS
import hashlib

DATABASE_URL = "postgresql://neondb_owner:npg_rdOxG4P1aAeJ@ep-steep-violet-a1h5hgsu-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, zhanghao, mima, name, phone FROM users WHERE zhanghao = %s",
            (username,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            stored_password = user[2]
            
            if stored_password == password:
                return jsonify({
                    'success': True,
                    'message': '登录成功',
                    'user': {
                        'id': user[0],
                        'zhanghao': user[1],
                        'name': user[3],
                        'phone': user[4]
                    }
                }), 200
            else:
                return jsonify({'success': False, 'message': '密码错误'}), 401
        else:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
            
    except psycopg2.Error as e:
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE zhanghao = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (zhanghao, mima) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': '注册成功'}), 201
        
    except psycopg2.Error as e:
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
