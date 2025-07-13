#!/usr/bin/env python3
"""
加密功能测试
"""

import sys
import os
import unittest

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.crypto.argon2_hash import Argon2Hasher
from src.crypto.elliptic_curve import EllipticCurveBlinder
from src.crypto.psi_protocol import PSIProtocol
from src.utils.canonicalize import canonicalize_username, validate_credentials


class TestArgon2Hasher(unittest.TestCase):
    """
    测试Argon2哈希器
    """
    
    def setUp(self):
        self.hasher = Argon2Hasher()
    
    def test_hash_credential(self):
        """测试凭证哈希"""
        username = "testuser"
        password = "testpass"
        
        # 测试固定盐哈希
        hash1 = self.hasher.hash_credential_with_fixed_salt(username, password)
        hash2 = self.hasher.hash_credential_with_fixed_salt(username, password)
        
        # 相同输入应该产生相同哈希
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 16)  # 16字节哈希
    
    def test_shard_prefix(self):
        """测试分片前缀"""
        username = "testuser"
        password = "testpass"
        
        hash_val = self.hasher.hash_credential_with_fixed_salt(username, password)
        prefix = self.hasher.get_shard_prefix(hash_val)
        index = self.hasher.get_shard_index(hash_val)
        
        self.assertEqual(len(prefix), 2)  # 2字节前缀
        self.assertTrue(0 <= index < 65536)  # 有效分片索引


class TestEllipticCurveBlinder(unittest.TestCase):
    """
    测试椭圆曲线盲化器
    """
    
    def setUp(self):
        self.blinder = EllipticCurveBlinder()
    
    def test_hash_to_curve(self):
        """测试哈希到曲线映射"""
        data = b"test data"
        point = self.blinder.hash_to_curve(data)
        
        # 应该返回有效的椭圆曲线点
        self.assertIsNotNone(point)
    
    def test_point_serialization(self):
        """测试点序列化"""
        data = b"test data"
        point = self.blinder.hash_to_curve(data)
        
        # 序列化和反序列化
        point_bytes = self.blinder.point_to_bytes(point)
        recovered_point = self.blinder.bytes_to_point(point_bytes)
        
        # 验证序列化正确性
        self.assertEqual(
            self.blinder.point_to_bytes(point),
            self.blinder.point_to_bytes(recovered_point)
        )
    
    def test_blinding_unblinding(self):
        """测试盲化和解盲化"""
        data = b"test data"
        point = self.blinder.hash_to_curve(data)
        blinding_factor = self.blinder.generate_random_key()
        
        # 盲化
        blinded_point = self.blinder.blind_point(point, blinding_factor)
        
        # 解盲化
        unblinded_point = self.blinder.unblind_point(blinded_point, blinding_factor)
        
        # 验证解盲化结果
        self.assertEqual(
            self.blinder.point_to_bytes(point),
            self.blinder.point_to_bytes(unblinded_point)
        )


class TestPSIProtocol(unittest.TestCase):
    """
    测试PSI协议
    """
    
    def setUp(self):
        self.psi = PSIProtocol()
    
    def test_client_prepare_query(self):
        """测试客户端查询准备"""
        username = "testuser"
        password = "testpass"
        
        blinded_hash, shard_prefix, client_key = self.psi.client_prepare_query(
            username, password
        )
        
        self.assertIsNotNone(blinded_hash)
        self.assertEqual(len(shard_prefix), 2)
        self.assertEqual(len(client_key), 28)
    
    def test_database_entry_creation(self):
        """测试数据库条目创建"""
        username = "testuser"
        password = "testpass"
        
        credential_hash, shard_prefix = self.psi.create_breach_database_entry(
            username, password
        )
        
        self.assertEqual(len(credential_hash), 16)
        self.assertEqual(len(shard_prefix), 2)
        
        # 测试盲化
        blinded_hash = self.psi.blind_database_entry(credential_hash)
        self.assertIsNotNone(blinded_hash)
    
    def test_full_protocol(self):
        """测试完整协议流程"""
        username = "testuser"
        password = "testpass"
        
        # 创建数据库条目
        credential_hash, shard_prefix = self.psi.create_breach_database_entry(
            username, password
        )
        blinded_db_hash = self.psi.blind_database_entry(credential_hash)
        
        # 客户端准备查询
        blinded_hash, query_prefix, client_key = self.psi.client_prepare_query(
            username, password
        )
        
        # 验证分片前缀匹配
        self.assertEqual(shard_prefix, query_prefix)
        
        # 模拟分片数据
        shard_data = [credential_hash]
        
        # 服务器处理查询
        double_blinded_hash, blinded_shard_data = self.psi.server_process_query(
            blinded_hash, query_prefix, shard_data
        )
        
        # 客户端处理响应
        is_match = self.psi.client_process_response(
            double_blinded_hash, blinded_shard_data, client_key
        )
        
        # 应该找到匹配
        self.assertTrue(is_match)


class TestUtilities(unittest.TestCase):
    """
    测试工具函数
    """
    
    def test_canonicalize_username(self):
        """测试用户名标准化"""
        # 测试邮箱格式
        self.assertEqual(canonicalize_username("user@gmail.com"), "user")
        self.assertEqual(canonicalize_username("User@Gmail.Com"), "user")
        
        # 测试普通用户名
        self.assertEqual(canonicalize_username("TestUser"), "testuser")
        self.assertEqual(canonicalize_username("test_user"), "test_user")
    
    def test_validate_credentials(self):
        """测试凭证验证"""
        # 有效凭证
        self.assertTrue(validate_credentials("user", "password"))
        self.assertTrue(validate_credentials("user@gmail.com", "123456"))
        
        # 无效凭证
        self.assertFalse(validate_credentials("", "password"))
        self.assertFalse(validate_credentials("user", ""))
        self.assertFalse(validate_credentials("", ""))


if __name__ == "__main__":
    unittest.main() 