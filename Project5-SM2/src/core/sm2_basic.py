#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SM2椭圆曲线密码算法基础实现
实现SM2的基本功能：密钥生成、加密解密、数字签名
"""

import hashlib
import random
import os
from typing import Tuple, Optional

class SM2Point:
    """椭圆曲线上的点"""
    def __init__(self, x: int, y: int, is_infinity: bool = False):
        self.x = x
        self.y = y
        self.is_infinity = is_infinity
    
    def __eq__(self, other):
        if isinstance(other, SM2Point):
            return (self.x == other.x and self.y == other.y and 
                   self.is_infinity == other.is_infinity)
        return False
    
    def __hash__(self):
        return hash((self.x, self.y, self.is_infinity))
    
    def __str__(self):
        if self.is_infinity:
            return "Point(Infinity)"
        return f"Point({hex(self.x)}, {hex(self.y)})"

class SM2Basic:
    """SM2椭圆曲线密码算法基础实现"""
    
    def __init__(self):
        # SM2推荐参数
        self.p = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
        self.a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
        self.b = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
        self.n = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
        self.Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
        self.Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
        
        # 基点G
        self.G = SM2Point(self.Gx, self.Gy)
        
        # 预计算的逆元表（用于优化）
        self._inv_cache = {}
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """计算模逆元 a^(-1) mod m"""
        if a in self._inv_cache:
            return self._inv_cache[a]
        
        # 使用扩展欧几里得算法
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, _ = extended_gcd(a % m, m)
        if gcd != 1:
            raise ValueError("Modular inverse does not exist")
        
        result = (x % m + m) % m
        self._inv_cache[a] = result
        return result
    
    def point_add(self, P: SM2Point, Q: SM2Point) -> SM2Point:
        """椭圆曲线点加法"""
        if P.is_infinity:
            return Q
        if Q.is_infinity:
            return P
        
        # 如果是相同的点，使用点倍乘
        if P.x == Q.x:
            if P.y == Q.y:
                return self.point_double(P)
            else:
                return SM2Point(0, 0, True)  # 无穷远点
        
        # 不同点的加法
        lambda_val = ((Q.y - P.y) * self._mod_inverse(Q.x - P.x, self.p)) % self.p
        x3 = (lambda_val * lambda_val - P.x - Q.x) % self.p
        y3 = (lambda_val * (P.x - x3) - P.y) % self.p
        
        return SM2Point(x3, y3)
    
    def point_double(self, P: SM2Point) -> SM2Point:
        """椭圆曲线点倍乘"""
        if P.is_infinity:
            return P
        
        # 计算切线斜率
        numerator = (3 * P.x * P.x + self.a) % self.p
        denominator = (2 * P.y) % self.p
        lambda_val = (numerator * self._mod_inverse(denominator, self.p)) % self.p
        
        x3 = (lambda_val * lambda_val - 2 * P.x) % self.p
        y3 = (lambda_val * (P.x - x3) - P.y) % self.p
        
        return SM2Point(x3, y3)
    
    def point_multiply(self, k: int, P: SM2Point) -> SM2Point:
        """椭圆曲线点标量乘法 k*P (基础版本，使用二进制方法)"""
        if k == 0:
            return SM2Point(0, 0, True)
        if k == 1:
            return P
        
        result = SM2Point(0, 0, True)  # 无穷远点
        addend = P
        
        while k:
            if k & 1:
                result = self.point_add(result, addend)
            addend = self.point_double(addend)
            k >>= 1
        
        return result
    
    def generate_keypair(self) -> Tuple[int, SM2Point]:
        """生成SM2密钥对"""
        # 生成私钥 (1 < d < n-1)
        d = random.randint(1, self.n - 1)
        
        # 计算公钥 P = d*G
        P = self.point_multiply(d, self.G)
        
        return d, P
    
    def _kdf(self, z: bytes, klen: int) -> bytes:
        """密钥派生函数KDF"""
        ct = 1
        rcnt = (klen + 31) // 32  # 向上取整
        zin = bytearray(z)
        ha = bytearray()
        
        for i in range(rcnt):
            msg = zin + ct.to_bytes(4, 'big')
            ha.extend(hashlib.sha256(msg).digest())
            ct += 1
        
        return bytes(ha[:klen])
    
    def encrypt(self, message: bytes, public_key: SM2Point) -> bytes:
        """SM2加密"""
        while True:
            # 生成随机数k
            k = random.randint(1, self.n - 1)
            
            # 计算椭圆曲线点C1 = k*G
            C1 = self.point_multiply(k, self.G)
            
            # 计算椭圆曲线点 kPb = k*Pb
            kPb = self.point_multiply(k, public_key)
            
            # 计算t = KDF(x2||y2, klen)
            x2_bytes = kPb.x.to_bytes(32, 'big')
            y2_bytes = kPb.y.to_bytes(32, 'big')
            t = self._kdf(x2_bytes + y2_bytes, len(message))
            
            # 如果t为全0，重新选择k
            if all(b == 0 for b in t):
                continue
            
            # 计算C2 = M ⊕ t
            C2 = bytes(m ^ t_byte for m, t_byte in zip(message, t))
            
            # 计算C3 = Hash(x2||M||y2)
            hash_input = x2_bytes + message + y2_bytes
            C3 = hashlib.sha256(hash_input).digest()
            
            # 返回密文C = C1||C2||C3
            C1_bytes = b'\x04' + C1.x.to_bytes(32, 'big') + C1.y.to_bytes(32, 'big')
            return C1_bytes + C2 + C3
    
    def decrypt(self, ciphertext: bytes, private_key: int) -> bytes:
        """SM2解密"""
        # 解析密文
        if len(ciphertext) < 97:  # 最小长度检查
            raise ValueError("Invalid ciphertext length")
        
        # 解析C1
        if ciphertext[0] != 0x04:
            raise ValueError("Invalid C1 format")
        
        C1_x = int.from_bytes(ciphertext[1:33], 'big')
        C1_y = int.from_bytes(ciphertext[33:65], 'big')
        C1 = SM2Point(C1_x, C1_y)
        
        # 解析C2和C3
        C2 = ciphertext[65:-32]
        C3 = ciphertext[-32:]
        
        # 计算椭圆曲线点 dC1 = d*C1
        dC1 = self.point_multiply(private_key, C1)
        
        # 计算t = KDF(x2||y2, klen)
        x2_bytes = dC1.x.to_bytes(32, 'big')
        y2_bytes = dC1.y.to_bytes(32, 'big')
        t = self._kdf(x2_bytes + y2_bytes, len(C2))
        
        # 计算明文M = C2 ⊕ t
        M = bytes(c ^ t_byte for c, t_byte in zip(C2, t))
        
        # 验证C3
        hash_input = x2_bytes + M + y2_bytes
        expected_C3 = hashlib.sha256(hash_input).digest()
        
        if C3 != expected_C3:
            raise ValueError("Decryption failed: hash verification failed")
        
        return M
    
    def sign(self, message: bytes, private_key: int) -> Tuple[int, int]:
        """SM2数字签名"""
        # 计算消息摘要
        e = int.from_bytes(hashlib.sha256(message).digest(), 'big')
        
        while True:
            # 生成随机数k
            k = random.randint(1, self.n - 1)
            
            # 计算椭圆曲线点 (x1, y1) = k*G
            point = self.point_multiply(k, self.G)
            x1 = point.x
            
            # 计算r = (e + x1) mod n
            r = (e + x1) % self.n
            if r == 0 or (r + k) % self.n == 0:
                continue
            
            # 计算s = (1 + d)^(-1) * (k - r*d) mod n
            d_inv = self._mod_inverse(1 + private_key, self.n)
            s = (d_inv * (k - r * private_key)) % self.n
            if s == 0:
                continue
            
            return r, s
    
    def verify(self, message: bytes, signature: Tuple[int, int], public_key: SM2Point) -> bool:
        """SM2签名验证"""
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
        
        # 计算椭圆曲线点 (x1, y1) = s*G + t*Pa
        point1 = self.point_multiply(s, self.G)
        point2 = self.point_multiply(t, public_key)
        point = self.point_add(point1, point2)
        
        # 计算R = (e + x1) mod n
        R = (e + point.x) % self.n
        
        return R == r

def main():
    """主函数演示SM2基础功能"""
    print("SM2 Basic Implementation Demo")
    print("=" * 40)
    
    # 创建SM2实例
    sm2 = SM2Basic()
    
    # 生成密钥对
    print("Generating keypair...")
    private_key, public_key = sm2.generate_keypair()
    print(f"Private key: {hex(private_key)}")
    print(f"Public key: {public_key}")
    print()
    
    # 加密解密测试
    print("Testing encryption/decryption...")
    message = b"Hello, SM2 encryption!"
    print(f"Original message: {message}")
    
    # 加密
    ciphertext = sm2.encrypt(message, public_key)
    print(f"Ciphertext length: {len(ciphertext)} bytes")
    print(f"Ciphertext (hex): {ciphertext.hex()}")
    
    # 解密
    decrypted = sm2.decrypt(ciphertext, private_key)
    print(f"Decrypted message: {decrypted}")
    print(f"Decryption successful: {message == decrypted}")
    print()
    
    # 数字签名测试
    print("Testing digital signature...")
    sign_message = b"Hello, SM2 signature!"
    print(f"Message to sign: {sign_message}")
    
    # 签名
    signature = sm2.sign(sign_message, private_key)
    print(f"Signature: r={hex(signature[0])}, s={hex(signature[1])}")
    
    # 验证
    is_valid = sm2.verify(sign_message, signature, public_key)
    print(f"Signature verification: {is_valid}")
    
    # 测试错误消息的验证
    wrong_message = b"Wrong message"
    is_valid_wrong = sm2.verify(wrong_message, signature, public_key)
    print(f"Wrong message verification: {is_valid_wrong}")

if __name__ == "__main__":
    main() 