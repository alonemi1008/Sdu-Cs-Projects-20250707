import os
import json
import time
from typing import List, Dict, Tuple, Optional
from .shard_manager import ShardManager
from ..crypto.psi_protocol import PSIProtocol
from ..utils.canonicalize import canonicalize_username, validate_credentials


class BreachDatabase:
    """
    泄露数据库管理器
    负责管理和查询泄露凭证数据库
    """
    
    def __init__(self, storage_path: str = "breach_db", server_private_key: Optional[bytes] = None):
        """
        初始化泄露数据库
        
        Args:
            storage_path: 数据库存储路径
            server_private_key: 服务器私钥
        """
        self.storage_path = storage_path
        self.shard_manager = ShardManager(os.path.join(storage_path, "shards"))
        self.psi_protocol = PSIProtocol(server_private_key)
        
        # 创建存储目录
        os.makedirs(storage_path, exist_ok=True)
        
        # 加载元数据
        self.metadata = self._load_metadata()
    
    def add_breach_data(self, credentials: List[Tuple[str, str]], breach_name: str = ""):
        """
        添加泄露数据到数据库
        
        Args:
            credentials: 凭证列表 [(username, password), ...]
            breach_name: 泄露事件名称
        """
        print(f"正在处理泄露数据: {breach_name}")
        print(f"凭证数量: {len(credentials)}")
        
        start_time = time.time()
        processed_count = 0
        
        for username, password in credentials:
            # 验证凭证格式
            if not validate_credentials(username, password):
                continue
            
            try:
                # 创建数据库条目
                credential_hash, shard_prefix = self.psi_protocol.create_breach_database_entry(
                    username, password
                )
                
                # 对条目进行盲化
                blinded_hash = self.psi_protocol.blind_database_entry(credential_hash)
                
                # 添加到分片
                self.shard_manager.add_credential(credential_hash, blinded_hash)
                
                processed_count += 1
                
                # 每处理1000条记录显示进度
                if processed_count % 1000 == 0:
                    elapsed = time.time() - start_time
                    print(f"已处理 {processed_count}/{len(credentials)} 条记录 ({elapsed:.2f}秒)")
                    
            except Exception as e:
                print(f"处理凭证失败 {username}: {e}")
                continue
        
        # 更新元数据
        self.metadata["breaches"].append({
            "name": breach_name,
            "credential_count": processed_count,
            "added_time": time.time()
        })
        
        self.metadata["total_credentials"] += processed_count
        
        # 保存数据
        self.save_database()
        
        elapsed = time.time() - start_time
        print(f"泄露数据处理完成: {processed_count} 条记录，耗时 {elapsed:.2f} 秒")
    
    def query_credential(self, username: str, password: str) -> bool:
        """
        查询凭证是否在泄露数据库中
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            是否在泄露数据库中
        """
        if not validate_credentials(username, password):
            return False
        
        try:
            # 客户端准备查询
            blinded_hash, shard_prefix, client_key = self.psi_protocol.client_prepare_query(
                username, password
            )
            
            # 获取对应分片的数据
            shard_data = self.shard_manager.get_shard_data(shard_prefix)
            
            # 服务器处理查询
            double_blinded_hash, blinded_shard_data = self.psi_protocol.server_process_query(
                blinded_hash, shard_prefix, shard_data
            )
            
            # 客户端处理响应
            is_breached = self.psi_protocol.client_process_response(
                double_blinded_hash, blinded_shard_data, client_key
            )
            
            return is_breached
            
        except Exception as e:
            print(f"查询凭证失败: {e}")
            return False
    
    def get_database_statistics(self) -> Dict:
        """
        获取数据库统计信息
        
        Returns:
            数据库统计信息
        """
        shard_stats = self.shard_manager.get_shard_statistics()
        
        return {
            "metadata": self.metadata,
            "shard_statistics": shard_stats,
            "size_distribution": self.shard_manager.get_shard_size_distribution()
        }
    
    def save_database(self):
        """
        保存数据库到磁盘
        """
        # 保存分片数据
        self.shard_manager.save_shards()
        
        # 保存元数据
        self._save_metadata()
        
        print("数据库已保存")
    
    def _load_metadata(self) -> Dict:
        """
        加载数据库元数据
        
        Returns:
            元数据字典
        """
        metadata_file = os.path.join(self.storage_path, "metadata.json")
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载元数据失败: {e}")
        
        # 返回默认元数据
        return {
            "version": "1.0",
            "created_time": time.time(),
            "total_credentials": 0,
            "breaches": []
        }
    
    def _save_metadata(self):
        """
        保存数据库元数据
        """
        metadata_file = os.path.join(self.storage_path, "metadata.json")
        
        self.metadata["last_updated"] = time.time()
        
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def clear_database(self):
        """
        清空整个数据库
        """
        self.shard_manager.clear_all_shards()
        
        # 删除元数据文件
        metadata_file = os.path.join(self.storage_path, "metadata.json")
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
        
        # 重新初始化元数据
        self.metadata = self._load_metadata()
        
        print("数据库已清空")
    
    def export_statistics(self, output_file: str):
        """
        导出数据库统计信息
        
        Args:
            output_file: 输出文件路径
        """
        stats = self.get_database_statistics()
        
        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"统计信息已导出到: {output_file}")
    
    def import_common_passwords(self, password_file: str, username_prefix: str = "user"):
        """
        导入常见密码列表
        
        Args:
            password_file: 密码文件路径
            username_prefix: 用户名前缀
        """
        passwords = []
        
        try:
            with open(password_file, 'r', encoding='utf-8') as f:
                for line in f:
                    password = line.strip()
                    if password:
                        passwords.append(password)
        except Exception as e:
            print(f"读取密码文件失败: {e}")
            return
        
        # 创建凭证列表
        credentials = []
        for i, password in enumerate(passwords):
            username = f"{username_prefix}{i}"
            credentials.append((username, password))
        
        # 添加到数据库
        self.add_breach_data(credentials, f"常见密码列表 ({password_file})")
    
    def simulate_breach_data(self, count: int = 1000):
        """
        生成模拟泄露数据用于测试
        
        Args:
            count: 生成的凭证数量
        """
        import random
        import string
        
        credentials = []
        
        # 生成随机凭证
        for i in range(count):
            username = f"user{i}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            credentials.append((username, password))
        
        # 添加一些常见的弱密码
        weak_passwords = [
            "password", "123456", "password123", "admin", "qwerty",
            "letmein", "welcome", "monkey", "dragon", "master"
        ]
        
        for i, password in enumerate(weak_passwords):
            username = f"weak_user{i}"
            credentials.append((username, password))
        
        self.add_breach_data(credentials, f"模拟泄露数据 ({count} 条记录)") 