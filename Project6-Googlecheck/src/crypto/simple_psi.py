"""
简化的私有集合交集协议实现
用于演示Google Password Checkup协议
"""

from .simple_ec import SimpleEllipticCurveBlinder
from .argon2_hash import Argon2Hasher
from ..utils.canonicalize import canonicalize_username


class SimplePSIProtocol:
    """
    简化的私有集合交集协议
    """
    
    def __init__(self, server_private_key=None):
        """
        初始化PSI协议
        
        Args:
            server_private_key: 服务器私钥
        """
        self.hasher = Argon2Hasher()
        self.blinder = SimpleEllipticCurveBlinder(server_private_key)
    
    def client_prepare_query(self, username, password):
        """
        客户端准备查询请求
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            (盲化哈希, 分片前缀, 客户端盲化密钥)
        """
        # 标准化用户名
        canonical_username = canonicalize_username(username)
        
        # 使用Argon2哈希凭证
        credential_hash = self.hasher.hash_credential_with_fixed_salt(
            canonical_username, password
        )
        
        # 获取分片前缀
        shard_prefix = self.hasher.get_shard_prefix(credential_hash)
        
        # 生成客户端盲化密钥
        client_blinding_key = self.blinder.generate_random_key()
        
        # 创建点表示
        point_representation = self.blinder.hash_to_point_representation(credential_hash)
        
        # 使用客户端密钥盲化
        blinded_hash = self.blinder.blind_hash(point_representation, client_blinding_key)
        
        return blinded_hash, shard_prefix, client_blinding_key
    
    def server_process_query(self, blinded_hash, shard_prefix, shard_data):
        """
        服务器处理查询请求
        
        Args:
            blinded_hash: 客户端盲化的哈希
            shard_prefix: 分片前缀
            shard_data: 对应分片的所有数据
            
        Returns:
            (双重盲化哈希, 盲化的分片数据)
        """
        # 使用服务器私钥进行双重盲化
        server_blinding_key = self.blinder.get_private_key_bytes()
        double_blinded_hash = self.blinder.blind_hash(blinded_hash, server_blinding_key)
        
        # 对分片数据进行服务器盲化
        blinded_shard_data = []
        for credential_hash in shard_data:
            # 创建点表示
            point_representation = self.blinder.hash_to_point_representation(credential_hash)
            
            # 使用服务器私钥盲化
            blinded_item = self.blinder.blind_hash(point_representation, server_blinding_key)
            blinded_shard_data.append(blinded_item)
        
        return double_blinded_hash, blinded_shard_data
    
    def client_process_response(self, double_blinded_hash, blinded_shard_data, client_blinding_key):
        """
        客户端处理服务器响应
        
        Args:
            double_blinded_hash: 双重盲化的查询哈希
            blinded_shard_data: 盲化的分片数据
            client_blinding_key: 客户端盲化密钥
            
        Returns:
            是否在泄露数据库中找到匹配
        """
        # 使用客户端密钥解盲化，得到仅服务器盲化的哈希
        server_blinded_hash = self.blinder.unblind_hash(double_blinded_hash, client_blinding_key)
        
        # 检查是否在分片数据中
        return server_blinded_hash in blinded_shard_data
    
    def create_breach_database_entry(self, username, password):
        """
        创建泄露数据库条目
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            (凭证哈希, 分片前缀)
        """
        # 标准化用户名
        canonical_username = canonicalize_username(username)
        
        # 使用Argon2哈希凭证
        credential_hash = self.hasher.hash_credential_with_fixed_salt(
            canonical_username, password
        )
        
        # 获取分片前缀
        shard_prefix = self.hasher.get_shard_prefix(credential_hash)
        
        return credential_hash, shard_prefix
    
    def blind_database_entry(self, credential_hash):
        """
        对数据库条目进行服务器盲化
        
        Args:
            credential_hash: 凭证哈希
            
        Returns:
            盲化后的哈希
        """
        # 创建点表示
        point_representation = self.blinder.hash_to_point_representation(credential_hash)
        
        # 使用服务器私钥盲化
        server_blinding_key = self.blinder.get_private_key_bytes()
        return self.blinder.blind_hash(point_representation, server_blinding_key) 