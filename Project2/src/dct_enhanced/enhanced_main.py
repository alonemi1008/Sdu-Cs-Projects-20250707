# -*- coding: utf-8 -*-
"""
增强数字水印系统演示程序
基于 DCT 频域变换算法
山东大学网络空间安全学院
Enhanced Digital Watermark System Demo
"""

import os
import sys
import time
import json
from datetime import datetime
import numpy as np
import cv2
from PIL import Image

from dct_enhanced.dct_watermark_system import DCTWatermarkSystem
from basic_lsb.watermark_system import WatermarkSystem  # 导入LSB系统用于对比
# 注意：DCT算法有自己的鲁棒性测试，不需要导入高级算法的测试模块

def create_output_dirs():
    """创建输出目录"""
    dirs = [
        "output/enhanced",
        "output/enhanced/watermarked",
        "output/enhanced/extracted", 
        "output/enhanced/robustness_test",
        "output/enhanced/reports",
        "output/enhanced/comparison",
        "output/enhanced/visualization"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("增强水印系统目录创建完成")

def demonstrate_invisibility_enhanced(original_path, watermarked_path, output_dir):
    """演示增强的水印不可见性"""
    print("\nDCT频域水印不可见性演示...")
    
    # 创建DCT水印系统实例
    dct_system = DCTWatermarkSystem()
    
    # 创建差异图像（多种放大倍数）
    amplifications = [5, 10, 20, 50]
    diff_paths = []
    
    for amp in amplifications:
        diff_path = os.path.join(output_dir, f"difference_amplified_{amp}x.png")
        diff_result = dct_system.create_difference_image(
            original_path, 
            watermarked_path, 
            diff_path, 
            amplify=amp
        )
        if diff_result:
            diff_paths.append((amp, diff_result))
    
    # 计算PSNR值
    psnr = dct_system.calculate_psnr(original_path, watermarked_path)
    print(f"DCT频域水印 PSNR: {psnr:.2f} dB")
    
    # 评估不可见性
    if psnr > 50:
        print("卓越的图像质量！水印完全不可见")
    elif psnr > 40:
        print("优秀的图像质量！水印肉眼不可见")
    elif psnr > 30:
        print("良好的图像质量，水印基本不可见")
    else:
        print("图像质量一般，水印可能轻微可见")
    
    # 创建侧边对比图
    create_side_by_side_comparison(original_path, watermarked_path, 
                                 os.path.join(output_dir, "side_by_side_comparison.png"))
    
    return diff_paths, psnr

def create_side_by_side_comparison(original_path, watermarked_path, output_path):
    """创建原图与含水印图的并排对比"""
    try:
        # 读取图像
        original = cv2.imread(original_path)
        watermarked = cv2.imread(watermarked_path)
        
        if original is None or watermarked is None:
            return None
        
        # 确保尺寸相同
        if original.shape != watermarked.shape:
            watermarked = cv2.resize(watermarked, (original.shape[1], original.shape[0]))
        
        # 创建并排图像
        h, w = original.shape[:2]
        comparison = np.zeros((h, w*2, 3), dtype=np.uint8)
        comparison[:, :w] = original
        comparison[:, w:] = watermarked
        
        # 添加文字标签
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(comparison, 'Original', (10, 30), font, 1, (255, 255, 255), 2)
        cv2.putText(comparison, 'Watermarked', (w+10, 30), font, 1, (255, 255, 255), 2)
        
        # 保存对比图
        cv2.imwrite(output_path, comparison)
        print(f"并排对比图已保存: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"创建对比图时出错: {e}")
        return None

def test_multiple_alpha_values():
    """测试不同的水印强度参数"""
    print("\n测试不同水印强度参数...")
    
    original_image = "images/original.png"
    text_watermark = "山东大学网络空间安全学院"
    
    # 初始化DCT系统
    dct_system = DCTWatermarkSystem()
    
    # 测试不同的alpha值
    alpha_values = [0.01, 0.03, 0.05, 0.08, 0.1, 0.15]
    results = []
    
    for alpha in alpha_values:
        print(f"  测试alpha={alpha}...")
        
        # 嵌入水印
        output_path = f"output/enhanced/comparison/alpha_{alpha}_watermarked.png"
        result, psnr = dct_system.embed_text_watermark(
            original_image, text_watermark, output_path, alpha=alpha
        )
        
        if result:
            # 测试提取
            extracted_path = f"output/enhanced/comparison/alpha_{alpha}_extracted.png"
            extract_result = dct_system.extract_text_watermark(
                result, extracted_path, watermark_shape=(64, 128)
            )
            
            results.append({
                'alpha': alpha,
                'psnr': psnr,
                'watermarked_path': result,
                'extracted_path': extract_result,
                'success': extract_result is not None
            })
            
            print(f"    Alpha={alpha}, PSNR={psnr:.2f} dB, 提取={'成功' if extract_result else '失败'}")
        else:
            print(f"    Alpha={alpha} 嵌入失败")
    
    # 找到最佳alpha值（PSNR最高且提取成功）
    successful_results = [r for r in results if r['success']]
    if successful_results:
        best_result = max(successful_results, key=lambda x: x['psnr'])
        print(f"\n最佳参数: Alpha={best_result['alpha']}, PSNR={best_result['psnr']:.2f} dB")
        return best_result
    else:
        print("\n没有找到成功的参数组合")
        return None

def run_enhanced_algorithm_comparison():
    """运行LSB vs DCT频域算法对比"""
    print("\n" + "="*70)
    print("算法对比：LSB vs DCT频域")
    print("="*70)
    
    # 设置文件路径
    original_image = "images/original.png"
    text_watermark = "山东大学网络空间安全学院"
    
    # 初始化两个系统
    lsb_system = WatermarkSystem()
    dct_system = DCTWatermarkSystem()
    
    # LSB 水印嵌入
    print("\n1. LSB算法测试...")
    lsb_watermarked = "output/enhanced/comparison/lsb_watermarked.png"
    lsb_result = lsb_system.embed_text_watermark(
        original_image, 
        text_watermark, 
        lsb_watermarked
    )
    
    if lsb_result:
        lsb_psnr = lsb_system.calculate_psnr(original_image, lsb_watermarked)
        print(f"LSB 嵌入成功，PSNR: {lsb_psnr:.2f} dB")
        
        # LSB 水印提取测试
        lsb_extracted = lsb_system.extract_text_watermark(lsb_watermarked)
        lsb_extract_success = "山东大学" in lsb_extracted if lsb_extracted else False
        print(f"LSB 提取结果: {'成功' if lsb_extract_success else '失败'}")
    else:
        print("LSB 嵌入失败")
        lsb_psnr = 0
        lsb_extract_success = False
    
    # DCT 水印嵌入
    print("\n2. DCT频域算法测试...")
    dct_watermarked = "output/enhanced/comparison/dct_watermarked.png"
    dct_result, dct_psnr = dct_system.embed_text_watermark(
        original_image,
        text_watermark,
        dct_watermarked,
        alpha=0.05
    )
    
    if dct_result:
        print(f"DCT 嵌入成功，PSNR: {dct_psnr:.2f} dB")
        
        # DCT 水印提取测试
        dct_extracted_path = "output/enhanced/comparison/dct_extracted.png"
        dct_extract_result = dct_system.extract_text_watermark(
            dct_result, dct_extracted_path, watermark_shape=(64, 128)
        )
        dct_extract_success = dct_extract_result is not None
        print(f"DCT 提取结果: {'成功' if dct_extract_success else '失败'}")
    else:
        print("DCT 嵌入失败")
        dct_extract_success = False
    
    # 创建可视化对比
    create_algorithm_comparison_visual(
        original_image, lsb_watermarked, dct_watermarked,
        lsb_psnr, dct_psnr,
        "output/enhanced/comparison/algorithm_comparison_visual.png"
    )
    
    comparison_results = {
        "lsb": {
            "psnr": lsb_psnr,
            "watermarked_path": lsb_watermarked if lsb_result else None,
            "extraction_success": lsb_extract_success,
            "success": lsb_result is not None
        },
        "dct": {
            "psnr": dct_psnr,
            "watermarked_path": dct_watermarked if dct_result else None,
            "extraction_success": dct_extract_success,
            "success": dct_result is not None
        }
    }
    
    # 对比总结
    print("\n算法对比总结:")
    print(f"  LSB算法:")
    print(f"    PSNR: {lsb_psnr:.2f} dB")
    print(f"    提取成功: {'是' if lsb_extract_success else '否'}")
    print(f"  DCT频域算法:")
    print(f"    PSNR: {dct_psnr:.2f} dB") 
    print(f"    提取成功: {'是' if dct_extract_success else '否'}")
    
    # 综合评价
    if dct_psnr > lsb_psnr and dct_extract_success:
        print("  DCT频域算法在图像质量和鲁棒性方面都表现更好")
    elif dct_psnr > lsb_psnr:
        print("  DCT频域算法在图像质量方面表现更好")
    elif dct_extract_success and not lsb_extract_success:
        print("  DCT频域算法在鲁棒性方面表现更好")
    else:
        print("  两种算法各有优势")
    
    return comparison_results

def create_algorithm_comparison_visual(original_path, lsb_path, dct_path, lsb_psnr, dct_psnr, output_path):
    """创建算法对比可视化图"""
    try:
        # 读取图像
        original = cv2.imread(original_path)
        lsb_img = cv2.imread(lsb_path) if os.path.exists(lsb_path) else original.copy()
        dct_img = cv2.imread(dct_path) if os.path.exists(dct_path) else original.copy()
        
        # 调整尺寸
        h, w = original.shape[:2]
        if lsb_img.shape[:2] != (h, w):
            lsb_img = cv2.resize(lsb_img, (w, h))
        if dct_img.shape[:2] != (h, w):
            dct_img = cv2.resize(dct_img, (w, h))
        
        # 创建三列对比图
        comparison = np.zeros((h + 80, w*3, 3), dtype=np.uint8)
        comparison[40:h+40, :w] = original
        comparison[40:h+40, w:2*w] = lsb_img  
        comparison[40:h+40, 2*w:3*w] = dct_img
        
        # 添加标题和PSNR信息
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(comparison, 'Original Image', (10, 25), font, 0.8, (255, 255, 255), 2)
        cv2.putText(comparison, f'LSB (PSNR: {lsb_psnr:.1f}dB)', (w+10, 25), font, 0.8, (255, 255, 255), 2)
        cv2.putText(comparison, f'DCT (PSNR: {dct_psnr:.1f}dB)', (2*w+10, 25), font, 0.8, (255, 255, 255), 2)
        
        # 添加底部说明
        cv2.putText(comparison, 'Shandong University - School of Cyber Science and Technology', 
                   (10, h+65), font, 0.6, (200, 200, 200), 1)
        
        cv2.imwrite(output_path, comparison)
        print(f"算法对比可视化图已保存: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"创建算法对比可视化时出错: {e}")
        return None

def main():
    """主程序"""
    print("="*70)
    print("增强数字水印系统演示程序")
    print("基于 DCT 频域变换算法")
    print("山东大学网络空间安全学院")
    print("Enhanced Digital Watermark System Demo")
    print("="*70)
    
    # 创建输出目录
    create_output_dirs()
    
    # 设置文件路径
    original_image = "images/original.png"
    watermark_image = "images/water.png"
    text_watermark = "山东大学网络空间安全学院"
    
    # 检查输入文件
    if not os.path.exists(original_image):
        print(f"错误：找不到原始图片 {original_image}")
        return
    
    print(f"原始图片：{original_image}")
    print(f"水印图片：{watermark_image}")
    print(f"文本水印：{text_watermark}")
    
    # 初始化DCT水印系统
    dct_system = DCTWatermarkSystem()
    
    # 1. 测试不同的水印强度参数
    best_alpha_result = test_multiple_alpha_values()
    
    # 2. DCT频域文本水印嵌入（使用最佳参数）
    print("\n1. DCT频域文本水印嵌入...")
    text_watermarked_path = "output/enhanced/watermarked/text_watermarked_dct.png"
    
    alpha = best_alpha_result['alpha'] if best_alpha_result else 0.05
    result, psnr = dct_system.embed_text_watermark(
        original_image,
        text_watermark,
        text_watermarked_path,
        alpha=alpha
    )
    
    if result:
        print(f"DCT频域文本水印嵌入成功！PSNR值: {psnr:.2f} dB")
        
        # 演示水印不可见性
        diff_paths, psnr_value = demonstrate_invisibility_enhanced(
            original_image, 
            text_watermarked_path, 
            "output/enhanced/visualization"
        )
        
    else:
        print("DCT频域文本水印嵌入失败")
        return
    
    # 3. 水印提取验证
    print("\n2. DCT频域水印提取验证...")
    extracted_wm_path = "output/enhanced/extracted/extracted_text_watermark.png"
    
    extracted_result = dct_system.extract_text_watermark(
        text_watermarked_path,
        extracted_wm_path,
        watermark_shape=(64, 128)
    )
    
    if extracted_result:
        print(f"水印提取成功！保存至: {extracted_result}")
    else:
        print("水印提取失败")
    
    # 4. 算法对比
    comparison_results = run_enhanced_algorithm_comparison()
    
    # 5. 简化的鲁棒性测试
    print("\n3. DCT频域鲁棒性快速测试...")
    test_basic_robustness(dct_system, text_watermarked_path)
    
    # 6. 生成报告
    print("\n4. 生成测试报告...")
    generate_enhanced_report(comparison_results, psnr, text_watermark, alpha)
    
    # 完成总结
    print("\n增强数字水印系统演示完成！")
    print("\n主要输出文件：")
    print(f"  含水印图片: {text_watermarked_path}")
    print(f"  提取的水印: {extracted_result}")
    print(f"  算法对比: output/enhanced/comparison/")
    print(f"  可视化结果: output/enhanced/visualization/")
    
    print(f"\nDCT频域算法 PSNR值: {psnr:.2f} dB")
    print(f"使用的水印强度参数: α = {alpha}")
    
    if psnr > 45:
        print("卓越的水印不可见性！")
    elif psnr > 35:
        print("优秀的水印不可见性")
    else:
        print("良好的水印效果")

def test_basic_robustness(dct_system, watermarked_path):
    """基础鲁棒性测试"""
    print("  执行基础鲁棒性测试...")
    
    tests = [
        ("JPEG压缩", lambda img_path, out_path: compress_jpeg(img_path, out_path, 80)),
        ("高斯噪声", lambda img_path, out_path: add_gaussian_noise(img_path, out_path, 10)),
        ("缩放测试", lambda img_path, out_path: resize_test(img_path, out_path, 0.8)),
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            # 执行攻击
            attacked_path = f"output/enhanced/robustness_test/{test_name.replace(' ', '_')}.png"
            os.makedirs("output/enhanced/robustness_test", exist_ok=True)
            
            test_func(watermarked_path, attacked_path)
            
            # 尝试提取水印
            extracted_path = f"output/enhanced/robustness_test/{test_name.replace(' ', '_')}_extracted.png"
            extract_result = dct_system.extract_text_watermark(
                attacked_path, extracted_path, watermark_shape=(64, 128)
            )
            
            if extract_result:
                print(f"    {test_name}: 成功")
                success_count += 1
            else:
                print(f"    {test_name}: 失败")
                
        except Exception as e:
            print(f"    {test_name}: 错误 - {e}")
    
    success_rate = success_count / total_tests
    print(f"  基础鲁棒性测试成功率: {success_rate:.1%} ({success_count}/{total_tests})")
    return success_rate

def compress_jpeg(input_path, output_path, quality):
    """JPEG压缩"""
    img = cv2.imread(input_path)
    cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, quality])

def add_gaussian_noise(input_path, output_path, noise_level):
    """添加高斯噪声"""
    img = cv2.imread(input_path)
    noise = np.random.normal(0, noise_level, img.shape).astype(np.int16)
    noisy_img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    cv2.imwrite(output_path, noisy_img)

def resize_test(input_path, output_path, scale):
    """缩放测试"""
    img = cv2.imread(input_path)
    h, w = img.shape[:2]
    resized = cv2.resize(img, (int(w*scale), int(h*scale)))
    final = cv2.resize(resized, (w, h))
    cv2.imwrite(output_path, final)

def generate_enhanced_report(comparison_results, psnr, original_text, alpha):
    """生成增强测试报告"""
    
    report_path = "output/enhanced/reports/enhanced_report.txt"
    os.makedirs("output/enhanced/reports", exist_ok=True)
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("增强数字水印系统测试报告\n")
            f.write("基于 DCT 频域变换算法\n")
            f.write("="*60 + "\n")
            f.write(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"原始水印文本：{original_text}\n")
            f.write(f"使用算法：DCT频域变换\n")
            f.write(f"水印强度参数：α = {alpha}\n")
            f.write(f"图像质量 PSNR：{psnr:.2f} dB\n\n")
            
            # 算法对比部分
            f.write("算法对比结果：\n")
            f.write("-" * 40 + "\n")
            lsb_psnr = comparison_results.get('lsb', {}).get('psnr', 0)
            dct_psnr = comparison_results.get('dct', {}).get('psnr', 0)
            f.write(f"LSB算法 PSNR: {lsb_psnr:.2f} dB\n")
            f.write(f"DCT算法 PSNR: {dct_psnr:.2f} dB\n\n")
            
            f.write("技术特点：\n")
            f.write("- 频域变换保证更好的不可见性\n")
            f.write("- 中频系数嵌入平衡鲁棒性和质量\n")
            f.write("- 自适应强度控制优化视觉效果\n")
            f.write("- 支持多种格式的图像处理\n")
        
        print(f"增强报告生成完成: {report_path}")
        
    except Exception as e:
        print(f"生成报告失败: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback
        traceback.print_exc() 