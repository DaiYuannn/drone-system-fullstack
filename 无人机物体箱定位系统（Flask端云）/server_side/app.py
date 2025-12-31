"""
Flask Web应用主程序
提供REST API和WebSocket服务
"""
import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import socketio
import eventlet
from database import DatabaseManager
try:
    from security.crypto_adapter import maybe_decrypt_request
except Exception:
    def maybe_decrypt_request(data):
        return data
import config

# 设置日志
def setup_logging():
    """设置日志配置"""
    os.makedirs(os.path.dirname(config.LOG_CONFIG['file']), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_CONFIG['level']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_CONFIG['file']),
            logging.StreamHandler()
        ]
    )

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 创建SocketIO实例
sio = socketio.Server(cors_allowed_origins="*")
app_sio = socketio.WSGIApp(sio, app)

# 创建数据库管理器
db_manager = DatabaseManager()

# 存储连接的客户端
connected_clients = set()

@sio.event
def connect(sid, environ):
    """WebSocket连接事件"""
    connected_clients.add(sid)
    logging.info(f"客户端连接: {sid}")
    
    # 发送欢迎消息
    sio.emit('message', {
        'type': 'welcome',
        'message': '连接成功',
        'timestamp': datetime.now().isoformat()
    }, room=sid)

@sio.event
def disconnect(sid):
    """WebSocket断开连接事件"""
    connected_clients.discard(sid)
    logging.info(f"客户端断开连接: {sid}")

def broadcast_data(data):
    """广播数据到所有连接的客户端"""
    if connected_clients:
        sio.emit('new_detection', data, room=None)
        logging.debug(f"广播数据到 {len(connected_clients)} 个客户端")

# Flask路由
def _get_mapbox_token():
    try:
        sec = getattr(config, 'SECURITY_CONFIG', {}) or {}
    except Exception:
        sec = {}
    return os.getenv('MAPBOX_TOKEN') or sec.get('mapbox_token')

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', mapbox_token=_get_mapbox_token())

@app.route('/api/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'connected_clients': len(connected_clients)
    })

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """接收无人机上传的数据"""
    try:
        data = request.json
        data = maybe_decrypt_request(data) if isinstance(data, dict) else data
        
        if not data:
            return jsonify({'status': 'error', 'message': '无效的数据'}), 400
        
        # 验证必要字段
        required_fields = ['timestamp', 'drone_id', 'barcode_data', 'confidence']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'缺少必要字段: {field}'}), 400
        
        # 存储到数据库
        if db_manager.insert_box_position(data):
            # 广播数据到WebSocket客户端
            broadcast_data(data)
            
            return jsonify({
                'status': 'success',
                'message': '数据存储成功',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'status': 'error', 'message': '数据存储失败'}), 500
            
    except Exception as e:
        logging.error(f"数据上传处理失败: {e}")
        return jsonify({'status': 'error', 'message': '服务器内部错误'}), 500

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """接收无人机心跳"""
    try:
        data = request.json
        data = maybe_decrypt_request(data) if isinstance(data, dict) else data
        
        if not data or 'drone_id' not in data:
            return jsonify({'status': 'error', 'message': '无效的心跳数据'}), 400
        
        # 更新无人机状态
        status_data = {
            'status': 'online',
            'gps': data.get('gps'),
            'battery_level': data.get('battery_level'),
            'signal_strength': data.get('signal_strength')
        }
        
        if db_manager.update_drone_status(data['drone_id'], status_data):
            return jsonify({
                'status': 'success',
                'message': '心跳更新成功',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'status': 'error', 'message': '心跳更新失败'}), 500
            
    except Exception as e:
        logging.error(f"心跳处理失败: {e}")
        return jsonify({'status': 'error', 'message': '服务器内部错误'}), 500

@app.route('/api/positions')
def get_positions():
    """获取位置数据"""
    try:
        limit = request.args.get('limit', 100, type=int)
        drone_id = request.args.get('drone_id')
        
        positions = db_manager.get_recent_positions(limit, drone_id)
        
        return jsonify({
            'status': 'success',
            'data': positions,
            'count': len(positions),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"获取位置数据失败: {e}")
        return jsonify({'status': 'error', 'message': '获取数据失败'}), 500

@app.route('/api/drones')
def get_drones():
    """获取无人机状态"""
    try:
        drone_id = request.args.get('drone_id')
        drones = db_manager.get_drone_status(drone_id)
        
        return jsonify({
            'status': 'success',
            'data': drones,
            'count': len(drones),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"获取无人机状态失败: {e}")
        return jsonify({'status': 'error', 'message': '获取数据失败'}), 500

@app.route('/api/statistics')
def get_statistics():
    """获取系统统计信息"""
    try:
        stats = db_manager.get_statistics()
        
        return jsonify({
            'status': 'success',
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"获取统计信息失败: {e}")
        return jsonify({'status': 'error', 'message': '获取统计信息失败'}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_data():
    """清理旧数据"""
    try:
        days = request.json.get('days') if request.json else None
        
        if db_manager.cleanup_old_data(days):
            return jsonify({
                'status': 'success',
                'message': '数据清理完成',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'status': 'error', 'message': '数据清理失败'}), 500
            
    except Exception as e:
        logging.error(f"数据清理失败: {e}")
        return jsonify({'status': 'error', 'message': '数据清理失败'}), 500

# 静态文件服务
@app.route('/static/<path:filename>')
def static_files(filename):
    """提供静态文件"""
    return send_from_directory('static', filename)

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': '服务器内部错误'}), 500

# ----- 管理端点（测试/演示用途） -----
def _get_admin_token():
    try:
        sec = getattr(config, 'SECURITY_CONFIG', {}) or {}
    except Exception:
        sec = {}
    return os.getenv('ADMIN_TOKEN') or sec.get('admin_token')

def _check_admin(req_json) -> bool:
    expect = _get_admin_token()
    if not expect:
        # 未配置令牌则默认不开放管理端点
        return False
    token = request.headers.get('X-Admin-Token') or (req_json or {}).get('admin_token')
    return token == expect

@app.route('/api/admin/positions/clear', methods=['POST'])
def admin_clear_positions():
    body = request.json or {}
    if not _check_admin(body):
        return jsonify({'status':'error','message':'未授权'}), 403
    if not body.get('confirm'):
        return jsonify({'status':'error','message':'需要确认(confirm=true)'}), 400
    ok = db_manager.clear_positions()
    return jsonify({'status':'success' if ok else 'error'})

@app.route('/api/admin/drones/clear', methods=['POST'])
def admin_clear_drones():
    body = request.json or {}
    if not _check_admin(body):
        return jsonify({'status':'error','message':'未授权'}), 403
    if not body.get('confirm'):
        return jsonify({'status':'error','message':'需要确认(confirm=true)'}), 400
    ok = db_manager.clear_drones()
    return jsonify({'status':'success' if ok else 'error'})

@app.route('/api/admin/positions/delete', methods=['POST'])
def admin_delete_positions():
    body = request.json or {}
    if not _check_admin(body):
        return jsonify({'status':'error','message':'未授权'}), 403
    ids = body.get('ids') or []
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return jsonify({'status':'error','message':'ids 需要为整数列表'}), 400
    if not body.get('confirm'):
        return jsonify({'status':'error','message':'需要确认(confirm=true)'}), 400
    ok = db_manager.delete_positions(ids)
    return jsonify({'status':'success' if ok else 'error'})

@app.route('/api/admin/positions/update', methods=['POST'])
def admin_update_position():
    body = request.json or {}
    if not _check_admin(body):
        return jsonify({'status':'error','message':'未授权'}), 403
    pid = body.get('id')
    fields = body.get('fields') or {}
    if not isinstance(pid, int) or not isinstance(fields, dict):
        return jsonify({'status':'error','message':'需要 id(int) 与 fields(dict)'}), 400
    ok = db_manager.update_position(pid, fields)
    return jsonify({'status':'success' if ok else 'error'})

def initialize_database():
    """初始化数据库"""
    if db_manager.connect():
        if db_manager.create_tables():
            logging.info("数据库初始化成功")
            return True
        else:
            logging.error("数据库表创建失败")
            return False
    else:
        logging.error("数据库连接失败")
        return False

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 初始化数据库
    if not initialize_database():
        logging.error("数据库初始化失败，程序退出")
        return
    
    # 启动服务器
    logging.info("启动服务器...")
    eventlet.wsgi.server(
        eventlet.listen((config.FLASK_CONFIG['host'], config.FLASK_CONFIG['port'])),
        app_sio,
        log=logging.getLogger('eventlet')
    )

if __name__ == '__main__':
    main()
 
