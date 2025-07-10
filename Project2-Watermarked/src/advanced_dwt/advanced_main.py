# -*- coding: utf-8 -*-
"""
高级数字水印系统演示程序
基于 DWT-DCT-SVD 算法
山东大学网络空间安全学院
Advanced Digital Watermark System Demo
"""

import os
import sys
import time
import json
from datetime import datetime

from advanced_dwt.advanced_watermark_system import AdvancedWatermarkSystem
from advanced_dwt.advanced_robustness_test import AdvancedRobustnessTest
from basic_lsb.watermark_system import WatermarkSystem  # 导入LSB系统用于对比
from basic_lsb.robustness_test import RobustnessTest  # 导入LSB测试用于对比

def create_output_dirs():
    """创建输出目录"""
    dirs = [
        "output/advanced",
        "output/advanced/watermarked",
        "output/advanced/extracted", 
        "output/advanced/robustness_test",
        "output/advanced/reports",
        "output/advanced/comparison",
        "output/advanced/visualization"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("高级水印系统目录创建完成")

def demonstrate_invisibility(original_path, watermarked_path, output_dir):
    """演示水印的不可见性"""
    print("\n 水印不可见性演示...")
    
    # 创建高级水印系统实例
    advanced_system = AdvancedWatermarkSystem()
    
    # 创建差异图像
    diff_path = os.path.join(output_dir, "difference_amplified.png")
    diff_result = advanced_system.create_difference_image(
        original_path, 
        watermarked_path, 
        diff_path, 
        amplify=20  # 放大20倍以显示差异
    )
    
    if diff_result:
        print(f" 差异图像（放大20倍）已生成: {diff_result}")
    
    # 计算PSNR值
    psnr = advanced_system.calculate_psnr(original_path, watermarked_path)
    print(f" 图像质量 PSNR: {psnr:.2f} dB")
    
    if psnr > 40:
        print(" 优秀的图像质量！水印肉眼不可见")
    elif psnr > 30:
        print(" 良好的图像质量，水印基本不可见")
    else:
        print(" 图像质量一般，水印可能轻微可见")
    
    return diff_result, psnr

def run_algorithm_comparison():
    """运行LSB vs DWT-DCT-SVD算法对比"""
    print("\n" + "="*70)
    print(" 算法对比：LSB vs DWT-DCT-SVD")
    print("="*70)
    
    # 设置文件路径
    original_image = "images/original.png"
    text_watermark = "山东大学网络空间安全学院"
    
    # 初始化两个系统
    lsb_system = WatermarkSystem()
    advanced_system = AdvancedWatermarkSystem()
    
    # LSB 水印嵌入
    print("\n1. LSB算法测试...")
    lsb_watermarked = "output/advanced/comparison/lsb_watermarked.png"
    lsb_result = lsb_system.embed_text_watermark(
        original_image, 
        text_watermark, 
        lsb_watermarked
    )
    
    if lsb_result:
        lsb_psnr = lsb_system.calculate_psnr(original_image, lsb_watermarked)
        print(f" LSB 嵌入成功，PSNR: {lsb_psnr:.2f} dB")
    else:
        print(" LSB 嵌入失败")
        lsb_psnr = 0
    
    # DWT-DCT-SVD 水印嵌入
    print("\n2. DWT-DCT-SVD算法测试...")
    advanced_watermarked = "output/advanced/comparison/advanced_watermarked.png"
    advanced_result, advanced_psnr = advanced_system.embed_text_watermark(
        original_image,
        text_watermark,
        advanced_watermarked
    )
    
    comparison_results = {
        "lsb": {
            "psnr": lsb_psnr,
            "watermarked_path": lsb_watermarked if lsb_result else None,
            "success": lsb_result is not None
        },
        "advanced": {
            "psnr": advanced_psnr,
            "watermarked_path": advanced_watermarked if advanced_result else None,
            "success": advanced_result is not None
        }
    }
    
    # 对比总结
    print("\n 算法对比总结:")
    print(f"  LSB算法 PSNR: {lsb_psnr:.2f} dB")
    print(f"  DWT-DCT-SVD PSNR: {advanced_psnr:.2f} dB")
    
    if advanced_psnr > lsb_psnr:
        print("   DWT-DCT-SVD 在图像质量方面表现更好")
    elif lsb_psnr > advanced_psnr:
        print("   LSB 在图像质量方面表现更好")
    else:
        print("   两种算法图像质量相近")
    
    return comparison_results

def main():
    """主程序"""
    print("="*70)
    print(" 高级数字水印系统演示程序")
    print("基于 DWT-DCT-SVD 算法 (blind-watermark)")
    print("山东大学网络空间安全学院")
    print("Advanced Digital Watermark System Demo")
    print("="*70)
    
    # 创建输出目录
    create_output_dirs()
    
    # 设置文件路径
    original_image = "images/original.png"
    watermark_image = "images/water.png"
    text_watermark = "山东大学网络空间安全学院"
    
    # 检查输入文件
    if not os.path.exists(original_image):
        print(f" 错误：找不到原始图片 {original_image}")
        return
    
    print(f" 原始图片：{original_image}")
    print(f"  水印图片：{watermark_image}")
    print(f" 文本水印：{text_watermark}")
    
    # 初始化高级水印系统
    advanced_system = AdvancedWatermarkSystem()
    advanced_test = AdvancedRobustnessTest(advanced_system)
    
    # 1. 文本水印嵌入（DWT-DCT-SVD）
    print("\n1. DWT-DCT-SVD 文本水印嵌入...")
    text_watermarked_path = "output/advanced/watermarked/text_watermarked_advanced.png"
    
    result, psnr = advanced_system.embed_text_watermark(
        original_image,
        text_watermark,
        text_watermarked_path,
        password_wm=1,
        password_img=1
    )
    
    if result:
        print(f" 高级文本水印嵌入成功！PSNR值: {psnr:.2f} dB")
        
        # 演示水印不可见性
        demonstrate_invisibility(
            original_image, 
            text_watermarked_path, 
            "output/advanced/visualization"
        )
        
    else:
        print(" 高级文本水印嵌入失败")
        return
    
    # 2. 图片水印嵌入（如果水印图片存在）
    if os.path.exists(watermark_image):
        print("\n2. DWT-DCT-SVD 图片水印嵌入...")
        image_watermarked_path = "output/advanced/watermarked/image_watermarked_advanced.png"
        
        img_result, img_psnr = advanced_system.embed_image_watermark(
            original_image,
            watermark_image,
            image_watermarked_path,
            password_wm=2,
            password_img=2
        )
        
        if img_result:
            print(f" 高级图片水印嵌入成功！PSNR值: {img_psnr:.2f} dB")
        else:
            print(" 高级图片水印嵌入失败")
    
    # 3. 水印提取验证
    print("\n3. 水印提取验证...")
    extracted_wm_path = "output/advanced/extracted/extracted_text_watermark.png"
    
    extracted_result = advanced_system.extract_watermark(
        text_watermarked_path,
        extracted_wm_path,
        password_wm=1,
        password_img=1,
        wm_shape=(100, 200)  # 指定水印尺寸
    )
    
    if extracted_result:
        print(f" 水印提取成功！保存至: {extracted_result}")
    else:
        print(" 水印提取失败")
    
    # 4. 鲁棒性测试
    print("\n4. 高级鲁棒性测试...")
    test_results, success_rate = advanced_test.run_comprehensive_tests(
        text_watermarked_path,
        "output/advanced/robustness_test",
        password_wm=1,
        password_img=1,
        wm_shape=(100, 200)
    )
    
    # 5. 算法对比
    comparison_results = run_algorithm_comparison()
    
    # 6. 生成报告
    print("\n5. 生成测试报告...")
    generate_advanced_report(test_results, success_rate, comparison_results, text_watermark)
    
    # 完成总结
    print("\n 高级数字水印系统演示完成！")
    print("\n 主要输出文件：")
    print(f"    含水印图片: {text_watermarked_path}")
    print(f"   提取的水印: {extracted_result}")
    print(f"  🧪 鲁棒性测试: output/advanced/robustness_test/")
    print(f"   测试报告: output/advanced/reports/")
    print(f"   算法对比: output/advanced/comparison/")
    print(f"   可视化结果: output/advanced/visualization/")
    
    print(f"\n DWT-DCT-SVD算法鲁棒性测试成功率: {success_rate:.1%}")
    
    if success_rate > 0.7:
        print(" 优秀的鲁棒性表现！")
    elif success_rate > 0.5:
        print(" 良好的鲁棒性表现")
    elif success_rate > 0.3:
        print(" 中等的鲁棒性表现")
    else:
        print(" 需要进一步优化鲁棒性")

def generate_advanced_report(test_results, success_rate, comparison_results, original_text):
    """生成高级测试报告"""
    
    # 生成详细文本报告
    report_path = "output/advanced/reports/advanced_robustness_report.txt"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("高级数字水印系统测试报告\n")
            f.write("基于 DWT-DCT-SVD 算法\n")
            f.write("="*60 + "\n")
            f.write(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"原始水印文本：{original_text}\n")
            f.write(f"使用算法：DWT-DCT-SVD (blind-watermark)\n")
            f.write(f"总测试数：{len(test_results)}\n")
            
            successful_tests = sum(1 for result in test_results.values() if result.get('success', False))
            f.write(f"成功测试数：{successful_tests}\n")
            f.write(f"成功率：{success_rate:.1%}\n\n")
            
            # 算法对比部分
            f.write("算法对比结果：\n")
            f.write("-" * 40 + "\n")
            lsb_psnr = comparison_results.get('lsb', {}).get('psnr', 0)
            advanced_psnr = comparison_results.get('advanced', {}).get('psnr', 0)
            f.write(f"LSB算法 PSNR: {lsb_psnr:.2f} dB\n")
            f.write(f"DWT-DCT-SVD算法 PSNR: {advanced_psnr:.2f} dB\n\n")
            
            # 详细测试结果
            f.write("详细鲁棒性测试结果：\n")
            f.write("-" * 50 + "\n")
            
            for test_name, result in test_results.items():
                f.write(f"\n测试名称：{test_name}\n")
                f.write(f"结果：{result.get('status', '未知')}\n")
                
                if 'error' in result:
                    f.write(f"错误信息：{result['error']}\n")
                    
                if result.get('extracted_path'):
                    f.write(f"提取水印路径：{result['extracted_path']}\n")
        
        print(f" 详细报告生成完成: {report_path}")
        
    except Exception as e:
        print(f" 生成报告失败: {e}")
    
    # 生成JSON报告
    json_report_path = "output/advanced/reports/advanced_robustness_report.json"
    
    try:
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "algorithm": "DWT-DCT-SVD",
            "original_text": original_text,
            "summary": {
                "total_tests": len(test_results),
                "successful_tests": successful_tests,
                "success_rate": success_rate
            },
            "algorithm_comparison": comparison_results,
            "detailed_results": test_results
        }
        
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f" JSON报告生成完成: {json_report_path}")
        
    except Exception as e:
        print(f" 生成JSON报告失败: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  程序被用户中断")
    except Exception as e:
        print(f"\n 程序运行出错: {e}")
        import traceback
        traceback.print_exc() 