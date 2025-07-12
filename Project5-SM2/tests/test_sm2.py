#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SM2功能测试脚本
验证基础版本和优化版本的正确性
"""

import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.sm2_basic import SM2Basic
from src.core.sm2_optimized import SM2Optimized

def test_basic_functionality():
    """测试基础功能"""
    print("Testing basic functionality...")
    
    sm2 = SM2Basic()
    
    # 测试密钥生成
    private_key, public_key = sm2.generate_keypair()
    print(f"Key generation: OK")
    
    # 测试加密解密
    message = b"Hello, SM2 test!"
    ciphertext = sm2.encrypt(message, public_key)
    decrypted = sm2.decrypt(ciphertext, private_key)
    assert message == decrypted, "Encryption/Decryption failed"
    print(f"Encryption/Decryption: OK")
    
    # 测试数字签名
    signature = sm2.sign(message, private_key)
    is_valid = sm2.verify(message, signature, public_key)
    assert is_valid, "Digital signature failed"
    print(f"Digital signature: OK")
    
    # 测试错误签名检测
    wrong_message = b"Wrong message"
    is_valid_wrong = sm2.verify(wrong_message, signature, public_key)
    assert not is_valid_wrong, "Wrong signature detection failed"
    print(f"Wrong signature detection: OK")

def test_optimized_functionality():
    """测试优化功能"""
    print("\nTesting optimized functionality...")
    
    sm2 = SM2Optimized()
    
    # 测试密钥生成
    private_key, public_key = sm2.generate_keypair()
    print(f"Optimized key generation: OK")
    
    # 测试加密解密
    message = b"Hello, SM2 optimized test!"
    ciphertext = sm2.encrypt(message, public_key)
    decrypted = sm2.decrypt(ciphertext, private_key)
    assert message == decrypted, "Optimized encryption/decryption failed"
    print(f"Optimized encryption/decryption: OK")
    
    # 测试数字签名
    signature = sm2.sign(message, private_key)
    is_valid = sm2.verify_optimized(message, signature, public_key)
    assert is_valid, "Optimized digital signature failed"
    print(f"Optimized digital signature: OK")

def test_cross_compatibility():
    """测试基础版本和优化版本的兼容性"""
    print("\nTesting cross-compatibility...")
    
    sm2_basic = SM2Basic()
    sm2_optimized = SM2Optimized()
    
    # 生成密钥对
    private_key, public_key = sm2_basic.generate_keypair()
    
    message = b"Cross-compatibility test"
    
    # 基础版本加密，优化版本解密
    ciphertext_basic = sm2_basic.encrypt(message, public_key)
    decrypted_optimized = sm2_optimized.decrypt(ciphertext_basic, private_key)
    assert message == decrypted_optimized, "Basic->Optimized compatibility failed"
    print(f"Basic encrypt -> Optimized decrypt: OK")
    
    # 优化版本加密，基础版本解密
    ciphertext_optimized = sm2_optimized.encrypt(message, public_key)
    decrypted_basic = sm2_basic.decrypt(ciphertext_optimized, private_key)
    assert message == decrypted_basic, "Optimized->Basic compatibility failed"
    print(f"Optimized encrypt -> Basic decrypt: OK")
    
    # 基础版本签名，优化版本验证
    signature_basic = sm2_basic.sign(message, private_key)
    is_valid_optimized = sm2_optimized.verify(message, signature_basic, public_key)
    assert is_valid_optimized, "Basic sign -> Optimized verify failed"
    print(f"Basic sign -> Optimized verify: OK")
    
    # 优化版本签名，基础版本验证
    signature_optimized = sm2_optimized.sign(message, private_key)
    is_valid_basic = sm2_basic.verify(message, signature_optimized, public_key)
    assert is_valid_basic, "Optimized sign -> Basic verify failed"
    print(f"Optimized sign -> Basic verify: OK")

def test_algorithm_consistency():
    """测试不同算法的一致性"""
    print("\nTesting algorithm consistency...")
    
    sm2 = SM2Optimized()
    
    # 生成测试数据
    import random
    test_scalar = random.randint(1, sm2.n - 1)
    test_point = sm2.G
    
    # 测试不同点乘法算法
    result_basic = sm2.point_multiply_basic(test_scalar, test_point)
    result_naf = sm2.point_multiply_naf(test_scalar, test_point)
    result_window = sm2.point_multiply_sliding_window(test_scalar, test_point)
    result_montgomery = sm2.point_multiply_montgomery(test_scalar, test_point)
    
    # 验证结果一致
    assert result_basic == result_naf, "Basic vs NAF algorithm mismatch"
    assert result_basic == result_window, "Basic vs Window algorithm mismatch"
    assert result_basic == result_montgomery, "Basic vs Montgomery algorithm mismatch"
    print(f"Point multiplication algorithms consistency: OK")

def performance_quick_test():
    """快速性能测试"""
    print("\nQuick performance test...")
    
    sm2_basic = SM2Basic()
    sm2_optimized = SM2Optimized()
    
    message = b"Performance test message"
    
    # 测试密钥生成
    start_time = time.time()
    for _ in range(5):
        private_key, public_key = sm2_basic.generate_keypair()
    basic_keygen_time = time.time() - start_time
    
    start_time = time.time()
    for _ in range(5):
        private_key, public_key = sm2_optimized.generate_keypair()
    optimized_keygen_time = time.time() - start_time
    
    print(f"Key generation - Basic: {basic_keygen_time:.4f}s, Optimized: {optimized_keygen_time:.4f}s")
    
    # 测试加密
    private_key, public_key = sm2_basic.generate_keypair()
    
    start_time = time.time()
    for _ in range(5):
        ciphertext = sm2_basic.encrypt(message, public_key)
    basic_encrypt_time = time.time() - start_time
    
    start_time = time.time()
    for _ in range(5):
        ciphertext = sm2_optimized.encrypt(message, public_key)
    optimized_encrypt_time = time.time() - start_time
    
    print(f"Encryption - Basic: {basic_encrypt_time:.4f}s, Optimized: {optimized_encrypt_time:.4f}s")
    
    # 测试签名
    start_time = time.time()
    for _ in range(5):
        signature = sm2_basic.sign(message, private_key)
    basic_sign_time = time.time() - start_time
    
    start_time = time.time()
    for _ in range(5):
        signature = sm2_optimized.sign(message, private_key)
    optimized_sign_time = time.time() - start_time
    
    print(f"Signing - Basic: {basic_sign_time:.4f}s, Optimized: {optimized_sign_time:.4f}s")

def main():
    """主测试函数"""
    print("SM2 Implementation Test Suite")
    print("=" * 40)
    
    try:
        test_basic_functionality()
        test_optimized_functionality()
        test_cross_compatibility()
        test_algorithm_consistency()
        performance_quick_test()
        
        print("\n" + "=" * 40)
        print("All tests passed successfully!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 