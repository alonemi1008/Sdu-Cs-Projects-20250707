import argon2
import os
from typing import Union
from ..utils.constants import (
    ARGON2_MEMORY_COST, ARGON2_TIME_COST, 
    ARGON2_PARALLELISM, ARGON2_HASH_LENGTH
)


class Argon2Hasher:
    """
    Argon2哈希器，用于安全哈希凭证
    """
    
    def __init__(self):
        """初始化Argon2哈希器"""
        self.hasher = argon2.PasswordHasher(
            memory_cost=ARGON2_MEMORY_COST,
            time_cost=ARGON2_TIME_COST,
            parallelism=ARGON2_PARALLELISM,
            hash_len=ARGON2_HASH_LENGTH,
            salt_len=16
        )
    
    def hash_credential(self, username: str, password: str, salt: bytes = None) -> bytes:
        """
        对凭证进行Argon2哈希
        
        Args:
            username: 标准化的用户名
            password: 密码
            salt: 可选的盐值，如果不提供则生成随机盐
            
        Returns:
            哈希后的凭证（16字节）
        """
        # 组合用户名和密码
        credential = f"{username}:{password}"
        
        if salt is None:
            salt = os.urandom(16)
        
        # 使用Argon2进行哈希
        try:
            # 使用低级API直接获取哈希值
            hash_result = argon2.low_level.hash_secret_raw(
                secret=credential.encode('utf-8'),
                salt=salt,
                time_cost=ARGON2_TIME_COST,
                memory_cost=ARGON2_MEMORY_COST,
                parallelism=ARGON2_PARALLELISM,
                hash_len=ARGON2_HASH_LENGTH,
                type=argon2.Type.ID
            )
            return hash_result
        except Exception as e:
            raise RuntimeError(f"Argon2哈希失败: {e}")
    
    def hash_credential_with_fixed_salt(self, username: str, password: str) -> bytes:
        """
        使用固定盐对凭证进行哈希（用于一致性哈希）
        
        Args:
            username: 标准化的用户名
            password: 密码
            
        Returns:
            哈希后的凭证（16字节）
        """
        # 使用凭证本身生成确定性盐
        credential = f"{username}:{password}"
        import hashlib
        salt = hashlib.sha256(credential.encode('utf-8')).digest()[:16]
        
        return self.hash_credential(username, password, salt)
    
    def get_shard_prefix(self, credential_hash: bytes) -> bytes:
        """
        获取用于分片的前缀
        
        Args:
            credential_hash: 凭证哈希
            
        Returns:
            前缀字节（2字节）
        """
        from ..utils.constants import SHARD_PREFIX_LENGTH
        return credential_hash[:SHARD_PREFIX_LENGTH]
    
    def get_shard_index(self, credential_hash: bytes) -> int:
        """
        获取分片索引
        
        Args:
            credential_hash: 凭证哈希
            
        Returns:
            分片索引（0-65535）
        """
        prefix = self.get_shard_prefix(credential_hash)
        return int.from_bytes(prefix, byteorder='big') 