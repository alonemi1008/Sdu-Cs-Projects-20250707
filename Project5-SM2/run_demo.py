#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SM2演示运行脚本
提供简单的菜单界面来运行不同的演示
"""

import sys
import os

def print_menu():
    """打印菜单"""
    print("SM2 Elliptic Curve Cryptography Demo")
    print("=" * 40)
    print("1. Basic functionality demo")
    print("2. Optimized functionality demo")
    print("3. Performance comparison")
    print("4. Interactive demo")
    print("5. Full performance test")
    print("6. Quick test")
    print("7. Signature protocol demo")
    print("8. Key exchange protocol demo")
    print("9. Comprehensive protocols demo")
    print("10. Protocol tests")
    print("11. Exit")
    print("=" * 40)

def run_demo():
    """运行演示"""
    while True:
        print_menu()
        
        try:
            choice = input("Select option (1-11): ").strip()
            
            if choice == '1':
                print("Running basic functionality demo...")
                os.system("python main.py basic")
                
            elif choice == '2':
                print("Running optimized functionality demo...")
                os.system("python main.py optimized")
                
            elif choice == '3':
                print("Running performance comparison...")
                os.system("python main.py performance")
                
            elif choice == '4':
                print("Starting interactive demo...")
                os.system("python main.py interactive")
                
            elif choice == '5':
                print("Running full performance test...")
                os.system("python main.py full-test")
                
            elif choice == '6':
                print("Running quick test...")
                os.system("python tests/test_sm2.py")
                
            elif choice == '7':
                print("Running signature protocol demo...")
                os.system("python main.py signature")
                
            elif choice == '8':
                print("Running key exchange protocol demo...")
                os.system("python main.py keyexchange")
                
            elif choice == '9':
                print("Running comprehensive protocols demo...")
                os.system("python main.py protocols")
                
            elif choice == '10':
                print("Protocol tests have been integrated into main tests")
                
            elif choice == '11':
                print("Goodbye!")
                break
                
            else:
                print("Invalid choice. Please try again.")
                
            input("\nPress Enter to continue...")
            print("\n" + "=" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """主函数"""
    print("SM2 Demo Launcher")
    print("Checking Python version...")
    
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required.")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    print("All dependencies satisfied.")
    print()
    
    # 检查文件是否存在
    required_files = [
        'src/core/sm2_basic.py',
        'src/core/sm2_optimized.py',
        'main.py',
        'tests/test_sm2.py',
        'examples/performance_test.py',
        'src/protocols/sm2_signature_protocol.py',
        'src/protocols/sm2_key_exchange.py',
        'examples/sm2_protocols_demo.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("Error: Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        sys.exit(1)
    
    print("All required files found.")
    print()
    
    run_demo()

if __name__ == "__main__":
    main() 