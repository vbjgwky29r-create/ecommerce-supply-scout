"""
陈艳红专用电商猎手 Web 服务
支持在微信浏览器中使用的轻量级Web应用，专为陈艳红定制
"""

import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'ecommerce-agent-secret-key-2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大上传16MB
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 创建SocketIO实例
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 导入Agent
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agents.agent import build_agent

# 全局变量：存储Agent实例和会话
agent_instances = {}
user_sessions = {}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_agent():
    """获取Agent实例（单例模式）"""
    if 'agent' not in agent_instances:
        try:
            logger.info("初始化Agent...")
            agent_instances['agent'] = build_agent()
            logger.info("Agent初始化成功")
        except Exception as e:
            logger.error(f"Agent初始化失败: {str(e)}")
            raise
    return agent_instances['agent']


def format_message(role, content, timestamp=None):
    """格式化消息"""
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    return {
        'role': role,
        'content': content,
        'timestamp': timestamp
    }


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': '没有上传文件'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': '没有选择文件'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'不支持的文件类型，仅支持: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'
        }), 400
    
    try:
        # 生成唯一文件名
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 构建可访问的URL
        file_url = f"/uploads/{filename}"
        
        logger.info(f"文件上传成功: {filename}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'url': file_url,
            'message': '文件上传成功'
        })
    
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'文件上传失败: {str(e)}'
        }), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@socketio.on('connect')
def handle_connect():
    """处理WebSocket连接"""
    logger.info(f"客户端连接: {request.sid}")
    emit('connected', {
        'message': '连接成功',
        'timestamp': datetime.now().isoformat()
    })


@socketio.on('disconnect')
def handle_disconnect():
    """处理WebSocket断开"""
    logger.info(f"客户端断开: {request.sid}")
    # 清理会话数据
    if request.sid in user_sessions:
        del user_sessions[request.sid]


@socketio.on('chat')
def handle_chat(data):
    """处理聊天消息"""
    try:
        user_message = data.get('message', '')
        image_url = data.get('image_url', None)
        
        logger.info(f"收到消息: {user_message[:100]}... (session: {request.sid})")
        
        # 发送用户消息确认
        emit('message', format_message('user', user_message))
        
        # 获取Agent实例
        agent = get_agent()
        
        # 获取或创建会话
        if request.sid not in user_sessions:
            # 生成唯一的thread_id
            thread_id = str(uuid.uuid4())
            user_sessions[request.sid] = {
                'thread_id': thread_id,
                'config': {
                    'configurable': {
                        'thread_id': thread_id
                    }
                }
            }
            logger.info(f"创建新会话: {thread_id}")
        
        session_config = user_sessions[request.sid]['config']
        
        # 构建输入消息
        from langchain_core.messages import HumanMessage
        import base64
        
        # 如果有图片，使用多模态消息
        if image_url:
            # 检查是否是相对路径，转换为绝对路径
            if image_url.startswith('/uploads/'):
                filename = image_url.replace('/uploads/', '')
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # 读取图片并转换为 base64
                try:
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
                    # 检测图片格式
                    import imghdr
                    image_format = imghdr.what(None, h=image_data)
                    if not image_format:
                        image_format = 'png'  # 默认使用 png
                    
                    # 转换为 base64
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    image_url = f"data:image/{image_format};base64,{image_base64}"
                    logger.info(f"图片已转换为 base64，格式: {image_format}, 大小: {len(image_base64)} 字符")
                except Exception as e:
                    logger.error(f"图片转换失败: {str(e)}")
                    raise
            
            input_message = HumanMessage(content=[
                {
                    "type": "text",
                    "text": user_message
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ])
        else:
            input_message = HumanMessage(content=user_message)
        
        # 构建输入
        inputs = {"messages": [input_message]}
        
        # 发送开始思考信号
        emit('thinking_start', {
            'message': '正在思考...'
        })
        
        # 流式调用Agent
        full_response = ""
        chunk_count = 0
        
        logger.info(f"开始流式调用 Agent...")
        
        for chunk in agent.stream(inputs, config=session_config):
            chunk_count += 1
            logger.info(f"收到 chunk #{chunk_count}: {list(chunk.keys())}")
            
            # 提取响应内容
            # 注意：LangGraph 流式输出格式为 {'model': {'messages': [...]}}
            if chunk and 'model' in chunk:
                logger.info(f"  chunk['model'] 存在")
                model_data = chunk.get('model', {})
                if 'messages' in model_data:
                    messages = model_data.get('messages', [])
                    logger.info(f"  消息数量: {len(messages)}")
                    
                    for i, msg in enumerate(messages):
                        if hasattr(msg, 'content'):
                            content = msg.content
                            logger.info(f"  消息 #{i}: content 类型={type(content)}, 长度={len(content) if isinstance(content, str) else 'N/A'}")
                            
                            if isinstance(content, str) and content:
                                # 流式发送响应
                                emit('message_chunk', {
                                    'content': content
                                })
                                full_response += content
                                logger.info(f"  发送 message_chunk, 累计长度: {len(full_response)}")
                else:
                    logger.warning(f"  chunk['model'] 中没有 'messages' 键")
            else:
                logger.warning(f"  chunk 中没有 'model' 键, 实际键: {list(chunk.keys())}")
        
        logger.info(f"流式调用完成，总 chunk 数: {chunk_count}, 完整响应长度: {len(full_response)}")
        
        # 发送完成信号
        emit('thinking_end', {})
        
        logger.info(f"响应完成，长度: {len(full_response)} (session: {request.sid})")
    
    except Exception as e:
        logger.error(f"处理聊天消息失败: {str(e)}", exc_info=True)
        emit('error', {
            'error': f'处理失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })


@socketio.on('clear_history')
def handle_clear_history():
    """清除对话历史"""
    try:
        # 删除当前会话
        if request.sid in user_sessions:
            del user_sessions[request.sid]
            logger.info(f"清除会话历史: {request.sid}")
        
        emit('history_cleared', {
            'message': '对话历史已清除',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"清除历史失败: {str(e)}")
        emit('error', {
            'error': f'操作失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })


if __name__ == '__main__':
    logger.info("启动电商货源猎手 Web 服务...")
    
    # 获取配置 - 优先使用 Render 的 PORT 环境变量
    host = os.getenv('WEB_HOST', '0.0.0.0')
    port = int(os.getenv('PORT', os.getenv('WEB_PORT', 5000)))
    debug = os.getenv('WEB_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"服务地址: http://{host}:{port}")
    
    # 启动服务
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
