import time
import requests
from typing import Optional, Dict, Any
from ..crypto.psi_protocol import PSIProtocol
from ..utils.canonicalize import canonicalize_username, validate_credentials
from ..utils.constants import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT, QUERY_TIMEOUT


class PasswordChecker:
    """
    密码检查器客户端
    实现Google Password Checkup协议的客户端部分
    """
    
    def __init__(self, server_host: str = DEFAULT_SERVER_HOST, 
                 server_port: int = DEFAULT_SERVER_PORT):
        """
        初始化密码检查器
        
        Args:
            server_host: 服务器主机地址
            server_port: 服务器端口
        """
        self.server_host = server_host
        self.server_port = server_port
        self.server_url = f"http://{server_host}:{server_port}"
        self.psi_protocol = PSIProtocol()
        
        # 统计信息
        self.query_count = 0
        self.breach_found_count = 0
        self.total_query_time = 0.0
    
    def check_credentials(self, username: str, password: str, 
                         timeout: int = QUERY_TIMEOUT) -> bool:
        """
        检查凭证是否在泄露数据库中
        
        Args:
            username: 用户名
            password: 密码
            timeout: 查询超时时间（秒）
            
        Returns:
            是否在泄露数据库中找到匹配
        """
        start_time = time.time()
        
        try:
            # 验证凭证格式
            if not validate_credentials(username, password):
                print("凭证格式无效")
                return False
            
            print(f"正在检查凭证: {canonicalize_username(username)}")
            
            # 客户端准备查询
            print("步骤1: 准备查询请求...")
            blinded_hash, shard_prefix, client_key = self.psi_protocol.client_prepare_query(
                username, password
            )
            
            # 发送查询请求到服务器
            print("步骤2: 发送查询到服务器...")
            response_data = self._send_query_request(blinded_hash, shard_prefix, timeout)
            
            if response_data is None:
                print("服务器查询失败")
                return False
            
            # 客户端处理响应
            print("步骤3: 处理服务器响应...")
            is_breached = self.psi_protocol.client_process_response(
                response_data["double_blinded_hash"],
                response_data["blinded_shard_data"],
                client_key
            )
            
            # 更新统计信息
            self.query_count += 1
            if is_breached:
                self.breach_found_count += 1
            
            elapsed_time = time.time() - start_time
            self.total_query_time += elapsed_time
            
            print(f"查询完成，耗时: {elapsed_time:.2f}秒")
            
            return is_breached
            
        except Exception as e:
            print(f"查询凭证时发生错误: {e}")
            return False
    
    def _send_query_request(self, blinded_hash: bytes, shard_prefix: bytes, 
                           timeout: int) -> Optional[Dict[str, Any]]:
        """
        发送查询请求到服务器
        
        Args:
            blinded_hash: 盲化哈希
            shard_prefix: 分片前缀
            timeout: 超时时间
            
        Returns:
            服务器响应数据
        """
        try:
            # 准备请求数据
            request_data = {
                "blinded_hash": blinded_hash.hex(),
                "shard_prefix": shard_prefix.hex()
            }
            
            # 发送POST请求
            response = requests.post(
                f"{self.server_url}/query",
                json=request_data,
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 将十六进制字符串转换回字节
                return {
                    "double_blinded_hash": bytes.fromhex(data["double_blinded_hash"]),
                    "blinded_shard_data": [
                        bytes.fromhex(item) for item in data["blinded_shard_data"]
                    ]
                }
            else:
                print(f"服务器返回错误: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("查询超时")
            return None
        except requests.exceptions.ConnectionError:
            print("无法连接到服务器")
            return None
        except Exception as e:
            print(f"发送查询请求时发生错误: {e}")
            return None
    
    def check_password_only(self, password: str, username: str = "user") -> bool:
        """
        仅检查密码（使用默认用户名）
        
        Args:
            password: 密码
            username: 默认用户名
            
        Returns:
            是否在泄露数据库中找到匹配
        """
        return self.check_credentials(username, password)
    
    def batch_check_credentials(self, credentials: list, 
                              show_progress: bool = True) -> Dict[str, bool]:
        """
        批量检查凭证
        
        Args:
            credentials: 凭证列表 [(username, password), ...]
            show_progress: 是否显示进度
            
        Returns:
            检查结果字典
        """
        results = {}
        total_count = len(credentials)
        
        print(f"开始批量检查 {total_count} 个凭证...")
        
        for i, (username, password) in enumerate(credentials):
            if show_progress:
                print(f"进度: {i+1}/{total_count}")
            
            key = f"{username}:{password}"
            results[key] = self.check_credentials(username, password)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取客户端统计信息
        
        Returns:
            统计信息字典
        """
        avg_query_time = (self.total_query_time / self.query_count 
                         if self.query_count > 0 else 0)
        
        return {
            "total_queries": self.query_count,
            "breaches_found": self.breach_found_count,
            "breach_rate": (self.breach_found_count / self.query_count 
                           if self.query_count > 0 else 0),
            "total_query_time": self.total_query_time,
            "average_query_time": avg_query_time
        }
    
    def reset_statistics(self):
        """
        重置统计信息
        """
        self.query_count = 0
        self.breach_found_count = 0
        self.total_query_time = 0.0
    
    def test_connection(self) -> bool:
        """
        测试与服务器的连接
        
        Returns:
            是否连接成功
        """
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_server_info(self) -> Optional[Dict[str, Any]]:
        """
        获取服务器信息
        
        Returns:
            服务器信息字典
        """
        try:
            response = requests.get(f"{self.server_url}/info", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None 