#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SM2椭圆曲线密码算法主演示程序
展示SM2的加密解密、数字签名功能以及性能对比
"""

import sys
import time
import random
from sm2_basic import SM2Basic
from sm2_optimized import SM2Optimized
from performance_test import SM2PerformanceTester

def demo_basic_functionality():
    """演示SM2基本功能"""
    print("SM2 Basic Functionality Demo")
    print("=" * 50)
    
    # 创建SM2实例
    sm2 = SM2Basic()
    
    # 生成密钥对
    print("1. Key Generation")
    print("-" * 20)
    start_time = time.time()
    private_key, public_key = sm2.generate_keypair()
    keygen_time = time.time() - start_time
    
    print(f"Private Key: {hex(private_key)}")
    print(f"Public Key X: {hex(public_key.x)}")
    print(f"Public Key Y: {hex(public_key.y)}")
    print(f"Key Generation Time: {keygen_time:.4f} seconds")
    print()
    
    # 加密解密演示
    print("2. Encryption/Decryption")
    print("-" * 25)
    
    # 测试不同长度的消息
    test_messages = [
        b"Hello, SM2!",
        b"This is a longer message to test SM2 encryption capabilities.",
        b"SM2 is a public key cryptographic algorithm based on elliptic curves. " +
        b"It was developed by Chinese cryptographers and is widely used in China."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: Message length = {len(message)} bytes")
        print(f"Original: {message}")
        
        # 加密
        start_time = time.time()
        ciphertext = sm2.encrypt(message, public_key)
        encrypt_time = time.time() - start_time
        
        print(f"Ciphertext length: {len(ciphertext)} bytes")
        print(f"Encryption time: {encrypt_time:.4f} seconds")
        
        # 解密
        start_time = time.time()
        decrypted = sm2.decrypt(ciphertext, private_key)
        decrypt_time = time.time() - start_time
        
        print(f"Decrypted: {decrypted}")
        print(f"Decryption time: {decrypt_time:.4f} seconds")
        print(f"Verification: {'PASS' if message == decrypted else 'FAIL'}")
        print()
    
    # 数字签名演示
    print("3. Digital Signature")
    print("-" * 20)
    
    test_sign_messages = [
        b"Document to be signed",
        b"Contract agreement between parties",
        b"Financial transaction record"
    ]
    
    for i, message in enumerate(test_sign_messages, 1):
        print(f"Signature Test {i}:")
        print(f"Message: {message}")
        
        # 签名
        start_time = time.time()
        signature = sm2.sign(message, private_key)
        sign_time = time.time() - start_time
        
        print(f"Signature: r={hex(signature[0])[:20]}...")
        print(f"           s={hex(signature[1])[:20]}...")
        print(f"Signing time: {sign_time:.4f} seconds")
        
        # 验证
        start_time = time.time()
        is_valid = sm2.verify(message, signature, public_key)
        verify_time = time.time() - start_time
        
        print(f"Verification: {'VALID' if is_valid else 'INVALID'}")
        print(f"Verification time: {verify_time:.4f} seconds")
        
        # 测试错误签名
        wrong_message = message + b" (modified)"
        is_valid_wrong = sm2.verify(wrong_message, signature, public_key)
        print(f"Wrong message verification: {'VALID' if is_valid_wrong else 'INVALID'}")
        print()

def demo_optimized_functionality():
    """演示SM2优化功能"""
    print("SM2 Optimized Functionality Demo")
    print("=" * 50)
    
    # 创建优化版本的SM2实例
    sm2 = SM2Optimized()
    
    # 生成密钥对
    print("1. Optimized Key Generation")
    print("-" * 30)
    start_time = time.time()
    private_key, public_key = sm2.generate_keypair()
    keygen_time = time.time() - start_time
    
    print(f"Private Key: {hex(private_key)}")
    print(f"Public Key: {public_key}")
    print(f"Key Generation Time: {keygen_time:.4f} seconds")
    print()
    
    # 点乘法算法比较
    print("2. Point Multiplication Algorithms Comparison")
    print("-" * 45)
    
    test_scalar = random.randint(1, sm2.n - 1)
    print(f"Test scalar bit length: {test_scalar.bit_length()}")
    
    algorithms = [
        ("Basic", sm2.point_multiply_basic),
        ("NAF", sm2.point_multiply_naf),
        ("Sliding Window", sm2.point_multiply_sliding_window),
        ("Montgomery Ladder", sm2.point_multiply_montgomery),
        ("Auto-Select", sm2.point_multiply)
    ]
    
    results = {}
    for name, func in algorithms:
        start_time = time.time()
        result = func(test_scalar, sm2.G)
        exec_time = time.time() - start_time
        results[name] = (result, exec_time)
        print(f"{name:16}: {exec_time:.4f} seconds")
    
    # 验证所有算法结果一致
    first_result = list(results.values())[0][0]
    all_match = all(result[0] == first_result for result in results.values())
    print(f"All algorithms produce same result: {'YES' if all_match else 'NO'}")
    print()
    
    # 同时点乘法演示
    print("3. Simultaneous Point Multiplication")
    print("-" * 35)
    
    k1 = random.randint(1, sm2.n - 1)
    k2 = random.randint(1, sm2.n - 1)
    P1 = sm2.G
    P2 = public_key
    
    # 分别计算
    start_time = time.time()
    result1 = sm2.point_multiply(k1, P1)
    result2 = sm2.point_multiply(k2, P2)
    separate_result = sm2.point_add(result1, result2)
    separate_time = time.time() - start_time
    
    # 同时计算
    start_time = time.time()
    simultaneous_result = sm2.simultaneous_point_multiply(k1, P1, k2, P2)
    simultaneous_time = time.time() - start_time
    
    print(f"Separate calculation: {separate_time:.4f} seconds")
    print(f"Simultaneous calculation: {simultaneous_time:.4f} seconds")
    print(f"Speedup: {separate_time / simultaneous_time:.2f}x")
    print(f"Results match: {'YES' if separate_result == simultaneous_result else 'NO'}")
    print()
    
    # 优化的签名验证
    print("4. Optimized Signature Verification")
    print("-" * 35)
    
    message = b"Test message for optimized verification"
    
    # 签名
    start_time = time.time()
    signature = sm2.sign(message, private_key)
    sign_time = time.time() - start_time
    
    # 基础验证
    start_time = time.time()
    basic_valid = sm2.verify(message, signature, public_key)
    basic_verify_time = time.time() - start_time
    
    # 优化验证
    start_time = time.time()
    optimized_valid = sm2.verify_optimized(message, signature, public_key)
    optimized_verify_time = time.time() - start_time
    
    print(f"Signing time: {sign_time:.4f} seconds")
    print(f"Basic verification: {basic_verify_time:.4f} seconds ({'VALID' if basic_valid else 'INVALID'})")
    print(f"Optimized verification: {optimized_verify_time:.4f} seconds ({'VALID' if optimized_valid else 'INVALID'})")
    print(f"Verification speedup: {basic_verify_time / optimized_verify_time:.2f}x")

def performance_comparison():
    """性能对比演示"""
    print("SM2 Performance Comparison")
    print("=" * 50)
    
    # 创建基础版本和优化版本
    sm2_basic = SM2Basic()
    sm2_optimized = SM2Optimized()
    
    # 生成测试数据
    test_scalar = random.randint(1, sm2_basic.n - 1)
    test_point = sm2_basic.G
    test_message = b"Performance test message"
    
    print(f"Test scalar bit length: {test_scalar.bit_length()}")
    print()
    
    # 点乘法性能对比
    print("1. Point Multiplication Performance")
    print("-" * 35)
    
    # 基础版本
    start_time = time.time()
    for _ in range(10):
        result_basic = sm2_basic.point_multiply(test_scalar, test_point)
    basic_time = time.time() - start_time
    
    # 优化版本
    start_time = time.time()
    for _ in range(10):
        result_optimized = sm2_optimized.point_multiply(test_scalar, test_point)
    optimized_time = time.time() - start_time
    
    print(f"Basic (10 iterations): {basic_time:.4f} seconds")
    print(f"Optimized (10 iterations): {optimized_time:.4f} seconds")
    print(f"Speedup: {basic_time / optimized_time:.2f}x")
    print(f"Results match: {'YES' if result_basic == result_optimized else 'NO'}")
    print()
    
    # 密钥生成性能对比
    print("2. Key Generation Performance")
    print("-" * 30)
    
    # 基础版本
    start_time = time.time()
    for _ in range(10):
        private_key_basic, public_key_basic = sm2_basic.generate_keypair()
    basic_keygen_time = time.time() - start_time
    
    # 优化版本
    start_time = time.time()
    for _ in range(10):
        private_key_optimized, public_key_optimized = sm2_optimized.generate_keypair()
    optimized_keygen_time = time.time() - start_time
    
    print(f"Basic (10 iterations): {basic_keygen_time:.4f} seconds")
    print(f"Optimized (10 iterations): {optimized_keygen_time:.4f} seconds")
    print(f"Speedup: {basic_keygen_time / optimized_keygen_time:.2f}x")
    print()
    
    # 签名验证性能对比
    print("3. Signature Verification Performance")
    print("-" * 37)
    
    # 使用相同的密钥对
    private_key, public_key = sm2_basic.generate_keypair()
    signature = sm2_basic.sign(test_message, private_key)
    
    # 基础验证
    start_time = time.time()
    for _ in range(10):
        result_basic = sm2_basic.verify(test_message, signature, public_key)
    basic_verify_time = time.time() - start_time
    
    # 优化验证
    start_time = time.time()
    for _ in range(10):
        result_optimized = sm2_optimized.verify_optimized(test_message, signature, public_key)
    optimized_verify_time = time.time() - start_time
    
    print(f"Basic verification (10 iterations): {basic_verify_time:.4f} seconds")
    print(f"Optimized verification (10 iterations): {optimized_verify_time:.4f} seconds")
    print(f"Speedup: {basic_verify_time / optimized_verify_time:.2f}x")
    print(f"Results match: {'YES' if result_basic == result_optimized else 'NO'}")

def interactive_demo():
    """交互式演示"""
    print("SM2 Interactive Demo")
    print("=" * 30)
    
    sm2 = SM2Optimized()
    
    while True:
        print("\nSelect an option:")
        print("1. Generate new keypair")
        print("2. Encrypt/Decrypt message")
        print("3. Sign/Verify message")
        print("4. Performance test")
        print("5. Exit")
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                print("\nGenerating new keypair...")
                start_time = time.time()
                private_key, public_key = sm2.generate_keypair()
                keygen_time = time.time() - start_time
                
                print(f"Private Key: {hex(private_key)}")
                print(f"Public Key: {public_key}")
                print(f"Generation Time: {keygen_time:.4f} seconds")
                
            elif choice == '2':
                private_key, public_key = sm2.generate_keypair()
                message = input("Enter message to encrypt: ").encode()
                
                print(f"Original message: {message}")
                
                # 加密
                start_time = time.time()
                ciphertext = sm2.encrypt(message, public_key)
                encrypt_time = time.time() - start_time
                
                print(f"Ciphertext length: {len(ciphertext)} bytes")
                print(f"Encryption time: {encrypt_time:.4f} seconds")
                
                # 解密
                start_time = time.time()
                decrypted = sm2.decrypt(ciphertext, private_key)
                decrypt_time = time.time() - start_time
                
                print(f"Decrypted message: {decrypted}")
                print(f"Decryption time: {decrypt_time:.4f} seconds")
                print(f"Verification: {'PASS' if message == decrypted else 'FAIL'}")
                
            elif choice == '3':
                private_key, public_key = sm2.generate_keypair()
                message = input("Enter message to sign: ").encode()
                
                print(f"Message: {message}")
                
                # 签名
                start_time = time.time()
                signature = sm2.sign(message, private_key)
                sign_time = time.time() - start_time
                
                print(f"Signature: r={hex(signature[0])[:20]}...")
                print(f"           s={hex(signature[1])[:20]}...")
                print(f"Signing time: {sign_time:.4f} seconds")
                
                # 验证
                start_time = time.time()
                is_valid = sm2.verify_optimized(message, signature, public_key)
                verify_time = time.time() - start_time
                
                print(f"Verification: {'VALID' if is_valid else 'INVALID'}")
                print(f"Verification time: {verify_time:.4f} seconds")
                
            elif choice == '4':
                print("\nRunning quick performance test...")
                tester = SM2PerformanceTester()
                
                # 快速测试
                pm_results = tester.benchmark_point_multiplication(20)
                print(f"Point multiplication speedup: {pm_results['speedup']:.2f}x")
                
                kg_results = tester.benchmark_key_generation(10)
                print(f"Key generation speedup: {kg_results['speedup']:.2f}x")
                
            elif choice == '5':
                print("Exiting...")
                break
                
            else:
                print("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """主函数"""
    print("SM2 Elliptic Curve Cryptography Implementation")
    print("=" * 55)
    print("Author: AI Assistant")
    print("Description: SM2 implementation with basic and optimized versions")
    print("=" * 55)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'basic':
            demo_basic_functionality()
        elif mode == 'optimized':
            demo_optimized_functionality()
        elif mode == 'performance':
            performance_comparison()
        elif mode == 'interactive':
            interactive_demo()
        elif mode == 'full-test':
            print("Running full performance test suite...")
            tester = SM2PerformanceTester()
            tester.run_all_benchmarks()
            tester.print_results()
            tester.save_results()
        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: basic, optimized, performance, interactive, full-test")
    else:
        print("\nRunning comprehensive demo...")
        print("\n" + "=" * 60)
        demo_basic_functionality()
        
        print("\n" + "=" * 60)
        demo_optimized_functionality()
        
        print("\n" + "=" * 60)
        performance_comparison()
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("Run with 'python main.py interactive' for interactive mode")
        print("Run with 'python main.py full-test' for complete performance analysis")

if __name__ == "__main__":
    main() 