# -*- coding: utf-8 -*-
"""
高级水印系统可视化程序
Advanced Watermark System Visualization
展示DWT-DCT-SVD算法的效果
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np
import os
import json
import cv2
from matplotlib.patches import Rectangle

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class AdvancedWatermarkVisualizer:
    def __init__(self):
        self.fig_size = (16, 12)
    
    def show_invisibility_demonstration(self):
        """展示水印不可见性演示"""
        
        # 检查必要文件
        original_path = "images/original.png"
        watermarked_path = "output/advanced/watermarked/text_watermarked_advanced.png"
        diff_path = "output/advanced/visualization/difference_amplified.png"
        
        if not all(os.path.exists(path) for path in [original_path, watermarked_path]):
            print(" 找不到必要的图像文件，请先运行水印嵌入程序")
            return
        
        # 创建图形
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('DWT-DCT-SVD 水印不可见性演示\n山东大学网络空间安全学院', fontsize=16, fontweight='bold')
        
        # 读取图像
        original = np.array(Image.open(original_path))
        watermarked = np.array(Image.open(watermarked_path))
        
        # 显示原始图像
        axes[0, 0].imshow(original)
        axes[0, 0].set_title('原始图像', fontsize=14)
        axes[0, 0].axis('off')
        
        # 显示含水印图像
        axes[0, 1].imshow(watermarked)
        axes[0, 1].set_title('含水印图像\n(肉眼不可见)', fontsize=14)
        axes[0, 1].axis('off')
        
        # 计算并显示差异图像
        if original.shape == watermarked.shape:
            diff = cv2.absdiff(original, watermarked)
            diff_amplified = np.clip(diff * 20, 0, 255).astype(np.uint8)
            
            axes[0, 2].imshow(diff_amplified)
            axes[0, 2].set_title('差异图像 (放大20倍)', fontsize=14)
            axes[0, 2].axis('off')
        else:
            axes[0, 2].text(0.5, 0.5, '图像尺寸不匹配', ha='center', va='center', transform=axes[0, 2].transAxes)
            axes[0, 2].set_title('差异图像', fontsize=14)
            axes[0, 2].axis('off')
        
        # 显示局部放大对比
        # 选择中心区域
        h, w = original.shape[:2]
        crop_size = min(h, w) // 4
        start_y, start_x = h//2 - crop_size//2, w//2 - crop_size//2
        
        # 原始图像局部
        original_crop = original[start_y:start_y+crop_size, start_x:start_x+crop_size]
        axes[1, 0].imshow(original_crop)
        axes[1, 0].set_title('原始图像 (局部放大)', fontsize=14)
        axes[1, 0].axis('off')
        
        # 含水印图像局部
        watermarked_crop = watermarked[start_y:start_y+crop_size, start_x:start_x+crop_size]
        axes[1, 1].imshow(watermarked_crop)
        axes[1, 1].set_title('含水印图像 (局部放大)', fontsize=14)
        axes[1, 1].axis('off')
        
        # 局部差异
        if original_crop.shape == watermarked_crop.shape:
            local_diff = cv2.absdiff(original_crop, watermarked_crop)
            local_diff_amplified = np.clip(local_diff * 30, 0, 255).astype(np.uint8)
            
            axes[1, 2].imshow(local_diff_amplified)
            axes[1, 2].set_title('局部差异 (放大30倍)', fontsize=14)
            axes[1, 2].axis('off')
        else:
            axes[1, 2].text(0.5, 0.5, '无法计算局部差异', ha='center', va='center', transform=axes[1, 2].transAxes)
            axes[1, 2].set_title('局部差异', fontsize=14)
            axes[1, 2].axis('off')
        
        # 在原始图像上标记放大区域
        rect = Rectangle((start_x, start_y), crop_size, crop_size, 
                        linewidth=3, edgecolor='red', facecolor='none')
        axes[0, 0].add_patch(rect)
        
        # 在含水印图像上标记放大区域
        rect2 = Rectangle((start_x, start_y), crop_size, crop_size, 
                         linewidth=3, edgecolor='red', facecolor='none')
        axes[0, 1].add_patch(rect2)
        
        plt.tight_layout()
        output_path = "output/advanced/visualization/invisibility_demonstration.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f" 不可见性演示图已保存: {output_path}")
        return output_path
    
    def show_robustness_results(self):
        """展示鲁棒性测试结果"""
        
        # 读取测试报告
        report_path = "output/advanced/reports/advanced_robustness_report.json"
        if not os.path.exists(report_path):
            print(" 找不到测试报告文件，请先运行鲁棒性测试")
            return
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
        except:
            print(" 无法读取测试报告")
            return
        
        # 提取测试结果
        results = report_data.get('detailed_results', {})
        success_rate = report_data.get('summary', {}).get('success_rate', 0)
        
        # 创建测试结果可视化
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle(f'DWT-DCT-SVD 鲁棒性测试结果\n总体成功率: {success_rate:.1%}', fontsize=16, fontweight='bold')
        
        # 1. 成功率柱状图
        test_names = []
        success_values = []
        
        for test_name, result in results.items():
            test_names.append(test_name.replace('_', '\n'))
            success_values.append(1 if result.get('success', False) else 0)
        
        # 设置颜色
        colors = ['green' if success else 'red' for success in success_values]
        
        bars = ax1.bar(range(len(test_names)), success_values, color=colors, alpha=0.7)
        ax1.set_xlabel('测试类型', fontsize=12)
        ax1.set_ylabel('成功 (1) / 失败 (0)', fontsize=12)
        ax1.set_title('各测试项成功率', fontsize=14)
        ax1.set_xticks(range(len(test_names)))
        ax1.set_xticklabels(test_names, rotation=45, ha='right', fontsize=10)
        ax1.set_ylim(0, 1.2)
        
        # 在柱子上添加标签
        for i, (bar, success) in enumerate(zip(bars, success_values)):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                    '成功' if success else '失败', ha='center', va='bottom', fontsize=8)
        
        # 2. 测试类别汇总饼图
        test_categories = {
            '几何变换': ['horizontal_flip', 'vertical_flip', 'rotation_15', 'rotation_45'],
            '几何攻击': ['crop_90', 'crop_80', 'resize_75', 'resize_50'],
            '信号处理': ['contrast_150', 'contrast_70', 'brightness_120', 'brightness_80'],
            '噪声攻击': ['gaussian_noise_15', 'gaussian_noise_25', 'salt_pepper_3', 'salt_pepper_5'],
            '压缩滤波': ['jpeg_80', 'jpeg_50', 'gaussian_blur_3', 'gaussian_blur_5', 'median_filter_3', 'median_filter_5']
        }
        
        category_success = {}
        for category, test_list in test_categories.items():
            successful = sum(1 for test in test_list if results.get(test, {}).get('success', False))
            total = len(test_list)
            category_success[category] = successful / total if total > 0 else 0
        
        categories = list(category_success.keys())
        success_rates = list(category_success.values())
        
        # 设置饼图颜色
        pie_colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
        
        wedges, texts, autotexts = ax2.pie(success_rates, labels=categories, autopct='%1.1f%%', 
                                          colors=pie_colors, startangle=90)
        ax2.set_title('各类别测试成功率', fontsize=14)
        
        plt.tight_layout()
        output_path = "output/advanced/visualization/robustness_results.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f" 鲁棒性结果图已保存: {output_path}")
        return output_path
    
    def show_algorithm_comparison(self):
        """展示LSB vs DWT-DCT-SVD算法对比"""
        
        # 读取对比报告
        report_path = "output/advanced/reports/advanced_robustness_report.json"
        if not os.path.exists(report_path):
            print(" 找不到对比报告文件")
            return
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
        except:
            print(" 无法读取对比报告")
            return
        
        comparison_data = report_data.get('algorithm_comparison', {})
        
        # 创建对比图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('LSB vs DWT-DCT-SVD 算法对比分析', fontsize=16, fontweight='bold')
        
        # 1. PSNR对比
        algorithms = ['LSB', 'DWT-DCT-SVD']
        psnr_values = [
            comparison_data.get('lsb', {}).get('psnr', 0),
            comparison_data.get('advanced', {}).get('psnr', 0)
        ]
        
        bars1 = ax1.bar(algorithms, psnr_values, color=['lightblue', 'lightgreen'], alpha=0.8)
        ax1.set_ylabel('PSNR (dB)', fontsize=12)
        ax1.set_title('图像质量对比 (PSNR)', fontsize=14)
        ax1.set_ylim(0, max(psnr_values) * 1.2)
        
        # 添加数值标签
        for bar, value in zip(bars1, psnr_values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{value:.2f} dB', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # 2. 理论鲁棒性对比（基于算法特性）
        robustness_aspects = ['旋转', '压缩', '噪声', '滤波', '几何攻击']
        lsb_scores = [1, 1, 1, 1, 1]  # LSB算法的理论鲁棒性评分（1-5）
        dwt_scores = [4, 5, 4, 4, 3]  # DWT-DCT-SVD的理论鲁棒性评分
        
        x = np.arange(len(robustness_aspects))
        width = 0.35
        
        bars2 = ax2.bar(x - width/2, lsb_scores, width, label='LSB', color='lightblue', alpha=0.8)
        bars3 = ax2.bar(x + width/2, dwt_scores, width, label='DWT-DCT-SVD', color='lightgreen', alpha=0.8)
        
        ax2.set_xlabel('攻击类型', fontsize=12)
        ax2.set_ylabel('鲁棒性评分 (1-5)', fontsize=12)
        ax2.set_title('理论鲁棒性对比', fontsize=14)
        ax2.set_xticks(x)
        ax2.set_xticklabels(robustness_aspects)
        ax2.legend()
        ax2.set_ylim(0, 5)
        
        # 3. 算法特性对比雷达图
        categories = ['图像质量', '鲁棒性', '计算复杂度', '安全性', '隐蔽性']
        lsb_values = [4, 1, 5, 2, 3]  # LSB在各方面的评分
        dwt_values = [3, 5, 2, 4, 5]  # DWT-DCT-SVD在各方面的评分
        
        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形
        
        lsb_values += lsb_values[:1]
        dwt_values += dwt_values[:1]
        
        ax3.plot(angles, lsb_values, 'o-', linewidth=2, label='LSB', color='blue')
        ax3.fill(angles, lsb_values, alpha=0.25, color='blue')
        ax3.plot(angles, dwt_values, 'o-', linewidth=2, label='DWT-DCT-SVD', color='green')
        ax3.fill(angles, dwt_values, alpha=0.25, color='green')
        
        ax3.set_xticks(angles[:-1])
        ax3.set_xticklabels(categories)
        ax3.set_ylim(0, 5)
        ax3.set_title('算法综合特性对比', fontsize=14)
        ax3.legend()
        ax3.grid(True)
        
        # 4. 应用场景推荐
        scenarios = ['版权保护', '内容认证', '隐秘通信', '完整性检测', '防篡改']
        lsb_suitability = [2, 1, 4, 1, 1]
        dwt_suitability = [5, 5, 3, 4, 5]
        
        x = np.arange(len(scenarios))
        bars4 = ax4.bar(x - width/2, lsb_suitability, width, label='LSB', color='lightblue', alpha=0.8)
        bars5 = ax4.bar(x + width/2, dwt_suitability, width, label='DWT-DCT-SVD', color='lightgreen', alpha=0.8)
        
        ax4.set_xlabel('应用场景', fontsize=12)
        ax4.set_ylabel('适用性评分 (1-5)', fontsize=12)
        ax4.set_title('应用场景适用性对比', fontsize=14)
        ax4.set_xticks(x)
        ax4.set_xticklabels(scenarios, rotation=45, ha='right')
        ax4.legend()
        ax4.set_ylim(0, 5)
        
        plt.tight_layout()
        output_path = "output/advanced/visualization/algorithm_comparison.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f" 算法对比图已保存: {output_path}")
        return output_path
    
    def show_watermark_extraction_gallery(self):
        """展示水印提取结果画廊"""
        
        # 检查提取的水印目录
        extracted_dir = "output/advanced/robustness_test/extracted_watermarks"
        if not os.path.exists(extracted_dir):
            print(" 找不到提取的水印目录")
            return
        
        # 获取所有提取的水印文件
        extracted_files = [f for f in os.listdir(extracted_dir) if f.endswith('.png')]
        
        if not extracted_files:
            print(" 没有找到提取的水印文件")
            return
        
        # 创建画廊
        n_files = len(extracted_files)
        cols = 5
        rows = (n_files + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(20, 4*rows))
        fig.suptitle('水印提取结果画廊\nDWT-DCT-SVD 算法各种攻击后的提取效果', fontsize=16, fontweight='bold')
        
        if rows == 1:
            axes = axes.reshape(1, -1)
        
        for i, filename in enumerate(extracted_files[:rows*cols]):
            row, col = i // cols, i % cols
            
            try:
                img_path = os.path.join(extracted_dir, filename)
                img = Image.open(img_path)
                
                axes[row, col].imshow(img, cmap='gray')
                
                # 从文件名提取测试类型
                test_name = filename.replace('_extracted.png', '').replace('_', ' ')
                axes[row, col].set_title(test_name, fontsize=10)
                axes[row, col].axis('off')
                
            except Exception as e:
                axes[row, col].text(0.5, 0.5, f'加载失败\n{filename}', 
                                  ha='center', va='center', transform=axes[row, col].transAxes)
                axes[row, col].set_title(filename, fontsize=10)
                axes[row, col].axis('off')
        
        # 隐藏多余的子图
        for i in range(n_files, rows * cols):
            row, col = i // cols, i % cols
            axes[row, col].axis('off')
        
        plt.tight_layout()
        output_path = "output/advanced/visualization/extraction_gallery.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f" 提取结果画廊已保存: {output_path}")
        return output_path
    
    def generate_comprehensive_report(self):
        """生成综合可视化报告"""
        print("\n 生成综合可视化报告...")
        
        results = []
        
        # 1. 不可见性演示
        try:
            result1 = self.show_invisibility_demonstration()
            if result1:
                results.append(result1)
        except Exception as e:
            print(f" 不可见性演示失败: {e}")
        
        # 2. 鲁棒性结果
        try:
            result2 = self.show_robustness_results()
            if result2:
                results.append(result2)
        except Exception as e:
            print(f" 鲁棒性结果展示失败: {e}")
        
        # 3. 算法对比
        try:
            result3 = self.show_algorithm_comparison()
            if result3:
                results.append(result3)
        except Exception as e:
            print(f" 算法对比展示失败: {e}")
        
        # 4. 提取结果画廊
        try:
            result4 = self.show_watermark_extraction_gallery()
            if result4:
                results.append(result4)
        except Exception as e:
            print(f" 提取结果画廊失败: {e}")
        
        print(f"\n 综合可视化报告生成完成！")
        print(f" 共生成 {len(results)} 个可视化图表")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result}")
        
        return results

if __name__ == "__main__":
    visualizer = AdvancedWatermarkVisualizer()
    visualizer.generate_comprehensive_report() 