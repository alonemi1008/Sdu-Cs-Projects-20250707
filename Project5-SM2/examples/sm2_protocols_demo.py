#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SM2协议综合演示程序
展示签名协议和密钥交换协议的完整功能
"""

import sys
import time
import json
from src.protocols.sm2_signature_protocol import SM2SignatureProtocol, SM2Certificate
from src.protocols.sm2_key_exchange import SM2KeyExchange, SM2KeyExchangeParty, SM2KeyExchangeSession

def demo_signature_protocol():
    """演示签名协议"""
    print("SM2 Digital Signature Protocol Demo")
    print("=" * 60)
    
    # 创建签名协议实例
    protocol = SM2SignatureProtocol()
    
    print("1. Setting up Certificate Authority...")
    # 创建CA
    ca_private_key, ca_public_key = protocol.generate_ca_keypair("RootCA")
    print(f"   CA 'RootCA' created successfully")
    print(f"   CA Public Key: {ca_public_key}")
    print()
    
    print("2. Generating user credentials...")
    # 生成用户密钥对
    alice_private_key, alice_public_key = protocol.sm2.generate_keypair()
    bob_private_key, bob_public_key = protocol.sm2.generate_keypair()
    charlie_private_key, charlie_public_key = protocol.sm2.generate_keypair()
    
    print(f"   Alice's keypair generated")
    print(f"   Bob's keypair generated")
    print(f"   Charlie's keypair generated")
    print()
    
    print("3. Issuing digital certificates...")
    # 创建证书
    alice_cert = protocol.create_certificate("Alice", alice_public_key, "RootCA", 365)
    bob_cert = protocol.create_certificate("Bob", bob_public_key, "RootCA", 365)
    charlie_cert = protocol.create_certificate("Charlie", charlie_public_key, "RootCA", 365)
    
    print(f"   Alice's certificate: {alice_cert.serial_number}")
    print(f"   Bob's certificate: {bob_cert.serial_number}")
    print(f"   Charlie's certificate: {charlie_cert.serial_number}")
    print()
    
    print("4. Document signing scenario...")
    # 创建要签名的文档
    contract = b"Service Agreement between Alice and Bob for software development project. Amount: $50,000. Duration: 6 months."
    
    print(f"   Document: {contract.decode()}")
    print()
    
    # Alice签名
    print("   Alice signs the contract...")
    alice_signature = protocol.create_signature_with_cert(contract, alice_private_key, alice_cert)
    print(f"   Alice's signature created at timestamp: {alice_signature['timestamp']}")
    
    # Bob签名
    print("   Bob signs the contract...")
    bob_signature = protocol.create_signature_with_cert(contract, bob_private_key, bob_cert)
    print(f"   Bob's signature created at timestamp: {bob_signature['timestamp']}")
    print()
    
    print("5. Signature verification...")
    # 验证签名
    alice_valid = protocol.verify_signature_with_cert(contract, alice_signature, ca_public_key)
    bob_valid = protocol.verify_signature_with_cert(contract, bob_signature, ca_public_key)
    
    print(f"   Alice's signature verification: {'VALID' if alice_valid else 'INVALID'}")
    print(f"   Bob's signature verification: {'VALID' if bob_valid else 'INVALID'}")
    print()
    
    print("6. Multi-party signature chain...")
    # 创建签名链
    signers = [("Alice", alice_private_key), ("Bob", bob_private_key), ("Charlie", charlie_private_key)]
    signature_chain = protocol.create_signature_chain(contract, signers)
    
    print(f"   Signature chain created with {len(signature_chain)} signatures")
    
    # 验证签名链
    chain_valid = protocol.verify_signature_chain(contract, signature_chain, ca_public_key)
    print(f"   Signature chain verification: {'VALID' if chain_valid else 'INVALID'}")
    print()
    
    print("7. Timestamped signature...")
    # 创建带时间戳的签名
    important_document = b"Critical security update notification - All systems must be updated by end of month."
    timestamped_signature = protocol.create_timestamped_signature(important_document, alice_private_key, alice_cert)
    
    print(f"   Timestamped signature created")
    print(f"   Timestamp: {time.ctime(timestamped_signature['timestamp'])}")
    
    # 验证时间戳签名
    timestamped_valid = protocol.verify_timestamped_signature(important_document, timestamped_signature, ca_public_key)
    print(f"   Timestamped signature verification: {'VALID' if timestamped_valid else 'INVALID'}")
    print()
    
    print("8. Certificate management...")
    # 导出证书
    try:
        protocol.export_certificate("Alice", "alice_certificate.json")
        print("   Alice's certificate exported to alice_certificate.json")
        
        # 导入证书
        imported_cert = protocol.import_certificate("alice_certificate.json")
        print(f"   Certificate imported: {imported_cert.subject}")
        print(f"   Certificate valid: {protocol.verify_certificate(imported_cert, ca_public_key)}")
    except Exception as e:
        print(f"   Certificate export/import error: {e}")
    
    print("\n" + "=" * 60)
    return protocol

def demo_key_exchange_protocol():
    """演示密钥交换协议"""
    print("SM2 Key Exchange Protocol Demo")
    print("=" * 60)
    
    # 创建密钥交换实例
    ke = SM2KeyExchange()
    
    print("1. Basic key exchange...")
    # 创建参与方
    alice = SM2KeyExchangeParty("Alice", ke.sm2)
    bob = SM2KeyExchangeParty("Bob", ke.sm2)
    
    # 生成长期密钥对
    alice.generate_keypair()
    bob.generate_keypair()
    
    print(f"   Alice and Bob generated their keypairs")
    print(f"   Alice's public key: {alice.public_key}")
    print(f"   Bob's public key: {bob.public_key}")
    print()
    
    # 执行密钥交换
    print("2. Executing key exchange...")
    start_time = time.time()
    
    try:
        alice_key, bob_key = ke.complete_key_exchange(alice, bob)
        exchange_time = time.time() - start_time
        
        print(f"   Key exchange completed in {exchange_time:.4f} seconds")
        print(f"   Alice's session key: {alice_key.hex()}")
        print(f"   Bob's session key: {bob_key.hex()}")
        print(f"   Keys match: {'YES' if alice_key == bob_key else 'NO'}")
        print(f"   Key length: {len(alice_key)} bytes")
        print()
        
    except Exception as e:
        print(f"   Key exchange failed: {e}")
        return None
    
    print("3. Session management...")
    # 创建会话管理器
    session_manager = SM2KeyExchangeSession(ke)
    
    # 创建多个会话
    sessions = []
    for i in range(3):
        session_id = f"session_{i+1:03d}"
        session_manager.create_session(session_id, f"User{i+1}A", f"User{i+1}B")
        result = session_manager.execute_key_exchange(session_id)
        sessions.append(result)
        print(f"   Session {session_id}: {result['status']}")
    
    print(f"   Total sessions created: {len(sessions)}")
    print()
    
    print("4. Performance analysis...")
    # 性能测试
    test_iterations = 5
    start_time = time.time()
    
    for i in range(test_iterations):
        test_alice = SM2KeyExchangeParty(f"TestAlice{i}", ke.sm2)
        test_bob = SM2KeyExchangeParty(f"TestBob{i}", ke.sm2)
        test_alice.generate_keypair()
        test_bob.generate_keypair()
        ke.complete_key_exchange(test_alice, test_bob)
    
    total_time = time.time() - start_time
    avg_time = total_time / test_iterations
    
    print(f"   Performance test completed:")
    print(f"   Total time for {test_iterations} key exchanges: {total_time:.4f} seconds")
    print(f"   Average time per key exchange: {avg_time:.4f} seconds")
    print(f"   Throughput: {test_iterations / total_time:.2f} exchanges/second")
    
    print("\n" + "=" * 60)
    return ke, session_manager

def demo_integrated_scenario():
    """演示集成场景：签名+密钥交换"""
    print("Integrated Scenario: Secure Document Exchange")
    print("=" * 60)
    
    # 初始化协议
    signature_protocol = SM2SignatureProtocol()
    key_exchange = SM2KeyExchange()
    
    print("1. Setting up secure communication environment...")
    
    # 创建CA
    ca_private_key, ca_public_key = signature_protocol.generate_ca_keypair("SecureCA")
    print("   Certificate Authority established")
    
    # 创建用户
    alice_private_key, alice_public_key = signature_protocol.sm2.generate_keypair()
    bob_private_key, bob_public_key = signature_protocol.sm2.generate_keypair()
    
    # 颁发证书
    alice_cert = signature_protocol.create_certificate("Alice", alice_public_key, "SecureCA", 365)
    bob_cert = signature_protocol.create_certificate("Bob", bob_public_key, "SecureCA", 365)
    
    print("   User certificates issued")
    print(f"   Alice's certificate: {alice_cert.serial_number}")
    print(f"   Bob's certificate: {bob_cert.serial_number}")
    print()
    
    print("2. Establishing secure session...")
    
    # 密钥交换
    alice_ke = SM2KeyExchangeParty("Alice", key_exchange.sm2)
    bob_ke = SM2KeyExchangeParty("Bob", key_exchange.sm2)
    
    # 使用相同的长期密钥
    alice_ke.private_key = alice_private_key
    alice_ke.public_key = alice_public_key
    bob_ke.private_key = bob_private_key
    bob_ke.public_key = bob_public_key
    
    # 执行密钥交换
    session_key_alice, session_key_bob = key_exchange.complete_key_exchange(alice_ke, bob_ke)
    
    print(f"   Session established successfully")
    print(f"   Session key: {session_key_alice.hex()[:32]}...")
    print(f"   Keys match: {'YES' if session_key_alice == session_key_bob else 'NO'}")
    print()
    
    print("3. Secure document exchange...")
    
    # 创建机密文档
    confidential_doc = b"TOP SECRET: New product launch plan for Q4 2024. Revenue target: $10M. Key partners: TechCorp, DataSys."
    
    print(f"   Document: {confidential_doc.decode()}")
    print()
    
    # Alice签名文档
    alice_signature = signature_protocol.create_signature_with_cert(
        confidential_doc, alice_private_key, alice_cert
    )
    
    print("   Alice signs the document")
    print(f"   Signature timestamp: {time.ctime(alice_signature['timestamp'])}")
    
    # Bob验证签名
    signature_valid = signature_protocol.verify_signature_with_cert(
        confidential_doc, alice_signature, ca_public_key
    )
    
    print(f"   Bob verifies signature: {'VALID' if signature_valid else 'INVALID'}")
    print()
    
    print("4. Document integrity and authenticity verification...")
    
    # 模拟文档传输后的验证
    print("   Verifying document integrity...")
    
    # 验证证书链
    alice_cert_valid = signature_protocol.verify_certificate(alice_cert, ca_public_key)
    print(f"   Alice's certificate valid: {'YES' if alice_cert_valid else 'NO'}")
    
    # 验证签名
    final_verification = signature_protocol.verify_signature_with_cert(
        confidential_doc, alice_signature, ca_public_key
    )
    print(f"   Document signature valid: {'YES' if final_verification else 'NO'}")
    
    # 验证时间戳（确保文档是最近签名的）
    current_time = int(time.time())
    signature_time = alice_signature['timestamp']
    time_diff = current_time - signature_time
    print(f"   Document age: {time_diff} seconds")
    print(f"   Document is recent: {'YES' if time_diff < 3600 else 'NO'}")
    print()
    
    print("5. Multi-party approval workflow...")
    
    # 创建需要多方批准的文档
    approval_doc = b"Budget approval request: $500,000 for infrastructure upgrade. Requires: CTO + CFO approval."
    
    print(f"   Approval document: {approval_doc.decode()}")
    
    # 创建CFO证书
    cfo_private_key, cfo_public_key = signature_protocol.sm2.generate_keypair()
    cfo_cert = signature_protocol.create_certificate("CFO", cfo_public_key, "SecureCA", 365)
    
    # 多方签名
    approvers = [("Alice", alice_private_key), ("CFO", cfo_private_key)]
    approval_chain = signature_protocol.create_signature_chain(approval_doc, approvers)
    
    print(f"   Multi-party approval chain created")
    print(f"   Number of approvals: {len(approval_chain)}")
    
    # 验证批准链
    approval_valid = signature_protocol.verify_signature_chain(approval_doc, approval_chain, ca_public_key)
    print(f"   Approval chain valid: {'YES' if approval_valid else 'NO'}")
    
    print("\n" + "=" * 60)
    return {
        'signature_protocol': signature_protocol,
        'key_exchange': key_exchange,
        'session_key': session_key_alice,
        'certificates': {
            'alice': alice_cert,
            'bob': bob_cert,
            'cfo': cfo_cert
        }
    }

def demo_performance_comparison():
    """性能对比演示"""
    print("Performance Comparison: Signature vs Key Exchange")
    print("=" * 60)
    
    signature_protocol = SM2SignatureProtocol()
    key_exchange = SM2KeyExchange()
    
    # 设置测试环境
    ca_private_key, ca_public_key = signature_protocol.generate_ca_keypair("PerfTestCA")
    
    iterations = 10
    print(f"Running performance test with {iterations} iterations...")
    print()
    
    # 签名性能测试
    print("1. Digital Signature Performance:")
    
    signature_times = []
    verification_times = []
    
    for i in range(iterations):
        # 生成密钥对和证书
        private_key, public_key = signature_protocol.sm2.generate_keypair()
        cert = signature_protocol.create_certificate(f"User{i}", public_key, "PerfTestCA", 365)
        
        # 测试文档
        document = f"Performance test document {i}".encode()
        
        # 签名性能
        start_time = time.time()
        signature = signature_protocol.create_signature_with_cert(document, private_key, cert)
        sign_time = time.time() - start_time
        signature_times.append(sign_time)
        
        # 验证性能
        start_time = time.time()
        signature_protocol.verify_signature_with_cert(document, signature, ca_public_key)
        verify_time = time.time() - start_time
        verification_times.append(verify_time)
    
    avg_sign_time = sum(signature_times) / len(signature_times)
    avg_verify_time = sum(verification_times) / len(verification_times)
    
    print(f"   Average signing time: {avg_sign_time:.4f} seconds")
    print(f"   Average verification time: {avg_verify_time:.4f} seconds")
    print(f"   Signature throughput: {1/avg_sign_time:.2f} signatures/second")
    print()
    
    # 密钥交换性能测试
    print("2. Key Exchange Performance:")
    
    ke_times = []
    
    for i in range(iterations):
        alice = SM2KeyExchangeParty(f"Alice{i}", key_exchange.sm2)
        bob = SM2KeyExchangeParty(f"Bob{i}", key_exchange.sm2)
        
        alice.generate_keypair()
        bob.generate_keypair()
        
        start_time = time.time()
        key_exchange.complete_key_exchange(alice, bob)
        ke_time = time.time() - start_time
        ke_times.append(ke_time)
    
    avg_ke_time = sum(ke_times) / len(ke_times)
    
    print(f"   Average key exchange time: {avg_ke_time:.4f} seconds")
    print(f"   Key exchange throughput: {1/avg_ke_time:.2f} exchanges/second")
    print()
    
    # 对比分析
    print("3. Performance Analysis:")
    print(f"   Signature is {avg_ke_time/avg_sign_time:.2f}x faster than key exchange")
    print(f"   Verification is {avg_ke_time/avg_verify_time:.2f}x faster than key exchange")
    print(f"   Key exchange provides session keys for bulk encryption")
    print(f"   Signatures provide non-repudiation and authentication")
    
    print("\n" + "=" * 60)

def main():
    """主程序"""
    print("SM2 Protocols Comprehensive Demo")
    print("=" * 70)
    print("This demo showcases SM2 digital signature and key exchange protocols")
    print("=" * 70)
    print()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'signature':
            demo_signature_protocol()
        elif mode == 'keyexchange':
            demo_key_exchange_protocol()
        elif mode == 'integrated':
            demo_integrated_scenario()
        elif mode == 'performance':
            demo_performance_comparison()
        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: signature, keyexchange, integrated, performance")
    else:
        # 运行所有演示
        print("Running comprehensive protocol demonstration...")
        print()
        
        # 1. 签名协议演示
        demo_signature_protocol()
        input("\nPress Enter to continue to key exchange demo...")
        
        # 2. 密钥交换协议演示
        demo_key_exchange_protocol()
        input("\nPress Enter to continue to integrated scenario...")
        
        # 3. 集成场景演示
        demo_integrated_scenario()
        input("\nPress Enter to continue to performance comparison...")
        
        # 4. 性能对比演示
        demo_performance_comparison()
        
        print("\n" + "=" * 70)
        print("All demonstrations completed successfully!")
        print("=" * 70)

if __name__ == "__main__":
    main() 