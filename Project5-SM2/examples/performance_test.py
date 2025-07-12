#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SM2性能测试脚本
全面测试基础版本和优化版本的性能差异
"""

import time
import random
import statistics
import json
from typing import List, Dict, Tuple
from src.core.sm2_basic import SM2Basic
from src.core.sm2_optimized import SM2Optimized

class SM2PerformanceTester:
    """SM2性能测试类"""
    
    def __init__(self):
        self.sm2_basic = SM2Basic()
        self.sm2_optimized = SM2Optimized()
        self.test_results = {}
    
    def time_function(self, func, *args, **kwargs) -> Tuple[float, any]:
        """测量函数执行时间"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return end_time - start_time, result
    
    def benchmark_point_multiplication(self, iterations: int = 100) -> Dict:
        """基准测试点乘法"""
        print(f"Benchmarking point multiplication ({iterations} iterations)...")
        
        # 生成测试数据
        test_scalars = [random.randint(1, self.sm2_basic.n - 1) for _ in range(iterations)]
        test_point = self.sm2_basic.G
        
        # 测试基础版本
        basic_times = []
        for scalar in test_scalars:
            exec_time, _ = self.time_function(self.sm2_basic.point_multiply, scalar, test_point)
            basic_times.append(exec_time)
        
        # 测试优化版本
        optimized_times = []
        for scalar in test_scalars:
            exec_time, _ = self.time_function(self.sm2_optimized.point_multiply, scalar, test_point)
            optimized_times.append(exec_time)
        
        # 计算统计数据
        basic_stats = {
            'mean': statistics.mean(basic_times),
            'median': statistics.median(basic_times),
            'min': min(basic_times),
            'max': max(basic_times),
            'std': statistics.stdev(basic_times) if len(basic_times) > 1 else 0
        }
        
        optimized_stats = {
            'mean': statistics.mean(optimized_times),
            'median': statistics.median(optimized_times),
            'min': min(optimized_times),
            'max': max(optimized_times),
            'std': statistics.stdev(optimized_times) if len(optimized_times) > 1 else 0
        }
        
        speedup = basic_stats['mean'] / optimized_stats['mean']
        
        return {
            'basic': basic_stats,
            'optimized': optimized_stats,
            'speedup': speedup,
            'iterations': iterations
        }
    
    def benchmark_different_algorithms(self, iterations: int = 50) -> Dict:
        """基准测试不同的点乘法算法"""
        print(f"Benchmarking different algorithms ({iterations} iterations)...")
        
        test_scalars = [random.randint(1, self.sm2_basic.n - 1) for _ in range(iterations)]
        test_point = self.sm2_basic.G
        
        algorithms = {
            'basic': self.sm2_basic.point_multiply,
            'naf': self.sm2_optimized.point_multiply_naf,
            'sliding_window': self.sm2_optimized.point_multiply_sliding_window,
            'montgomery': self.sm2_optimized.point_multiply_montgomery,
            'optimized_auto': self.sm2_optimized.point_multiply
        }
        
        results = {}
        
        for alg_name, alg_func in algorithms.items():
            times = []
            for scalar in test_scalars:
                exec_time, _ = self.time_function(alg_func, scalar, test_point)
                times.append(exec_time)
            
            results[alg_name] = {
                'mean': statistics.mean(times),
                'median': statistics.median(times),
                'min': min(times),
                'max': max(times),
                'std': statistics.stdev(times) if len(times) > 1 else 0
            }
        
        return results
    
    def benchmark_key_generation(self, iterations: int = 50) -> Dict:
        """基准测试密钥生成"""
        print(f"Benchmarking key generation ({iterations} iterations)...")
        
        # 测试基础版本
        basic_times = []
        for _ in range(iterations):
            exec_time, _ = self.time_function(self.sm2_basic.generate_keypair)
            basic_times.append(exec_time)
        
        # 测试优化版本
        optimized_times = []
        for _ in range(iterations):
            exec_time, _ = self.time_function(self.sm2_optimized.generate_keypair)
            optimized_times.append(exec_time)
        
        basic_stats = {
            'mean': statistics.mean(basic_times),
            'median': statistics.median(basic_times),
            'min': min(basic_times),
            'max': max(basic_times),
            'std': statistics.stdev(basic_times) if len(basic_times) > 1 else 0
        }
        
        optimized_stats = {
            'mean': statistics.mean(optimized_times),
            'median': statistics.median(optimized_times),
            'min': min(optimized_times),
            'max': max(optimized_times),
            'std': statistics.stdev(optimized_times) if len(optimized_times) > 1 else 0
        }
        
        speedup = basic_stats['mean'] / optimized_stats['mean']
        
        return {
            'basic': basic_stats,
            'optimized': optimized_stats,
            'speedup': speedup,
            'iterations': iterations
        }
    
    def benchmark_encryption_decryption(self, iterations: int = 20) -> Dict:
        """基准测试加密解密"""
        print(f"Benchmarking encryption/decryption ({iterations} iterations)...")
        
        # 生成测试数据
        messages = [f"Test message {i}".encode() for i in range(iterations)]
        private_key, public_key = self.sm2_basic.generate_keypair()
        
        # 测试基础版本
        basic_encrypt_times = []
        basic_decrypt_times = []
        ciphertexts_basic = []
        
        for message in messages:
            # 加密
            exec_time, ciphertext = self.time_function(self.sm2_basic.encrypt, message, public_key)
            basic_encrypt_times.append(exec_time)
            ciphertexts_basic.append(ciphertext)
            
            # 解密
            exec_time, _ = self.time_function(self.sm2_basic.decrypt, ciphertext, private_key)
            basic_decrypt_times.append(exec_time)
        
        # 测试优化版本
        optimized_encrypt_times = []
        optimized_decrypt_times = []
        ciphertexts_optimized = []
        
        for message in messages:
            # 加密
            exec_time, ciphertext = self.time_function(self.sm2_optimized.encrypt, message, public_key)
            optimized_encrypt_times.append(exec_time)
            ciphertexts_optimized.append(ciphertext)
            
            # 解密
            exec_time, _ = self.time_function(self.sm2_optimized.decrypt, ciphertext, private_key)
            optimized_decrypt_times.append(exec_time)
        
        return {
            'encryption': {
                'basic': {
                    'mean': statistics.mean(basic_encrypt_times),
                    'median': statistics.median(basic_encrypt_times),
                    'min': min(basic_encrypt_times),
                    'max': max(basic_encrypt_times),
                    'std': statistics.stdev(basic_encrypt_times) if len(basic_encrypt_times) > 1 else 0
                },
                'optimized': {
                    'mean': statistics.mean(optimized_encrypt_times),
                    'median': statistics.median(optimized_encrypt_times),
                    'min': min(optimized_encrypt_times),
                    'max': max(optimized_encrypt_times),
                    'std': statistics.stdev(optimized_encrypt_times) if len(optimized_encrypt_times) > 1 else 0
                },
                'speedup': statistics.mean(basic_encrypt_times) / statistics.mean(optimized_encrypt_times)
            },
            'decryption': {
                'basic': {
                    'mean': statistics.mean(basic_decrypt_times),
                    'median': statistics.median(basic_decrypt_times),
                    'min': min(basic_decrypt_times),
                    'max': max(basic_decrypt_times),
                    'std': statistics.stdev(basic_decrypt_times) if len(basic_decrypt_times) > 1 else 0
                },
                'optimized': {
                    'mean': statistics.mean(optimized_decrypt_times),
                    'median': statistics.median(optimized_decrypt_times),
                    'min': min(optimized_decrypt_times),
                    'max': max(optimized_decrypt_times),
                    'std': statistics.stdev(optimized_decrypt_times) if len(optimized_decrypt_times) > 1 else 0
                },
                'speedup': statistics.mean(basic_decrypt_times) / statistics.mean(optimized_decrypt_times)
            },
            'iterations': iterations
        }
    
    def benchmark_signing_verification(self, iterations: int = 50) -> Dict:
        """基准测试签名验证"""
        print(f"Benchmarking signing/verification ({iterations} iterations)...")
        
        # 生成测试数据
        messages = [f"Test signature message {i}".encode() for i in range(iterations)]
        private_key, public_key = self.sm2_basic.generate_keypair()
        
        # 测试基础版本
        basic_sign_times = []
        basic_verify_times = []
        signatures_basic = []
        
        for message in messages:
            # 签名
            exec_time, signature = self.time_function(self.sm2_basic.sign, message, private_key)
            basic_sign_times.append(exec_time)
            signatures_basic.append(signature)
            
            # 验证
            exec_time, _ = self.time_function(self.sm2_basic.verify, message, signature, public_key)
            basic_verify_times.append(exec_time)
        
        # 测试优化版本
        optimized_sign_times = []
        optimized_verify_times = []
        signatures_optimized = []
        
        for message in messages:
            # 签名
            exec_time, signature = self.time_function(self.sm2_optimized.sign, message, private_key)
            optimized_sign_times.append(exec_time)
            signatures_optimized.append(signature)
            
            # 验证（使用优化的验证函数）
            exec_time, _ = self.time_function(self.sm2_optimized.verify_optimized, message, signature, public_key)
            optimized_verify_times.append(exec_time)
        
        return {
            'signing': {
                'basic': {
                    'mean': statistics.mean(basic_sign_times),
                    'median': statistics.median(basic_sign_times),
                    'min': min(basic_sign_times),
                    'max': max(basic_sign_times),
                    'std': statistics.stdev(basic_sign_times) if len(basic_sign_times) > 1 else 0
                },
                'optimized': {
                    'mean': statistics.mean(optimized_sign_times),
                    'median': statistics.median(optimized_sign_times),
                    'min': min(optimized_sign_times),
                    'max': max(optimized_sign_times),
                    'std': statistics.stdev(optimized_sign_times) if len(optimized_sign_times) > 1 else 0
                },
                'speedup': statistics.mean(basic_sign_times) / statistics.mean(optimized_sign_times)
            },
            'verification': {
                'basic': {
                    'mean': statistics.mean(basic_verify_times),
                    'median': statistics.median(basic_verify_times),
                    'min': min(basic_verify_times),
                    'max': max(basic_verify_times),
                    'std': statistics.stdev(basic_verify_times) if len(basic_verify_times) > 1 else 0
                },
                'optimized': {
                    'mean': statistics.mean(optimized_verify_times),
                    'median': statistics.median(optimized_verify_times),
                    'min': min(optimized_verify_times),
                    'max': max(optimized_verify_times),
                    'std': statistics.stdev(optimized_verify_times) if len(optimized_verify_times) > 1 else 0
                },
                'speedup': statistics.mean(basic_verify_times) / statistics.mean(optimized_verify_times)
            },
            'iterations': iterations
        }
    
    def benchmark_simultaneous_multiplication(self, iterations: int = 50) -> Dict:
        """基准测试同时点乘法"""
        print(f"Benchmarking simultaneous multiplication ({iterations} iterations)...")
        
        # 生成测试数据
        test_data = []
        for _ in range(iterations):
            k1 = random.randint(1, self.sm2_basic.n - 1)
            k2 = random.randint(1, self.sm2_basic.n - 1)
            P1 = self.sm2_basic.G
            _, P2 = self.sm2_basic.generate_keypair()
            test_data.append((k1, P1, k2, P2))
        
        # 测试分离计算
        separate_times = []
        for k1, P1, k2, P2 in test_data:
            def separate_multiply():
                result1 = self.sm2_optimized.point_multiply(k1, P1)
                result2 = self.sm2_optimized.point_multiply(k2, P2)
                return self.sm2_optimized.point_add(result1, result2)
            
            exec_time, _ = self.time_function(separate_multiply)
            separate_times.append(exec_time)
        
        # 测试同时计算
        simultaneous_times = []
        for k1, P1, k2, P2 in test_data:
            exec_time, _ = self.time_function(self.sm2_optimized.simultaneous_point_multiply, k1, P1, k2, P2)
            simultaneous_times.append(exec_time)
        
        separate_stats = {
            'mean': statistics.mean(separate_times),
            'median': statistics.median(separate_times),
            'min': min(separate_times),
            'max': max(separate_times),
            'std': statistics.stdev(separate_times) if len(separate_times) > 1 else 0
        }
        
        simultaneous_stats = {
            'mean': statistics.mean(simultaneous_times),
            'median': statistics.median(simultaneous_times),
            'min': min(simultaneous_times),
            'max': max(simultaneous_times),
            'std': statistics.stdev(simultaneous_times) if len(simultaneous_times) > 1 else 0
        }
        
        speedup = separate_stats['mean'] / simultaneous_stats['mean']
        
        return {
            'separate': separate_stats,
            'simultaneous': simultaneous_stats,
            'speedup': speedup,
            'iterations': iterations
        }
    
    def run_all_benchmarks(self) -> Dict:
        """运行所有基准测试"""
        print("SM2 Performance Benchmark Suite")
        print("=" * 50)
        
        results = {}
        
        # 点乘法基准测试
        results['point_multiplication'] = self.benchmark_point_multiplication(100)
        
        # 不同算法基准测试
        results['algorithm_comparison'] = self.benchmark_different_algorithms(50)
        
        # 密钥生成基准测试
        results['key_generation'] = self.benchmark_key_generation(50)
        
        # 加密解密基准测试
        results['encryption_decryption'] = self.benchmark_encryption_decryption(20)
        
        # 签名验证基准测试
        results['signing_verification'] = self.benchmark_signing_verification(50)
        
        # 同时点乘法基准测试
        results['simultaneous_multiplication'] = self.benchmark_simultaneous_multiplication(50)
        
        self.test_results = results
        return results
    
    def print_results(self):
        """打印测试结果"""
        if not self.test_results:
            print("No test results available. Run benchmarks first.")
            return
        
        print("\n" + "=" * 60)
        print("PERFORMANCE BENCHMARK RESULTS")
        print("=" * 60)
        
        # 点乘法结果
        pm_results = self.test_results['point_multiplication']
        print(f"\n1. Point Multiplication ({pm_results['iterations']} iterations):")
        print(f"   Basic:     {pm_results['basic']['mean']:.4f}s (±{pm_results['basic']['std']:.4f})")
        print(f"   Optimized: {pm_results['optimized']['mean']:.4f}s (±{pm_results['optimized']['std']:.4f})")
        print(f"   Speedup:   {pm_results['speedup']:.2f}x")
        
        # 算法比较结果
        alg_results = self.test_results['algorithm_comparison']
        print(f"\n2. Algorithm Comparison:")
        for alg_name, stats in alg_results.items():
            print(f"   {alg_name:15}: {stats['mean']:.4f}s (±{stats['std']:.4f})")
        
        # 密钥生成结果
        kg_results = self.test_results['key_generation']
        print(f"\n3. Key Generation ({kg_results['iterations']} iterations):")
        print(f"   Basic:     {kg_results['basic']['mean']:.4f}s (±{kg_results['basic']['std']:.4f})")
        print(f"   Optimized: {kg_results['optimized']['mean']:.4f}s (±{kg_results['optimized']['std']:.4f})")
        print(f"   Speedup:   {kg_results['speedup']:.2f}x")
        
        # 加密解密结果
        ed_results = self.test_results['encryption_decryption']
        print(f"\n4. Encryption/Decryption ({ed_results['iterations']} iterations):")
        print(f"   Encryption:")
        print(f"     Basic:     {ed_results['encryption']['basic']['mean']:.4f}s")
        print(f"     Optimized: {ed_results['encryption']['optimized']['mean']:.4f}s")
        print(f"     Speedup:   {ed_results['encryption']['speedup']:.2f}x")
        print(f"   Decryption:")
        print(f"     Basic:     {ed_results['decryption']['basic']['mean']:.4f}s")
        print(f"     Optimized: {ed_results['decryption']['optimized']['mean']:.4f}s")
        print(f"     Speedup:   {ed_results['decryption']['speedup']:.2f}x")
        
        # 签名验证结果
        sv_results = self.test_results['signing_verification']
        print(f"\n5. Signing/Verification ({sv_results['iterations']} iterations):")
        print(f"   Signing:")
        print(f"     Basic:     {sv_results['signing']['basic']['mean']:.4f}s")
        print(f"     Optimized: {sv_results['signing']['optimized']['mean']:.4f}s")
        print(f"     Speedup:   {sv_results['signing']['speedup']:.2f}x")
        print(f"   Verification:")
        print(f"     Basic:     {sv_results['verification']['basic']['mean']:.4f}s")
        print(f"     Optimized: {sv_results['verification']['optimized']['mean']:.4f}s")
        print(f"     Speedup:   {sv_results['verification']['speedup']:.2f}x")
        
        # 同时点乘法结果
        sm_results = self.test_results['simultaneous_multiplication']
        print(f"\n6. Simultaneous Multiplication ({sm_results['iterations']} iterations):")
        print(f"   Separate:     {sm_results['separate']['mean']:.4f}s (±{sm_results['separate']['std']:.4f})")
        print(f"   Simultaneous: {sm_results['simultaneous']['mean']:.4f}s (±{sm_results['simultaneous']['std']:.4f})")
        print(f"   Speedup:      {sm_results['speedup']:.2f}x")
    
    def save_results(self, filename: str = "sm2_performance_results.json"):
        """保存测试结果到文件"""
        if not self.test_results:
            print("No test results to save.")
            return
        
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"Results saved to {filename}")

def main():
    """主函数"""
    print("SM2 Performance Testing Suite")
    print("=" * 40)
    
    # 创建测试器
    tester = SM2PerformanceTester()
    
    # 运行所有基准测试
    tester.run_all_benchmarks()
    
    # 打印结果
    tester.print_results()
    
    # 保存结果
    tester.save_results("Project5-SM2/sm2_performance_results.json")

if __name__ == "__main__":
    main() 