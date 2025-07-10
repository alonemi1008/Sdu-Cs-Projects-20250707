# -*- coding: utf-8 -*-
"""
Robustness Test Module for Watermark System
包含各种攻击测试：翻转、平移、截取、对比度调整等
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
import time

class RobustnessTest:
    def __init__(self, watermark_system):
        self.watermark_system = watermark_system
        
    def horizontal_flip(self, image_path, output_path):
        """水平翻转测试"""
        try:
            img = Image.open(image_path)
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)
            flipped_img.save(output_path, 'PNG')
            print(f"水平翻转完成：{output_path}")
            return output_path
        except Exception as e:
            print(f"水平翻转失败: {e}")
            return None
    
    def vertical_flip(self, image_path, output_path):
        """垂直翻转测试"""
        try:
            img = Image.open(image_path)
            flipped_img = img.transpose(Image.FLIP_TOP_BOTTOM)
            flipped_img.save(output_path, 'PNG')
            print(f"垂直翻转完成：{output_path}")
            return output_path
        except Exception as e:
            print(f"垂直翻转失败: {e}")
            return None
    
    def rotation_test(self, image_path, output_path, angle=45):
        """旋转测试"""
        try:
            img = Image.open(image_path)
            rotated_img = img.rotate(angle, expand=True, fillcolor='white')
            rotated_img.save(output_path, 'PNG')
            print(f"旋转 {angle}度 完成：{output_path}")
            return output_path
        except Exception as e:
            print(f"旋转失败: {e}")
            return None
    
    def crop_test(self, image_path, output_path, crop_ratio=0.8):
        """截取测试"""
        try:
            img = Image.open(image_path)
            width, height = img.size
            
            # 计算截取区域
            new_width = int(width * crop_ratio)
            new_height = int(height * crop_ratio)
            left = (width - new_width) // 2
            top = (height - new_height) // 2
            right = left + new_width
            bottom = top + new_height
            
            cropped_img = img.crop((left, top, right, bottom))
            cropped_img.save(output_path, 'PNG')
            print(f"截取测试完成 ({crop_ratio*100}%)：{output_path}")
            return output_path
        except Exception as e:
            print(f"截取失败: {e}")
            return None
    
    def resize_test(self, image_path, output_path, scale_factor=0.5):
        """缩放测试"""
        try:
            img = Image.open(image_path)
            width, height = img.size
            new_size = (int(width * scale_factor), int(height * scale_factor))
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
            # 再放大回原尺寸
            resized_img = resized_img.resize((width, height), Image.Resampling.LANCZOS)
            resized_img.save(output_path, 'PNG')
            print(f"缩放测试完成 (缩放因子: {scale_factor})：{output_path}")
            return output_path
        except Exception as e:
            print(f"缩放失败: {e}")
            return None
    
    def contrast_adjustment(self, image_path, output_path, factor=1.5):
        """对比度调整测试"""
        try:
            img = Image.open(image_path)
            enhancer = ImageEnhance.Contrast(img)
            enhanced_img = enhancer.enhance(factor)
            enhanced_img.save(output_path, 'PNG')
            print(f"对比度调整完成 (因子: {factor})：{output_path}")
            return output_path
        except Exception as e:
            print(f"对比度调整失败: {e}")
            return None
    
    def brightness_adjustment(self, image_path, output_path, factor=1.2):
        """亮度调整测试"""
        try:
            img = Image.open(image_path)
            enhancer = ImageEnhance.Brightness(img)
            enhanced_img = enhancer.enhance(factor)
            enhanced_img.save(output_path, 'PNG')
            print(f"亮度调整完成 (因子: {factor})：{output_path}")
            return output_path
        except Exception as e:
            print(f"亮度调整失败: {e}")
            return None
    
    def gaussian_noise(self, image_path, output_path, noise_level=25):
        """高斯噪声测试"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                print(f"无法读取图片: {image_path}")
                return None
                
            noise = np.random.normal(0, noise_level, img.shape).astype(np.int16)
            noisy_img = img.astype(np.int16) + noise
            noisy_img = np.clip(noisy_img, 0, 255).astype(np.uint8)
            cv2.imwrite(output_path, noisy_img)
            print(f"高斯噪声测试完成 (噪声级别: {noise_level})：{output_path}")
            return output_path
        except Exception as e:
            print(f"高斯噪声失败: {e}")
            return None
    
    def jpeg_compression(self, image_path, output_path, quality=50):
        """JPEG压缩测试"""
        try:
            img = Image.open(image_path)
            # 先保存为JPEG格式压缩，再转回PNG
            temp_jpeg = output_path.replace('.png', '_temp.jpg')
            img.save(temp_jpeg, 'JPEG', quality=quality)
            # 重新读取并保存为PNG
            compressed_img = Image.open(temp_jpeg)
            compressed_img.save(output_path, 'PNG')
            # 删除临时文件
            if os.path.exists(temp_jpeg):
                os.remove(temp_jpeg)
            print(f"JPEG压缩测试完成 (质量: {quality})：{output_path}")
            return output_path
        except Exception as e:
            print(f"JPEG压缩失败: {e}")
            return None
    
    def salt_pepper_noise(self, image_path, output_path, noise_ratio=0.05):
        """椒盐噪声测试"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                print(f"无法读取图片: {image_path}")
                return None
                
            # 生成噪声
            noise = np.random.random(img.shape[:2])
            
            # 添加椒盐噪声
            img_copy = img.copy()
            img_copy[noise < noise_ratio/2] = 0
            img_copy[noise > 1 - noise_ratio/2] = 255
            
            cv2.imwrite(output_path, img_copy)
            print(f"椒盐噪声测试完成 (噪声比例: {noise_ratio})：{output_path}")
            return output_path
        except Exception as e:
            print(f"椒盐噪声失败: {e}")
            return None
    
    def run_all_tests(self, watermarked_image_path, output_dir, original_text="山东大学网络空间安全学院"):
        """运行所有鲁棒性测试"""
        print("="*50)
        print("开始鲁棒性测试...")
        print("="*50)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        results = {}
        
        # 测试列表（减少测试数量避免过长输出）
        tests = [
            ("horizontal_flip", self.horizontal_flip, {}),
            ("vertical_flip", self.vertical_flip, {}),
            ("rotation_45", self.rotation_test, {"angle": 45}),
            ("crop_80", self.crop_test, {"crop_ratio": 0.8}),
            ("resize_75", self.resize_test, {"scale_factor": 0.75}),
            ("contrast_150", self.contrast_adjustment, {"factor": 1.5}),
            ("brightness_120", self.brightness_adjustment, {"factor": 1.2}),
            ("gaussian_noise_25", self.gaussian_noise, {"noise_level": 25}),
            ("jpeg_50", self.jpeg_compression, {"quality": 50}),
            ("salt_pepper_5", self.salt_pepper_noise, {"noise_ratio": 0.05}),
        ]
        
        for test_name, test_func, kwargs in tests:
            try:
                print(f"\n执行测试: {test_name}")
                
                # 执行攻击
                attacked_path = os.path.join(output_dir, f"{test_name}.png")
                result_path = test_func(watermarked_image_path, attacked_path, **kwargs)
                
                if result_path and os.path.exists(result_path):
                    # 尝试提取水印
                    extracted_text = self.watermark_system.extract_text_watermark(result_path)
                    
                    # 安全地处理提取的文本
                    if extracted_text:
                        # 只保留安全的字符
                        safe_text = ''.join(c for c in extracted_text if c.isprintable() and ord(c) < 128)
                        if len(safe_text) > 50:  # 截断过长的文本
                            safe_text = safe_text[:50] + "..."
                    else:
                        safe_text = ""
                    
                    # 检查提取是否成功
                    success = original_text in extracted_text if extracted_text else False
                    accuracy = self.calculate_text_similarity(original_text, extracted_text) if extracted_text else 0
                    
                    results[test_name] = {
                        "success": success,
                        "extracted_text": safe_text,  # 使用安全的文本
                        "accuracy": accuracy,
                        "attack_path": result_path
                    }
                    
                    print(f"{test_name}: {'成功' if success else '失败'} (准确率: {accuracy:.2%})")
                    if safe_text and len(safe_text) > 0:
                        print(f"  提取文本片段: {safe_text}")
                else:
                    results[test_name] = {
                        "success": False,
                        "extracted_text": "",
                        "accuracy": 0,
                        "error": "攻击测试失败"
                    }
                    print(f"{test_name}: 攻击测试失败")
                
            except Exception as e:
                print(f"{test_name}: 错误 - {str(e)}")
                results[test_name] = {
                    "success": False,
                    "extracted_text": "",
                    "accuracy": 0,
                    "error": str(e)
                }
        
        return results
    
    def calculate_text_similarity(self, original, extracted):
        """计算文本相似度"""
        if not extracted or not original:
            return 0
        
        try:
            # 简单的字符匹配相似度
            original_chars = set(original)
            extracted_chars = set(extracted)
            
            if len(original_chars) == 0:
                return 0
            
            intersection = len(original_chars.intersection(extracted_chars))
            similarity = intersection / len(original_chars)
            
            return similarity
        except Exception:
            return 0 