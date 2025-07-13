from typing import List, Tuple, Optional
from .elliptic_curve import EllipticCurveBlinder
from .argon2_hash import Argon2Hasher
from ..utils.canonicalize import canonicalize_username
from cryptography.hazmat.primitives.asymmetric import ec


class PSIProtocol:
    """
    私有集合交集协议实现
    遵循Google Password Checkup协议规范
    """
    
    def __init__(self, server_private_key: Optional[bytes] = None):
        """
        初始化PSI协议
        
        Args:
            server_private_key: 服务器私钥，如果不提供则生成随机私钥
        """
        self.hasher = Argon2Hasher()
        self.blinder = EllipticCurveBlinder(server_private_key)
        
    def client_prepare_query(self, username: str, password: str) -> Tuple[bytes, bytes, bytes]:
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
        
        # 将哈希映射到椭圆曲线点
        hash_point = self.blinder.hash_to_curve(credential_hash)
        
        # 生成客户端盲化密钥
        client_blinding_key = self.blinder.generate_random_key()
        
        # 使用客户端密钥盲化点
        blinded_point = self.blinder.blind_point(hash_point, client_blinding_key)
        
        # 将盲化点转换为字节
        blinded_hash = self.blinder.point_to_bytes(blinded_point)
        
        return blinded_hash, shard_prefix, client_blinding_key
    
    def server_process_query(self, blinded_hash: bytes, shard_prefix: bytes, 
                           shard_data: List[bytes]) -> Tuple[bytes, List[bytes]]:
        """
        服务器处理查询请求
        
        Args:
            blinded_hash: 客户端盲化的哈希
            shard_prefix: 分片前缀
            shard_data: 对应分片的所有数据
            
        Returns:
            (双重盲化哈希, 盲化的分片数据)
        """
        # 将盲化哈希转换为椭圆曲线点
        client_blinded_point = self.blinder.bytes_to_point(blinded_hash)
        
        # 使用服务器私钥进行双重盲化
        server_blinding_key = self.blinder.get_private_key_bytes()
        double_blinded_point = self.blinder.blind_point(
            client_blinded_point, server_blinding_key
        )
        
        # 转换为字节
        double_blinded_hash = self.blinder.point_to_bytes(double_blinded_point)
        
        # 对分片数据进行服务器盲化
        blinded_shard_data = []
        for credential_hash in shard_data:
            # 将凭证哈希映射到椭圆曲线点
            hash_point = self.blinder.hash_to_curve(credential_hash)
            
            # 使用服务器私钥盲化
            blinded_point = self.blinder.blind_point(hash_point, server_blinding_key)
            
            # 转换为字节并添加到结果
            blinded_shard_data.append(self.blinder.point_to_bytes(blinded_point))
        
        return double_blinded_hash, blinded_shard_data
    
    def client_process_response(self, double_blinded_hash: bytes, 
                              blinded_shard_data: List[bytes],
                              client_blinding_key: bytes) -> bool:
        """
        客户端处理服务器响应
        
        Args:
            double_blinded_hash: 双重盲化的查询哈希
            blinded_shard_data: 盲化的分片数据
            client_blinding_key: 客户端盲化密钥
            
        Returns:
            是否在泄露数据库中找到匹配
        """
        # 将双重盲化哈希转换为椭圆曲线点
        double_blinded_point = self.blinder.bytes_to_point(double_blinded_hash)
        
        # 使用客户端密钥解盲化，得到仅服务器盲化的哈希
        server_blinded_point = self.blinder.unblind_point(
            double_blinded_point, client_blinding_key
        )
        
        # 转换为字节进行比较
        server_blinded_hash = self.blinder.point_to_bytes(server_blinded_point)
        
        # 检查是否在分片数据中
        return server_blinded_hash in blinded_shard_data
    
    def create_breach_database_entry(self, username: str, password: str) -> Tuple[bytes, bytes]:
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
    
    def blind_database_entry(self, credential_hash: bytes) -> bytes:
        """
        对数据库条目进行服务器盲化
        
        Args:
            credential_hash: 凭证哈希
            
        Returns:
            盲化后的哈希
        """
        # 将哈希映射到椭圆曲线点
        hash_point = self.blinder.hash_to_curve(credential_hash)
        
        # 使用服务器私钥盲化
        server_blinding_key = self.blinder.get_private_key_bytes()
        blinded_point = self.blinder.blind_point(hash_point, server_blinding_key)
        
        # 转换为字节
        return self.blinder.point_to_bytes(blinded_point) 