# -*- coding: utf-8 -*-
"""
水印系统结果可视化程序
Watermark System Results Visualization
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np
import os
import json

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class WatermarkVisualizer:
    def __init__(self):
        self.fig_size = (15, 10)
    
    def show_watermark_results(self):
        """展示水印嵌入结果"""
        
        # 检查文件是否存在
        original_path = "images/original.png"
        text_watermarked_path = "output/watermarked/text_watermarked.png"
        image_watermarked_path = "output/watermarked/image_watermarked.png"
        
        if not all(os.path.exists(path) for path in [original_path, text_watermarked_path, image_watermarked_path]):
            print("请先运行 main.py 生成水印图片")
            return
        
        # 创建图形
        fig, axes = plt.subplots(2, 2, figsize=self.fig_size)
        fig.suptitle('数字水印嵌入结果展示', fontsize=16, fontweight='bold')
        
        # 原始图片
        original_img = Image.open(original_path)
        axes[0, 0].imshow(original_img)
        axes[0, 0].set_title('原始图片', fontsize=12)
        axes[0, 0].axis('off')
        
        # 文本水印图片
        text_watermarked_img = Image.open(text_watermarked_path)
        axes[0, 1].imshow(text_watermarked_img)
        axes[0, 1].set_title('嵌入文本水印图片\n(山东大学网络空间安全学院)', fontsize=12)
        axes[0, 1].axis('off')
        
        # 图片水印图片
        image_watermarked_img = Image.open(image_watermarked_path)
        axes[1, 0].imshow(image_watermarked_img)
        axes[1, 0].set_title('嵌入图片水印图片', fontsize=12)
        axes[1, 0].axis('off')
        
        # 差异图
        original_array = np.array(original_img)
        watermarked_array = np.array(text_watermarked_img)
        
        # 计算差异
        diff = np.abs(original_array.astype(np.float32) - watermarked_array.astype(np.float32))
        diff_enhanced = np.clip(diff * 10, 0, 255)  # 增强显示效果
        
        axes[1, 1].imshow(diff_enhanced.astype(np.uint8))
        axes[1, 1].set_title('原图与文本水印图差异\n(增强10倍显示)', fontsize=12)
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig('output/reports/watermark_results.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def show_robustness_results(self):
        """展示鲁棒性测试结果"""
        
        # 读取测试报告
        report_path = "output/reports/robustness_report.json"
        if not os.path.exists(report_path):
            print("请先运行 main.py 生成测试报告")
            return
        
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        results = report_data['detailed_results']
        
        # 准备数据
        test_names = []
        success_flags = []
        accuracy_scores = []
        
        for test_name, result in results.items():
            test_names.append(test_name.replace('_', '\n'))
            success_flags.append(result.get('success', False))
            accuracy_scores.append(result.get('accuracy', 0) * 100)
        
        # 创建图形
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
        fig.suptitle('鲁棒性测试结果分析', fontsize=16, fontweight='bold')
        
        # 成功率柱状图
        colors = ['green' if success else 'red' for success in success_flags]
        bars1 = ax1.bar(range(len(test_names)), [100 if success else 0 for success in success_flags], 
                       color=colors, alpha=0.7)
        
        ax1.set_title('各项测试成功情况', fontsize=14)
        ax1.set_ylabel('成功率 (%)', fontsize=12)
        ax1.set_ylim(0, 120)
        ax1.set_xticks(range(len(test_names)))
        ax1.set_xticklabels(test_names, rotation=45, ha='right', fontsize=10)
        
        # 在柱子上添加标签
        for i, (bar, success) in enumerate(zip(bars1, success_flags)):
            if success:
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                        '成功', ha='center', va='bottom', fontsize=8, color='green')
            else:
                ax1.text(bar.get_x() + bar.get_width()/2, 10, 
                        '失败', ha='center', va='bottom', fontsize=8, color='red')
        
        # 准确率柱状图
        bars2 = ax2.bar(range(len(test_names)), accuracy_scores, 
                       color='skyblue', alpha=0.7)
        
        ax2.set_title('文本相似度准确率', fontsize=14)
        ax2.set_ylabel('准确率 (%)', fontsize=12)
        ax2.set_ylim(0, 100)
        ax2.set_xticks(range(len(test_names)))
        ax2.set_xticklabels(test_names, rotation=45, ha='right', fontsize=10)
        
        # 在柱子上添加数值标签
        for bar, score in zip(bars2, accuracy_scores):
            if score > 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                        f'{score:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # 添加统计信息
        total_tests = len(results)
        successful_tests = sum(success_flags)
        overall_success_rate = successful_tests / total_tests * 100
        
        fig.text(0.02, 0.02, f'总测试数: {total_tests} | 成功测试数: {successful_tests} | 总体成功率: {overall_success_rate:.1f}%', 
                fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)
        plt.savefig('output/reports/robustness_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 生成攻击效果展示
        self.show_attack_effects()
    
    def show_attack_effects(self):
        """展示部分攻击效果"""
        
        attack_examples = [
            "horizontal_flip.png",
            "rotation_45.png", 
            "crop_80.png",
            "contrast_150.png",
            "gaussian_noise_25.png",
            "jpeg_50.png"
        ]
        
        attack_names = [
            "水平翻转",
            "旋转45°",
            "截取80%",
            "对比度+50%", 
            "高斯噪声",
            "JPEG压缩"
        ]
        
        # 检查文件是否存在
        base_path = "output/robustness_test"
        existing_files = []
        existing_names = []
        
        for i, filename in enumerate(attack_examples):
            filepath = os.path.join(base_path, filename)
            if os.path.exists(filepath):
                existing_files.append(filepath)
                existing_names.append(attack_names[i])
        
        if not existing_files:
            print("没有找到攻击测试结果图片")
            return
        
        # 创建图形
        rows = 2
        cols = 3
        fig, axes = plt.subplots(rows, cols, figsize=(15, 10))
        fig.suptitle('部分攻击效果展示', fontsize=16, fontweight='bold')
        
        for i in range(rows * cols):
            row = i // cols
            col = i % cols
            
            if i < len(existing_files):
                img = Image.open(existing_files[i])
                axes[row, col].imshow(img)
                axes[row, col].set_title(existing_names[i], fontsize=12)
            else:
                axes[row, col].text(0.5, 0.5, '无数据', ha='center', va='center', 
                                  transform=axes[row, col].transAxes, fontsize=12)
            
            axes[row, col].axis('off')
        
        plt.tight_layout()
        plt.savefig('output/reports/attack_effects.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """主程序"""
    print("数字水印系统结果可视化")
    print("="*40)
    
    visualizer = WatermarkVisualizer()
    
    try:
        print("1. 展示水印嵌入结果...")
        visualizer.show_watermark_results()
        
        print("2. 展示鲁棒性测试结果...")
        visualizer.show_robustness_results()
        
        print("可视化完成！图片已保存到 output/reports/ 目录")
        
    except Exception as e:
        print(f"可视化过程中出现错误：{str(e)}")
        print("请确保已经运行过 main.py 并生成了相关文件")

if __name__ == "__main__":
    main() 