# -*- coding: utf-8 -*-
"""
数字水印系统主程序
山东大学网络空间安全学院
Digital Watermark System Main Program
"""

import os
import sys
import time
import json
from datetime import datetime

from basic_lsb.watermark_system import WatermarkSystem
from basic_lsb.robustness_test import RobustnessTest

def create_output_dirs():
    """创建输出目录"""
    dirs = [
        "output",
        "output/watermarked",
        "output/extracted", 
        "output/robustness_test",
        "output/reports"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("输出目录创建完成")

def main():
    """主程序"""
    print("="*60)
    print("数字水印系统演示程序")
    print("山东大学网络空间安全学院")
    print("Digital Watermark System Demo")
    print("="*60)
    
    # 创建输出目录
    create_output_dirs()
    
    # 初始化系统
    watermark_system = WatermarkSystem()
    robustness_test = RobustnessTest(watermark_system)
    
    # 设置文件路径
    original_image = "images/original.png"
    watermark_image = "images/water.png"
    text_watermark = "山东大学网络空间安全学院"
    
    # 检查输入文件
    if not os.path.exists(original_image):
        print(f"错误：找不到原始图片 {original_image}")
        return
    
    if not os.path.exists(watermark_image):
        print(f"错误：找不到水印图片 {watermark_image}")
        return
    
    print(f"原始图片：{original_image}")
    print(f"水印图片：{watermark_image}")
    print(f"文本水印：{text_watermark}")
    print()
    
    # 1. 文本水印嵌入
    print("1. 文本水印嵌入中...")
    text_watermarked_path = "output/watermarked/text_watermarked.png"
    try:
        result = watermark_system.embed_text_watermark(
            original_image, 
            text_watermark, 
            text_watermarked_path
        )
        
        if result:
            # 计算PSNR
            psnr = watermark_system.calculate_psnr(original_image, text_watermarked_path)
            print(f"文本水印嵌入成功！PSNR值: {psnr:.2f} dB")
        else:
            print("文本水印嵌入失败")
            return
        
    except Exception as e:
        print(f"文本水印嵌入失败：{str(e)}")
        return
    
    print()
    
    # 2. 图片水印嵌入
    print("2. 图片水印嵌入中...")
    image_watermarked_path = "output/watermarked/image_watermarked.png"
    try:
        result = watermark_system.embed_image_watermark(
            original_image,
            watermark_image,
            image_watermarked_path,
            alpha=0.3
        )
        
        if result:
            # 计算PSNR
            psnr = watermark_system.calculate_psnr(original_image, image_watermarked_path)
            print(f"图片水印嵌入成功！PSNR值: {psnr:.2f} dB")
        else:
            print("图片水印嵌入失败")
            return
        
    except Exception as e:
        print(f"图片水印嵌入失败：{str(e)}")
        return
    
    print()
    
    # 3. 水印提取测试
    print("3. 水印提取测试中...")
    
    # 从文本水印图片中提取
    extracted_text = watermark_system.extract_text_watermark(text_watermarked_path)
    
    # 安全地显示提取的文本
    if extracted_text:
        # 只显示安全的字符
        safe_extracted = ''.join(c for c in extracted_text if c.isprintable())
        print(f"提取的文本: {safe_extracted[:100]}{'...' if len(safe_extracted) > 100 else ''}")
        
        # 验证提取结果
        if text_watermark in extracted_text:
            print("文本水印提取成功！")
        else:
            print("文本水印提取部分成功（包含部分原始内容）")
    else:
        print("文本水印提取失败")
    
    print()
    
    # 4. 鲁棒性测试
    print("4. 鲁棒性测试中...")
    print("对含有文本水印的图片进行各种攻击测试...")
    
    test_results = robustness_test.run_all_tests(
        text_watermarked_path,
        "output/robustness_test",
        text_watermark
    )
    
    # 5. 生成测试报告
    print("\n5. 生成测试报告中...")
    generate_report(test_results, text_watermark)
    
    print("\n演示完成！")
    print("请查看 output 文件夹中的结果文件")
    print("\n主要文件：")
    print(f"  - 文本水印图片: {text_watermarked_path}")
    print(f"  - 图片水印图片: {image_watermarked_path}")
    print("  - 鲁棒性测试结果: output/robustness_test/")
    print("  - 测试报告: output/reports/")

def generate_report(test_results, original_text):
    """生成测试报告"""
    
    # 统计结果
    total_tests = len(test_results)
    successful_tests = sum(1 for result in test_results.values() if result.get('success', False))
    success_rate = successful_tests / total_tests if total_tests > 0 else 0
    
    # 生成文本报告
    report_path = "output/reports/robustness_report.txt"
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("数字水印鲁棒性测试报告\n")
            f.write("="*50 + "\n")
            f.write(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"原始水印文本：{original_text}\n")
            f.write(f"总测试数：{total_tests}\n")
            f.write(f"成功测试数：{successful_tests}\n")
            f.write(f"成功率：{success_rate:.2%}\n\n")
            
            f.write("详细测试结果：\n")
            f.write("-" * 50 + "\n")
            
            for test_name, result in test_results.items():
                f.write(f"\n测试名称：{test_name}\n")
                f.write(f"结果：{'成功' if result.get('success', False) else '失败'}\n")
                f.write(f"准确率：{result.get('accuracy', 0):.2%}\n")
                
                extracted_text = result.get('extracted_text', '')
                if extracted_text:
                    f.write(f"提取文本片段：{extracted_text}\n")
                
                if 'error' in result:
                    f.write(f"错误信息：{result['error']}\n")
    except Exception as e:
        print(f"生成文本报告失败: {e}")
    
    # 生成JSON报告
    json_report_path = "output/reports/robustness_report.json"
    try:
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "original_text": original_text,
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": success_rate
            },
            "detailed_results": test_results
        }
        
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"生成JSON报告失败: {e}")
    
    print(f"报告生成完成")
    print(f"   文本报告：{report_path}")
    print(f"   JSON报告：{json_report_path}")
    print(f"   总体成功率：{success_rate:.2%} ({successful_tests}/{total_tests})")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback
        traceback.print_exc() 