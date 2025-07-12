#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SM2密钥交换协议实现
实现SM2-KE密钥交换协议，支持双方密钥协商
"""

import hashlib
import random
import time
from typing import Tuple, Dict, Optional, List
from ..core.sm2_basic import SM2Basic, SM2Point

class SM2KeyExchangeParty:
    """SM2密钥交换参与方"""
    
    def __init__(self, party_id: str, sm2: SM2Basic):
        self.party_id = party_id
        self.sm2 = sm2
        self.private_key = None
        self.public_key = None
        self.temp_private_key = None
        self.temp_public_key = None
        self.shared_secret = None
        self.session_key = None
        
    def generate_keypair(self) -> Tuple[int, SM2Point]:
        """生成长期密钥对"""
        self.private_key, self.public_key = self.sm2.generate_keypair()
        return self.private_key, self.public_key
    
    def generate_temp_keypair(self) -> Tuple[int, SM2Point]:
        """生成临时密钥对"""
        self.temp_private_key, self.temp_public_key = self.sm2.generate_keypair()
        return self.temp_private_key, self.temp_public_key

class SM2KeyExchange:
    """SM2密钥交换协议"""
    
    def __init__(self):
        self.sm2 = SM2Basic()
        self.key_length = 32  # 默认会话密钥长度（字节）
    
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
    
    def _hash(self, *args) -> bytes:
        """哈希函数"""
        hasher = hashlib.sha256()
        for arg in args:
            if isinstance(arg, bytes):
                hasher.update(arg)
            elif isinstance(arg, int):
                hasher.update(arg.to_bytes(32, 'big'))
            elif isinstance(arg, SM2Point):
                hasher.update(arg.x.to_bytes(32, 'big'))
                hasher.update(arg.y.to_bytes(32, 'big'))
            elif isinstance(arg, str):
                hasher.update(arg.encode('utf-8'))
        return hasher.digest()
    
    def _check_point_order(self, point: SM2Point) -> bool:
        """检查点是否满足阶的要求"""
        if point.is_infinity:
            return False
        
        # 检查点是否在曲线上
        left = (point.y * point.y) % self.sm2.p
        right = (point.x * point.x * point.x + self.sm2.a * point.x + self.sm2.b) % self.sm2.p
        if left != right:
            return False
        
        # 检查点的阶（简化检查）
        result = self.sm2.point_multiply(self.sm2.n, point)
        return result.is_infinity
    
    def phase1_initiator(self, initiator: SM2KeyExchangeParty, 
                        responder_id: str, responder_public_key: SM2Point) -> Dict:
        """密钥交换第一阶段 - 发起方"""
        # 生成临时密钥对
        r_a, R_A = initiator.generate_temp_keypair()
        
        # 存储对方信息
        initiator.responder_id = responder_id
        initiator.responder_public_key = responder_public_key
        
        return {
            "party_id": initiator.party_id,
            "public_key": initiator.public_key,
            "temp_public_key": R_A,
            "timestamp": int(time.time())
        }
    
    def phase1_responder(self, responder: SM2KeyExchangeParty,
                        initiator_data: Dict) -> Dict:
        """密钥交换第一阶段 - 响应方"""
        # 验证发起方的临时公钥
        R_A = initiator_data["temp_public_key"]
        if not self._check_point_order(R_A):
            raise ValueError("Invalid initiator temp public key")
        
        # 生成临时密钥对
        r_b, R_B = responder.generate_temp_keypair()
        
        # 存储对方信息
        responder.initiator_id = initiator_data["party_id"]
        responder.initiator_public_key = initiator_data["public_key"]
        responder.initiator_temp_public_key = R_A
        
        return {
            "party_id": responder.party_id,
            "public_key": responder.public_key,
            "temp_public_key": R_B,
            "timestamp": int(time.time())
        }
    
    def phase2_compute_shared_secret(self, party: SM2KeyExchangeParty,
                                   other_temp_public_key: SM2Point,
                                   other_public_key: SM2Point,
                                   other_id: str, is_initiator: bool) -> bytes:
        """计算共享密钥"""
        # 验证对方的临时公钥
        if not self._check_point_order(other_temp_public_key):
            raise ValueError("Invalid temp public key")
        
        # 计算共享点
        # x = 2^w + (x_A mod 2^w) 其中w = ceil(log2(n)/2) - 1
        w = (self.sm2.n.bit_length() + 1) // 2 - 1
        x_mask = (1 << w) - 1
        
        if is_initiator:
            # 发起方计算
            x_a = (1 << w) + (party.temp_public_key.x & x_mask)
            t_a = (party.private_key + x_a * party.temp_private_key) % self.sm2.n
            
            x_b = (1 << w) + (other_temp_public_key.x & x_mask)
            
            # 计算 V = h * t_a * (P_b + x_b * R_b)
            point1 = self.sm2.point_multiply(x_b, other_temp_public_key)
            point2 = self.sm2.point_add(other_public_key, point1)
            V = self.sm2.point_multiply(t_a, point2)
            
        else:
            # 响应方计算
            x_b = (1 << w) + (party.temp_public_key.x & x_mask)
            t_b = (party.private_key + x_b * party.temp_private_key) % self.sm2.n
            
            x_a = (1 << w) + (other_temp_public_key.x & x_mask)
            
            # 计算 U = h * t_b * (P_a + x_a * R_a)
            point1 = self.sm2.point_multiply(x_a, other_temp_public_key)
            point2 = self.sm2.point_add(other_public_key, point1)
            V = self.sm2.point_multiply(t_b, point2)
        
        if V.is_infinity:
            raise ValueError("Key exchange failed: point at infinity")
        
        # 计算共享密钥材料
        if is_initiator:
            z = self._hash(
                V.x, V.y,
                party.party_id,
                other_id,
                party.public_key,
                other_public_key,
                party.temp_public_key,
                other_temp_public_key
            )
        else:
            z = self._hash(
                V.x, V.y,
                other_id,
                party.party_id,
                other_public_key,
                party.public_key,
                other_temp_public_key,
                party.temp_public_key
            )
        
        # 派生会话密钥
        party.shared_secret = z
        party.session_key = self._kdf(z, self.key_length)
        
        return party.session_key
    
    def phase3_generate_confirmation(self, party: SM2KeyExchangeParty,
                                   other_temp_public_key: SM2Point,
                                   other_public_key: SM2Point,
                                   other_id: str, is_initiator: bool) -> bytes:
        """生成密钥确认值"""
        if party.shared_secret is None:
            raise ValueError("Shared secret not computed")
        
        if is_initiator:
            # 发起方生成确认值
            confirmation_data = self._hash(
                b"KeyConfirmation",
                party.shared_secret,
                party.party_id,
                other_id,
                party.public_key,
                other_public_key,
                party.temp_public_key,
                other_temp_public_key
            )
        else:
            # 响应方生成确认值
            confirmation_data = self._hash(
                b"KeyConfirmation",
                party.shared_secret,
                other_id,
                party.party_id,
                other_public_key,
                party.public_key,
                other_temp_public_key,
                party.temp_public_key
            )
        
        return confirmation_data
    
    def verify_confirmation(self, party: SM2KeyExchangeParty,
                          received_confirmation: bytes,
                          other_temp_public_key: SM2Point,
                          other_public_key: SM2Point,
                          other_id: str, is_initiator: bool) -> bool:
        """验证密钥确认值"""
        # 创建临时的对方参与方对象来生成期望的确认值
        other_party = SM2KeyExchangeParty(other_id, self.sm2)
        other_party.public_key = other_public_key
        other_party.temp_public_key = other_temp_public_key
        other_party.shared_secret = party.shared_secret  # 使用相同的共享密钥
        
        # 生成对方应该生成的确认值（对方的角色与当前方相反）
        expected_confirmation = self.phase3_generate_confirmation(
            other_party, party.temp_public_key, party.public_key, party.party_id, not is_initiator
        )
        
        return received_confirmation == expected_confirmation
    
    def complete_key_exchange(self, initiator: SM2KeyExchangeParty,
                            responder: SM2KeyExchangeParty) -> Tuple[bytes, bytes]:
        """完成密钥交换过程"""
        # 第一阶段：交换临时公钥
        initiator_msg = self.phase1_initiator(initiator, responder.party_id, responder.public_key)
        responder_msg = self.phase1_responder(responder, initiator_msg)
        
        # 第二阶段：计算共享密钥
        initiator_key = self.phase2_compute_shared_secret(
            initiator, responder.temp_public_key, responder.public_key,
            responder.party_id, True
        )
        
        responder_key = self.phase2_compute_shared_secret(
            responder, initiator.temp_public_key, initiator.public_key,
            initiator.party_id, False
        )
        
        # 验证密钥一致性
        if initiator_key != responder_key:
            raise ValueError("Key exchange failed: keys don't match")
        
        # 第三阶段：密钥确认
        initiator_confirmation = self.phase3_generate_confirmation(
            initiator, responder.temp_public_key, responder.public_key,
            responder.party_id, True
        )
        
        responder_confirmation = self.phase3_generate_confirmation(
            responder, initiator.temp_public_key, initiator.public_key,
            initiator.party_id, False
        )
        
        # 验证确认值
        initiator_verify = self.verify_confirmation(
            initiator, responder_confirmation, responder.temp_public_key,
            responder.public_key, responder.party_id, True
        )
        
        responder_verify = self.verify_confirmation(
            responder, initiator_confirmation, initiator.temp_public_key,
            initiator.public_key, initiator.party_id, False
        )
        
        if not (initiator_verify and responder_verify):
            raise ValueError("Key exchange failed: confirmation verification failed")
        
        return initiator_key, responder_key

class SM2KeyExchangeSession:
    """SM2密钥交换会话管理"""
    
    def __init__(self, key_exchange: SM2KeyExchange):
        self.ke = key_exchange
        self.sessions = {}
    
    def create_session(self, session_id: str, initiator_id: str, responder_id: str) -> Dict:
        """创建密钥交换会话"""
        initiator = SM2KeyExchangeParty(initiator_id, self.ke.sm2)
        responder = SM2KeyExchangeParty(responder_id, self.ke.sm2)
        
        # 生成长期密钥对
        initiator.generate_keypair()
        responder.generate_keypair()
        
        session = {
            "session_id": session_id,
            "initiator": initiator,
            "responder": responder,
            "status": "created",
            "created_time": int(time.time())
        }
        
        self.sessions[session_id] = session
        return session
    
    def execute_key_exchange(self, session_id: str) -> Dict:
        """执行密钥交换"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        initiator = session["initiator"]
        responder = session["responder"]
        
        try:
            # 执行密钥交换
            initiator_key, responder_key = self.ke.complete_key_exchange(initiator, responder)
            
            session["status"] = "completed"
            session["session_key"] = initiator_key
            session["completed_time"] = int(time.time())
            
            return {
                "session_id": session_id,
                "status": "success",
                "session_key": initiator_key.hex(),
                "key_length": len(initiator_key)
            }
            
        except Exception as e:
            session["status"] = "failed"
            session["error"] = str(e)
            raise
    
    def get_session_info(self, session_id: str) -> Dict:
        """获取会话信息"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "initiator_id": session["initiator"].party_id,
            "responder_id": session["responder"].party_id,
            "status": session["status"],
            "created_time": session["created_time"],
            "completed_time": session.get("completed_time"),
            "has_session_key": session.get("session_key") is not None
        }

def demo_key_exchange():
    """演示密钥交换功能"""
    print("SM2 Key Exchange Protocol Demo")
    print("=" * 50)
    
    # 创建密钥交换实例
    ke = SM2KeyExchange()
    
    # 创建参与方
    print("1. Creating parties...")
    alice = SM2KeyExchangeParty("Alice", ke.sm2)
    bob = SM2KeyExchangeParty("Bob", ke.sm2)
    
    # 生成长期密钥对
    alice.generate_keypair()
    bob.generate_keypair()
    
    print(f"Alice's public key: {alice.public_key}")
    print(f"Bob's public key: {bob.public_key}")
    print()
    
    # 执行密钥交换
    print("2. Executing key exchange...")
    start_time = time.time()
    
    try:
        alice_key, bob_key = ke.complete_key_exchange(alice, bob)
        
        exchange_time = time.time() - start_time
        print(f"Key exchange completed in {exchange_time:.4f} seconds")
        print(f"Alice's session key: {alice_key.hex()}")
        print(f"Bob's session key: {bob_key.hex()}")
        print(f"Keys match: {alice_key == bob_key}")
        print(f"Key length: {len(alice_key)} bytes")
        print()
        
    except Exception as e:
        print(f"Key exchange failed: {e}")
        return
    
    # 测试会话管理
    print("3. Testing session management...")
    session_manager = SM2KeyExchangeSession(ke)
    
    # 创建会话
    session = session_manager.create_session("session_001", "Alice", "Bob")
    print(f"Session created: {session['session_id']}")
    
    # 执行密钥交换
    result = session_manager.execute_key_exchange("session_001")
    print(f"Session key exchange result: {result['status']}")
    print(f"Session key: {result['session_key'][:32]}...")
    
    # 获取会话信息
    info = session_manager.get_session_info("session_001")
    print(f"Session info: {info}")
    print()
    
    # 多会话测试
    print("4. Testing multiple sessions...")
    sessions = []
    for i in range(5):
        session_id = f"session_{i:03d}"
        session_manager.create_session(session_id, f"User{i}A", f"User{i}B")
        result = session_manager.execute_key_exchange(session_id)
        sessions.append(result)
        print(f"Session {session_id}: {result['status']}")
    
    print(f"Total sessions created: {len(sessions)}")
    print()
    
    # 性能测试
    print("5. Performance test...")
    test_iterations = 10
    start_time = time.time()
    
    for i in range(test_iterations):
        test_alice = SM2KeyExchangeParty(f"TestAlice{i}", ke.sm2)
        test_bob = SM2KeyExchangeParty(f"TestBob{i}", ke.sm2)
        test_alice.generate_keypair()
        test_bob.generate_keypair()
        
        ke.complete_key_exchange(test_alice, test_bob)
    
    total_time = time.time() - start_time
    avg_time = total_time / test_iterations
    
    print(f"Performance test completed:")
    print(f"Total time for {test_iterations} key exchanges: {total_time:.4f} seconds")
    print(f"Average time per key exchange: {avg_time:.4f} seconds")
    print(f"Throughput: {test_iterations / total_time:.2f} exchanges/second")

if __name__ == "__main__":
    demo_key_exchange() 