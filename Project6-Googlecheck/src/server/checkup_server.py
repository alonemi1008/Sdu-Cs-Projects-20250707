import time
import json
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from ..database.breach_db import BreachDatabase
from ..utils.constants import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT


class CheckupServer:
    """
    Password Checkup服务器
    实现Google Password Checkup协议的服务器端
    """
    
    def __init__(self, database_path: str = "breach_db", 
                 server_private_key: Optional[bytes] = None):
        """
        初始化服务器
        
        Args:
            database_path: 数据库存储路径
            server_private_key: 服务器私钥
        """
        self.app = Flask(__name__)
        self.database = BreachDatabase(database_path, server_private_key)
        
        # 统计信息
        self.query_count = 0
        self.total_query_time = 0.0
        self.start_time = time.time()
        
        # 注册路由
        self._register_routes()
    
    def _register_routes(self):
        """
        注册Flask路由
        """
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """健康检查端点"""
            return jsonify({
                "status": "healthy",
                "timestamp": time.time(),
                "uptime": time.time() - self.start_time
            })
        
        @self.app.route('/info', methods=['GET'])
        def server_info():
            """服务器信息端点"""
            db_stats = self.database.get_database_statistics()
            
            return jsonify({
                "server_info": {
                    "version": "1.0.0",
                    "protocol": "Google Password Checkup",
                    "uptime": time.time() - self.start_time,
                    "total_queries": self.query_count,
                    "average_query_time": (self.total_query_time / self.query_count 
                                         if self.query_count > 0 else 0)
                },
                "database_info": db_stats
            })
        
        @self.app.route('/query', methods=['POST'])
        def process_query():
            """处理密码检查查询"""
            start_time = time.time()
            
            try:
                # 解析请求数据
                data = request.get_json()
                if not data:
                    return jsonify({"error": "无效的请求数据"}), 400
                
                blinded_hash_hex = data.get("blinded_hash")
                shard_prefix_hex = data.get("shard_prefix")
                
                if not blinded_hash_hex or not shard_prefix_hex:
                    return jsonify({"error": "缺少必要参数"}), 400
                
                # 将十六进制字符串转换为字节
                blinded_hash = bytes.fromhex(blinded_hash_hex)
                shard_prefix = bytes.fromhex(shard_prefix_hex)
                
                # 获取对应分片的数据
                shard_data = self.database.shard_manager.get_shard_data(shard_prefix)
                
                # 使用PSI协议处理查询
                double_blinded_hash, blinded_shard_data = self.database.psi_protocol.server_process_query(
                    blinded_hash, shard_prefix, shard_data
                )
                
                # 准备响应数据
                response_data = {
                    "double_blinded_hash": double_blinded_hash.hex(),
                    "blinded_shard_data": [item.hex() for item in blinded_shard_data]
                }
                
                # 更新统计信息
                self.query_count += 1
                self.total_query_time += time.time() - start_time
                
                return jsonify(response_data)
                
            except Exception as e:
                return jsonify({"error": f"处理查询时发生错误: {str(e)}"}), 500
        
        @self.app.route('/statistics', methods=['GET'])
        def get_statistics():
            """获取服务器统计信息"""
            return jsonify({
                "server_stats": {
                    "total_queries": self.query_count,
                    "total_query_time": self.total_query_time,
                    "average_query_time": (self.total_query_time / self.query_count 
                                         if self.query_count > 0 else 0),
                    "uptime": time.time() - self.start_time
                },
                "database_stats": self.database.get_database_statistics()
            })
        
        @self.app.route('/admin/add_breach', methods=['POST'])
        def add_breach_data():
            """管理员端点：添加泄露数据"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "无效的请求数据"}), 400
                
                credentials = data.get("credentials", [])
                breach_name = data.get("breach_name", "未命名泄露")
                
                if not credentials:
                    return jsonify({"error": "未提供凭证数据"}), 400
                
                # 转换凭证格式
                credential_list = [(cred["username"], cred["password"]) 
                                 for cred in credentials]
                
                # 添加到数据库
                self.database.add_breach_data(credential_list, breach_name)
                
                return jsonify({
                    "message": f"成功添加 {len(credential_list)} 条凭证",
                    "breach_name": breach_name
                })
                
            except Exception as e:
                return jsonify({"error": f"添加泄露数据时发生错误: {str(e)}"}), 500
        
        @self.app.route('/admin/simulate_data', methods=['POST'])
        def simulate_breach_data():
            """管理员端点：生成模拟泄露数据"""
            try:
                data = request.get_json()
                count = data.get("count", 1000) if data else 1000
                
                self.database.simulate_breach_data(count)
                
                return jsonify({
                    "message": f"成功生成 {count} 条模拟泄露数据"
                })
                
            except Exception as e:
                return jsonify({"error": f"生成模拟数据时发生错误: {str(e)}"}), 500
        
        @self.app.route('/admin/clear_database', methods=['POST'])
        def clear_database():
            """管理员端点：清空数据库"""
            try:
                self.database.clear_database()
                return jsonify({"message": "数据库已清空"})
            except Exception as e:
                return jsonify({"error": f"清空数据库时发生错误: {str(e)}"}), 500
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"error": "端点不存在"}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({"error": "服务器内部错误"}), 500
    
    def run(self, host: str = DEFAULT_SERVER_HOST, port: int = DEFAULT_SERVER_PORT, 
            debug: bool = False):
        """
        启动服务器
        
        Args:
            host: 主机地址
            port: 端口号
            debug: 是否启用调试模式
        """
        print(f"启动Password Checkup服务器...")
        print(f"地址: http://{host}:{port}")
        print(f"数据库统计: {self.database.get_database_statistics()}")
        
        self.app.run(host=host, port=port, debug=debug)
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            数据库统计信息
        """
        return self.database.get_database_statistics()
    
    def add_breach_data(self, credentials: list, breach_name: str = ""):
        """
        添加泄露数据到数据库
        
        Args:
            credentials: 凭证列表
            breach_name: 泄露事件名称
        """
        self.database.add_breach_data(credentials, breach_name)
    
    def simulate_breach_data(self, count: int = 1000):
        """
        生成模拟泄露数据
        
        Args:
            count: 生成数量
        """
        self.database.simulate_breach_data(count)
    
    def clear_database(self):
        """
        清空数据库
        """
        self.database.clear_database()
    
    def save_database(self):
        """
        保存数据库
        """
        self.database.save_database()


def create_server(database_path: str = "breach_db", 
                 server_private_key: Optional[bytes] = None) -> CheckupServer:
    """
    创建服务器实例
    
    Args:
        database_path: 数据库路径
        server_private_key: 服务器私钥
        
    Returns:
        服务器实例
    """
    return CheckupServer(database_path, server_private_key) 