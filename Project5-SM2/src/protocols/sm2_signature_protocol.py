#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SM2数字签名协议实现
包括完整的签名格式、证书验证、签名链等功能
"""

import hashlib
import time
import json
from typing import Dict, List, Tuple, Optional, Union
from ..core.sm2_basic import SM2Basic, SM2Point

class SM2Certificate:
    """SM2数字证书类"""
    
    def __init__(self, subject: str, issuer: str, public_key: SM2Point, 
                 serial_number: str, not_before: int, not_after: int):
        self.subject = subject  # 证书主体
        self.issuer = issuer    # 证书颁发者
        self.public_key = public_key  # 公钥
        self.serial_number = serial_number  # 序列号
        self.not_before = not_before  # 有效期开始时间
        self.not_after = not_after   # 有效期结束时间
        self.signature = None  # 证书签名
        self.signature_algorithm = "SM2withSM3"  # 签名算法
        
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "subject": self.subject,
            "issuer": self.issuer,
            "public_key": {
                "x": hex(self.public_key.x),
                "y": hex(self.public_key.y)
            },
            "serial_number": self.serial_number,
            "not_before": self.not_before,
            "not_after": self.not_after,
            "signature": {
                "r": hex(self.signature[0]) if self.signature else None,
                "s": hex(self.signature[1]) if self.signature else None
            } if self.signature else None,
            "signature_algorithm": self.signature_algorithm
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SM2Certificate':
        """从字典创建证书对象"""
        public_key = SM2Point(
            int(data["public_key"]["x"], 16),
            int(data["public_key"]["y"], 16)
        )
        
        cert = cls(
            data["subject"],
            data["issuer"],
            public_key,
            data["serial_number"],
            data["not_before"],
            data["not_after"]
        )
        
        if data.get("signature"):
            cert.signature = (
                int(data["signature"]["r"], 16),
                int(data["signature"]["s"], 16)
            )
        
        return cert
    
    def get_tbs_data(self) -> bytes:
        """获取待签名数据 (To Be Signed)"""
        tbs_data = {
            "subject": self.subject,
            "issuer": self.issuer,
            "public_key": {
                "x": hex(self.public_key.x),
                "y": hex(self.public_key.y)
            },
            "serial_number": self.serial_number,
            "not_before": self.not_before,
            "not_after": self.not_after,
            "signature_algorithm": self.signature_algorithm
        }
        return json.dumps(tbs_data, sort_keys=True).encode('utf-8')
    
    def is_valid_time(self) -> bool:
        """检查证书是否在有效期内"""
        current_time = int(time.time())
        return self.not_before <= current_time <= self.not_after

class SM2SignatureProtocol:
    """SM2数字签名协议类"""
    
    def __init__(self):
        self.sm2 = SM2Basic()
        self.certificates = {}  # 证书存储
        self.ca_keys = {}       # CA密钥存储
    
    def generate_ca_keypair(self, ca_name: str) -> Tuple[int, SM2Point]:
        """生成CA密钥对"""
        private_key, public_key = self.sm2.generate_keypair()
        self.ca_keys[ca_name] = {
            "private_key": private_key,
            "public_key": public_key
        }
        return private_key, public_key
    
    def create_certificate(self, subject: str, subject_public_key: SM2Point,
                          ca_name: str, validity_days: int = 365) -> SM2Certificate:
        """创建数字证书"""
        if ca_name not in self.ca_keys:
            raise ValueError(f"CA '{ca_name}' not found")
        
        current_time = int(time.time())
        serial_number = hashlib.sha256(
            f"{subject}{current_time}".encode()
        ).hexdigest()[:16]
        
        # 创建证书
        cert = SM2Certificate(
            subject=subject,
            issuer=ca_name,
            public_key=subject_public_key,
            serial_number=serial_number,
            not_before=current_time,
            not_after=current_time + validity_days * 24 * 3600
        )
        
        # 使用CA私钥签名证书
        ca_private_key = self.ca_keys[ca_name]["private_key"]
        tbs_data = cert.get_tbs_data()
        cert.signature = self.sm2.sign(tbs_data, ca_private_key)
        
        # 存储证书
        self.certificates[subject] = cert
        
        return cert
    
    def verify_certificate(self, cert: SM2Certificate, ca_public_key: SM2Point) -> bool:
        """验证数字证书"""
        if not cert.is_valid_time():
            return False
        
        if not cert.signature:
            return False
        
        tbs_data = cert.get_tbs_data()
        return self.sm2.verify(tbs_data, cert.signature, ca_public_key)
    
    def create_signature_with_cert(self, message: bytes, private_key: int,
                                  cert: SM2Certificate) -> Dict:
        """使用证书创建签名"""
        signature = self.sm2.sign(message, private_key)
        
        return {
            "message_hash": hashlib.sha256(message).hexdigest(),
            "signature": {
                "r": hex(signature[0]),
                "s": hex(signature[1])
            },
            "certificate": cert.to_dict(),
            "timestamp": int(time.time()),
            "algorithm": "SM2withSM3"
        }
    
    def verify_signature_with_cert(self, message: bytes, signature_data: Dict,
                                  ca_public_key: SM2Point) -> bool:
        """使用证书验证签名"""
        try:
            # 重构证书
            cert = SM2Certificate.from_dict(signature_data["certificate"])
            
            # 验证证书
            if not self.verify_certificate(cert, ca_public_key):
                return False
            
            # 验证消息哈希
            expected_hash = hashlib.sha256(message).hexdigest()
            if signature_data["message_hash"] != expected_hash:
                return False
            
            # 验证签名
            signature = (
                int(signature_data["signature"]["r"], 16),
                int(signature_data["signature"]["s"], 16)
            )
            
            return self.sm2.verify(message, signature, cert.public_key)
            
        except Exception:
            return False
    
    def create_signature_chain(self, message: bytes, signers: List[Tuple[str, int]]) -> List[Dict]:
        """创建签名链（多重签名）"""
        signature_chain = []
        
        for signer_name, private_key in signers:
            if signer_name not in self.certificates:
                raise ValueError(f"Certificate for '{signer_name}' not found")
            
            cert = self.certificates[signer_name]
            signature_data = self.create_signature_with_cert(message, private_key, cert)
            signature_chain.append(signature_data)
        
        return signature_chain
    
    def verify_signature_chain(self, message: bytes, signature_chain: List[Dict],
                              ca_public_key: SM2Point) -> bool:
        """验证签名链"""
        if not signature_chain:
            return False
        
        for signature_data in signature_chain:
            if not self.verify_signature_with_cert(message, signature_data, ca_public_key):
                return False
        
        return True
    
    def create_timestamped_signature(self, message: bytes, private_key: int,
                                   cert: SM2Certificate) -> Dict:
        """创建带时间戳的签名"""
        timestamp = int(time.time())
        timestamped_message = message + timestamp.to_bytes(8, 'big')
        
        signature = self.sm2.sign(timestamped_message, private_key)
        
        return {
            "message_hash": hashlib.sha256(message).hexdigest(),
            "signature": {
                "r": hex(signature[0]),
                "s": hex(signature[1])
            },
            "certificate": cert.to_dict(),
            "timestamp": timestamp,
            "algorithm": "SM2withSM3",
            "type": "timestamped"
        }
    
    def verify_timestamped_signature(self, message: bytes, signature_data: Dict,
                                   ca_public_key: SM2Point, max_age_seconds: int = 3600) -> bool:
        """验证带时间戳的签名"""
        try:
            # 检查时间戳
            current_time = int(time.time())
            signature_time = signature_data["timestamp"]
            
            if current_time - signature_time > max_age_seconds:
                return False
            
            # 重构证书
            cert = SM2Certificate.from_dict(signature_data["certificate"])
            
            # 验证证书
            if not self.verify_certificate(cert, ca_public_key):
                return False
            
            # 验证消息哈希
            expected_hash = hashlib.sha256(message).hexdigest()
            if signature_data["message_hash"] != expected_hash:
                return False
            
            # 重构带时间戳的消息
            timestamped_message = message + signature_time.to_bytes(8, 'big')
            
            # 验证签名
            signature = (
                int(signature_data["signature"]["r"], 16),
                int(signature_data["signature"]["s"], 16)
            )
            
            return self.sm2.verify(timestamped_message, signature, cert.public_key)
            
        except Exception:
            return False
    
    def export_certificate(self, subject: str, filename: str):
        """导出证书到文件"""
        if subject not in self.certificates:
            raise ValueError(f"Certificate for '{subject}' not found")
        
        cert_data = self.certificates[subject].to_dict()
        with open(filename, 'w') as f:
            json.dump(cert_data, f, indent=2)
    
    def import_certificate(self, filename: str) -> SM2Certificate:
        """从文件导入证书"""
        with open(filename, 'r') as f:
            cert_data = json.load(f)
        
        cert = SM2Certificate.from_dict(cert_data)
        self.certificates[cert.subject] = cert
        return cert

def demo_signature_protocol():
    """演示签名协议功能"""
    print("SM2 Signature Protocol Demo")
    print("=" * 50)
    
    # 创建签名协议实例
    protocol = SM2SignatureProtocol()
    
    # 1. 创建CA
    print("1. Creating Certificate Authority...")
    ca_private_key, ca_public_key = protocol.generate_ca_keypair("TestCA")
    print(f"CA created: TestCA")
    print(f"CA Public Key: {ca_public_key}")
    print()
    
    # 2. 生成用户密钥对
    print("2. Generating user keypairs...")
    alice_private_key, alice_public_key = protocol.sm2.generate_keypair()
    bob_private_key, bob_public_key = protocol.sm2.generate_keypair()
    print(f"Alice's keypair generated")
    print(f"Bob's keypair generated")
    print()
    
    # 3. 创建证书
    print("3. Creating certificates...")
    alice_cert = protocol.create_certificate("Alice", alice_public_key, "TestCA", 365)
    bob_cert = protocol.create_certificate("Bob", bob_public_key, "TestCA", 365)
    print(f"Alice's certificate created: {alice_cert.serial_number}")
    print(f"Bob's certificate created: {bob_cert.serial_number}")
    print()
    
    # 4. 验证证书
    print("4. Verifying certificates...")
    alice_cert_valid = protocol.verify_certificate(alice_cert, ca_public_key)
    bob_cert_valid = protocol.verify_certificate(bob_cert, ca_public_key)
    print(f"Alice's certificate valid: {alice_cert_valid}")
    print(f"Bob's certificate valid: {bob_cert_valid}")
    print()
    
    # 5. 创建带证书的签名
    print("5. Creating signed document...")
    document = b"This is a confidential document that needs to be signed."
    alice_signature = protocol.create_signature_with_cert(document, alice_private_key, alice_cert)
    print(f"Document signed by Alice")
    print(f"Signature: {alice_signature['signature']['r'][:20]}...")
    print()
    
    # 6. 验证签名
    print("6. Verifying signature...")
    signature_valid = protocol.verify_signature_with_cert(document, alice_signature, ca_public_key)
    print(f"Signature verification: {signature_valid}")
    print()
    
    # 7. 创建签名链（多重签名）
    print("7. Creating signature chain...")
    signers = [("Alice", alice_private_key), ("Bob", bob_private_key)]
    signature_chain = protocol.create_signature_chain(document, signers)
    print(f"Signature chain created with {len(signature_chain)} signatures")
    print()
    
    # 8. 验证签名链
    print("8. Verifying signature chain...")
    chain_valid = protocol.verify_signature_chain(document, signature_chain, ca_public_key)
    print(f"Signature chain verification: {chain_valid}")
    print()
    
    # 9. 创建带时间戳的签名
    print("9. Creating timestamped signature...")
    timestamped_signature = protocol.create_timestamped_signature(document, alice_private_key, alice_cert)
    print(f"Timestamped signature created")
    print(f"Timestamp: {timestamped_signature['timestamp']}")
    print()
    
    # 10. 验证带时间戳的签名
    print("10. Verifying timestamped signature...")
    timestamped_valid = protocol.verify_timestamped_signature(document, timestamped_signature, ca_public_key)
    print(f"Timestamped signature verification: {timestamped_valid}")
    print()
    
    # 11. 导出和导入证书
    print("11. Certificate export/import...")
    try:
        protocol.export_certificate("Alice", "alice_cert.json")
        imported_cert = protocol.import_certificate("alice_cert.json")
        print(f"Certificate exported and imported successfully")
        print(f"Imported certificate subject: {imported_cert.subject}")
    except Exception as e:
        print(f"Certificate export/import failed: {e}")

if __name__ == "__main__":
    demo_signature_protocol() 