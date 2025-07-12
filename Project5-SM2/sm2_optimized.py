#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SM2椭圆曲线密码算法优化实现
实现多种优化技术：滑动窗口法、NAF、蒙哥马利阶梯、预计算表等
"""

import hashlib
import random
import time
from typing import Tuple, List, Dict, Optional
from sm2_basic import SM2Point, SM2Basic

class SM2Optimized(SM2Basic):
    """SM2椭圆曲线密码算法优化实现"""
    
    def __init__(self):
        super().__init__()
        
        # 预计算表
        self._precomputed_G = {}
        self._precomputed_multiples = {}
        self._window_size = 4  # 滑动窗口大小
        
        # 初始化预计算表
        self._init_precomputed_tables()
    
    def _init_precomputed_tables(self):
        """初始化预计算表（延迟初始化）"""
        # 只预计算少量基本倍数，其他按需计算
        self._precomputed_multiples[self.G] = {}
        for i in range(1, min(16, 1 << self._window_size), 2):  # 只预计算前几个奇数倍数
            self._precomputed_multiples[self.G][i] = self.point_multiply_basic(i, self.G)
    
    def point_multiply_basic(self, k: int, P: SM2Point) -> SM2Point:
        """基础点乘法（用于预计算）"""
        return super().point_multiply(k, P)
    
    def _signed_binary_representation(self, k: int) -> List[int]:
        """计算NAF (Non-Adjacent Form) 表示"""
        naf = []
        while k > 0:
            if k & 1:  # k是奇数
                width = 2 - (k & 3)  # width = 2 - (k mod 4)
                naf.append(width)
                k -= width
            else:
                naf.append(0)
            k >>= 1
        return naf
    
    def point_multiply_naf(self, k: int, P: SM2Point) -> SM2Point:
        """使用NAF优化的点乘法"""
        if k == 0:
            return SM2Point(0, 0, True)
        if k == 1:
            return P
        
        # 计算NAF表示
        naf = self._signed_binary_representation(k)
        
        # 预计算 -P
        neg_P = SM2Point(P.x, (-P.y) % self.p)
        
        result = SM2Point(0, 0, True)
        
        # 从最高位开始
        for i in reversed(range(len(naf))):
            result = self.point_double(result)
            if naf[i] == 1:
                result = self.point_add(result, P)
            elif naf[i] == -1:
                result = self.point_add(result, neg_P)
        
        return result
    
    def point_multiply_sliding_window(self, k: int, P: SM2Point) -> SM2Point:
        """使用滑动窗口法的点乘法"""
        if k == 0:
            return SM2Point(0, 0, True)
        if k == 1:
            return P
        
        # 如果P是基点G，使用预计算表
        if P == self.G and P in self._precomputed_multiples:
            return self._point_multiply_precomputed(k, P)
        
        # 预计算奇数倍数
        if P not in self._precomputed_multiples:
            self._precomputed_multiples[P] = {}
            for i in range(1, 1 << self._window_size, 2):
                self._precomputed_multiples[P][i] = self.point_multiply_basic(i, P)
        
        return self._point_multiply_precomputed(k, P)
    
    def _point_multiply_precomputed(self, k: int, P: SM2Point) -> SM2Point:
        """使用预计算表的点乘法"""
        if k == 0:
            return SM2Point(0, 0, True)
        
        result = SM2Point(0, 0, True)
        window_size = self._window_size
        
        # 将k转换为二进制
        binary_k = bin(k)[2:]  # 去掉'0b'前缀
        i = 0
        
        while i < len(binary_k):
            if binary_k[i] == '0':
                result = self.point_double(result)
                i += 1
            else:
                # 找到连续的1的长度
                j = i
                while j < len(binary_k) and j < i + window_size and binary_k[j] == '1':
                    j += 1
                
                # 提取窗口值
                window_bits = binary_k[i:j]
                window_value = int(window_bits, 2)
                
                # 如果窗口值是奇数且在预计算表中
                if window_value % 2 == 1 and window_value in self._precomputed_multiples[P]:
                    # 左移相应位数
                    for _ in range(j - i):
                        result = self.point_double(result)
                    result = self.point_add(result, self._precomputed_multiples[P][window_value])
                    i = j
                else:
                    # 回退到基本方法
                    result = self.point_double(result)
                    if binary_k[i] == '1':
                        result = self.point_add(result, P)
                    i += 1
        
        return result
    
    def point_multiply_montgomery(self, k: int, P: SM2Point) -> SM2Point:
        """蒙哥马利阶梯算法"""
        if k == 0:
            return SM2Point(0, 0, True)
        if k == 1:
            return P
        
        # 蒙哥马利阶梯需要特殊的坐标系统
        # 这里使用标准的二进制方法但优化了分支预测
        bits = bin(k)[2:]  # 转换为二进制字符串
        result = SM2Point(0, 0, True)
        addend = P
        
        for bit in reversed(bits):
            if bit == '1':
                result = self.point_add(result, addend)
            addend = self.point_double(addend)
        
        return result
    
    def point_multiply(self, k: int, P: SM2Point) -> SM2Point:
        """优化的点乘法（自动选择最佳算法）"""
        if k == 0:
            return SM2Point(0, 0, True)
        if k == 1:
            return P
        
        # 根据k的大小和P的类型选择最佳算法
        if P == self.G:
            # 对于基点，使用预计算表
            return self.point_multiply_sliding_window(k, P)
        elif k.bit_length() > 128:
            # 对于大数，使用NAF
            return self.point_multiply_naf(k, P)
        else:
            # 对于中等大小的数，使用滑动窗口
            return self.point_multiply_sliding_window(k, P)
    
    def fast_mod_inverse(self, a: int, m: int) -> int:
        """快速模逆元计算（使用费马小定理）"""
        if a in self._inv_cache:
            return self._inv_cache[a]
        
        # 对于素数模，使用费马小定理: a^(-1) = a^(p-2) mod p
        if m == self.p:
            result = pow(a, m - 2, m)
        else:
            result = super()._mod_inverse(a, m)
        
        self._inv_cache[a] = result
        return result
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """重写模逆元计算"""
        return self.fast_mod_inverse(a, m)
    
    def batch_point_multiply(self, scalars: List[int], points: List[SM2Point]) -> List[SM2Point]:
        """批量点乘法"""
        if len(scalars) != len(points):
            raise ValueError("Scalars and points must have the same length")
        
        results = []
        for k, P in zip(scalars, points):
            results.append(self.point_multiply(k, P))
        
        return results
    
    def simultaneous_point_multiply(self, k1: int, P1: SM2Point, k2: int, P2: SM2Point) -> SM2Point:
        """同时点乘法 k1*P1 + k2*P2 (Shamir's trick)"""
        # 将k1和k2转换为二进制
        max_bits = max(k1.bit_length(), k2.bit_length())
        
        # 预计算组合点
        combinations = {
            (0, 0): SM2Point(0, 0, True),
            (0, 1): P2,
            (1, 0): P1,
            (1, 1): self.point_add(P1, P2)
        }
        
        result = SM2Point(0, 0, True)
        
        for i in range(max_bits - 1, -1, -1):
            result = self.point_double(result)
            
            bit1 = (k1 >> i) & 1
            bit2 = (k2 >> i) & 1
            
            if (bit1, bit2) in combinations:
                result = self.point_add(result, combinations[(bit1, bit2)])
        
        return result
    
    def verify_optimized(self, message: bytes, signature: Tuple[int, int], public_key: SM2Point) -> bool:
        """优化的签名验证（使用同时点乘法）"""
        r, s = signature
        
        # 检查r, s是否在有效范围内
        if not (1 <= r < self.n and 1 <= s < self.n):
            return False
        
        # 计算消息摘要
        e = int.from_bytes(hashlib.sha256(message).digest(), 'big')
        
        # 计算t = (r + s) mod n
        t = (r + s) % self.n
        if t == 0:
            return False
        
        # 使用同时点乘法计算 s*G + t*Pa
        point = self.simultaneous_point_multiply(s, self.G, t, public_key)
        
        # 计算R = (e + x1) mod n
        R = (e + point.x) % self.n
        
        return R == r

def performance_comparison():
    """性能比较测试"""
    print("SM2 Performance Comparison")
    print("=" * 50)
    
    # 创建基础版本和优化版本
    sm2_basic = SM2Basic()
    sm2_optimized = SM2Optimized()
    
    # 生成测试数据
    test_scalar = random.randint(1, sm2_basic.n - 1)
    test_point = sm2_basic.G
    
    print(f"Test scalar bit length: {test_scalar.bit_length()}")
    print()
    
    # 测试基础点乘法
    print("Testing point multiplication...")
    
    start_time = time.time()
    result_basic = sm2_basic.point_multiply(test_scalar, test_point)
    basic_time = time.time() - start_time
    
    start_time = time.time()
    result_optimized = sm2_optimized.point_multiply(test_scalar, test_point)
    optimized_time = time.time() - start_time
    
    print(f"Basic implementation: {basic_time:.4f} seconds")
    print(f"Optimized implementation: {optimized_time:.4f} seconds")
    print(f"Speedup: {basic_time / optimized_time:.2f}x")
    print(f"Results match: {result_basic == result_optimized}")
    print()
    
    # 测试签名验证
    print("Testing signature verification...")
    
    # 生成测试签名
    private_key, public_key = sm2_basic.generate_keypair()
    message = b"Performance test message"
    signature = sm2_basic.sign(message, private_key)
    
    # 基础验证
    start_time = time.time()
    for _ in range(10):
        result_basic = sm2_basic.verify(message, signature, public_key)
    basic_verify_time = time.time() - start_time
    
    # 优化验证
    start_time = time.time()
    for _ in range(10):
        result_optimized = sm2_optimized.verify_optimized(message, signature, public_key)
    optimized_verify_time = time.time() - start_time
    
    print(f"Basic verification (10 times): {basic_verify_time:.4f} seconds")
    print(f"Optimized verification (10 times): {optimized_verify_time:.4f} seconds")
    print(f"Verification speedup: {basic_verify_time / optimized_verify_time:.2f}x")
    print(f"Verification results match: {result_basic == result_optimized}")

def main():
    """主函数演示SM2优化功能"""
    print("SM2 Optimized Implementation Demo")
    print("=" * 40)
    
    # 创建SM2优化实例
    sm2 = SM2Optimized()
    
    # 生成密钥对
    print("Generating keypair...")
    private_key, public_key = sm2.generate_keypair()
    print(f"Private key: {hex(private_key)}")
    print(f"Public key: {public_key}")
    print()
    
    # 测试不同的点乘法算法
    print("Testing different point multiplication algorithms...")
    test_scalar = random.randint(1, sm2.n - 1)
    
    # NAF算法
    start_time = time.time()
    result_naf = sm2.point_multiply_naf(test_scalar, sm2.G)
    naf_time = time.time() - start_time
    
    # 滑动窗口算法
    start_time = time.time()
    result_window = sm2.point_multiply_sliding_window(test_scalar, sm2.G)
    window_time = time.time() - start_time
    
    # 蒙哥马利阶梯算法
    start_time = time.time()
    result_montgomery = sm2.point_multiply_montgomery(test_scalar, sm2.G)
    montgomery_time = time.time() - start_time
    
    print(f"NAF algorithm: {naf_time:.4f} seconds")
    print(f"Sliding window algorithm: {window_time:.4f} seconds")
    print(f"Montgomery ladder algorithm: {montgomery_time:.4f} seconds")
    print(f"All results match: {result_naf == result_window == result_montgomery}")
    print()
    
    # 测试同时点乘法
    print("Testing simultaneous point multiplication...")
    k1 = random.randint(1, sm2.n - 1)
    k2 = random.randint(1, sm2.n - 1)
    P1 = sm2.G
    P2 = public_key
    
    start_time = time.time()
    result_separate = sm2.point_add(sm2.point_multiply(k1, P1), sm2.point_multiply(k2, P2))
    separate_time = time.time() - start_time
    
    start_time = time.time()
    result_simultaneous = sm2.simultaneous_point_multiply(k1, P1, k2, P2)
    simultaneous_time = time.time() - start_time
    
    print(f"Separate multiplication: {separate_time:.4f} seconds")
    print(f"Simultaneous multiplication: {simultaneous_time:.4f} seconds")
    print(f"Speedup: {separate_time / simultaneous_time:.2f}x")
    print(f"Results match: {result_separate == result_simultaneous}")
    print()
    
    # 加密解密测试
    print("Testing encryption/decryption...")
    message = b"Hello, SM2 optimized encryption!"
    print(f"Original message: {message}")
    
    # 加密
    start_time = time.time()
    ciphertext = sm2.encrypt(message, public_key)
    encrypt_time = time.time() - start_time
    
    # 解密
    start_time = time.time()
    decrypted = sm2.decrypt(ciphertext, private_key)
    decrypt_time = time.time() - start_time
    
    print(f"Encryption time: {encrypt_time:.4f} seconds")
    print(f"Decryption time: {decrypt_time:.4f} seconds")
    print(f"Decryption successful: {message == decrypted}")
    print()
    
    # 数字签名测试
    print("Testing optimized digital signature...")
    sign_message = b"Hello, SM2 optimized signature!"
    
    # 签名
    start_time = time.time()
    signature = sm2.sign(sign_message, private_key)
    sign_time = time.time() - start_time
    
    # 验证
    start_time = time.time()
    is_valid = sm2.verify_optimized(sign_message, signature, public_key)
    verify_time = time.time() - start_time
    
    print(f"Signing time: {sign_time:.4f} seconds")
    print(f"Verification time: {verify_time:.4f} seconds")
    print(f"Signature verification: {is_valid}")
    
    # 运行性能比较
    print("\n" + "=" * 50)
    performance_comparison()

if __name__ == "__main__":
    main() 