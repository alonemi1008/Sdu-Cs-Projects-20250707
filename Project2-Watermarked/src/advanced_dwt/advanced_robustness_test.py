# -*- coding: utf-8 -*-
"""
Advanced Robustness Test Module for DWT-DCT-SVD Watermark System
增强的鲁棒性测试模块
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
import time

class AdvancedRobustnessTest:
    def __init__(self, watermark_system):
        self.watermark_system = watermark_system
        
    def horizontal_flip(self, image_path, output_path):
        """水平翻转测试"""
        try:
            img = cv2.imread(image_path)
            flipped_img = cv2.flip(img, 1)  # 水平翻转
            cv2.imwrite(output_path, flipped_img)
            print(f" 水平翻转完成：{output_path}")
            return output_path
        except Exception as e:
            print(f" 水平翻转失败: {e}")
            return None
    
    def vertical_flip(self, image_path, output_path):
        """垂直翻转测试"""
        try:
            img = cv2.imread(image_path)
            flipped_img = cv2.flip(img, 0)  # 垂直翻转
            cv2.imwrite(output_path, flipped_img)
            print(f" 垂直翻转完成：{output_path}")
            return output_path
        except Exception as e:
            print(f" 垂直翻转失败: {e}")
            return None
    
    def rotation_test(self, image_path, output_path, angle=45):
        """旋转测试"""
        try:
            img = cv2.imread(image_path)
            height, width = img.shape[:2]
            center = (width // 2, height // 2)
            
            # 获取旋转矩阵
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # 应用旋转
            rotated_img = cv2.warpAffine(img, rotation_matrix, (width, height), 
                                       borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
            
            cv2.imwrite(output_path, rotated_img)
            print(f" 旋转 {angle}度 完成：{output_path}")
            return output_path
        except Exception as e:
            print(f" 旋转失败: {e}")
            return None
    
    def crop_test(self, image_path, output_path, crop_ratio=0.8):
        """截取测试"""
        try:
            img = cv2.imread(image_path)
            height, width = img.shape[:2]
            
            # 计算截取区域
            new_height = int(height * crop_ratio)
            new_width = int(width * crop_ratio)
            start_y = (height - new_height) // 2
            start_x = (width - new_width) // 2
            
            # 截取图像
            cropped_img = img[start_y:start_y+new_height, start_x:start_x+new_width]
            
            cv2.imwrite(output_path, cropped_img)
            print(f" 截取测试完成 ({crop_ratio*100}%)：{output_path}")
            return output_path
        except Exception as e:
            print(f" 截取失败: {e}")
            return None
    
    def resize_test(self, image_path, output_path, scale_factor=0.5):
        """缩放测试"""
        try:
            img = cv2.imread(image_path)
            height, width = img.shape[:2]
            
            # 先缩小
            new_size = (int(width * scale_factor), int(height * scale_factor))
            resized_img = cv2.resize(img, new_size, interpolation=cv2.INTER_CUBIC)
            
            # 再放大回原尺寸
            final_img = cv2.resize(resized_img, (width, height), interpolation=cv2.INTER_CUBIC)
            
            cv2.imwrite(output_path, final_img)
            print(f" 缩放测试完成 (缩放因子: {scale_factor})：{output_path}")
            return output_path
        except Exception as e:
            print(f" 缩放失败: {e}")
            return None
    
    def contrast_adjustment(self, image_path, output_path, factor=1.5):
        """对比度调整测试"""
        try:
            img = cv2.imread(image_path).astype(np.float64)
            
            # 调整对比度
            adjusted_img = img * factor
            adjusted_img = np.clip(adjusted_img, 0, 255).astype(np.uint8)
            
            cv2.imwrite(output_path, adjusted_img)
            print(f" 对比度调整完成 (因子: {factor})：{output_path}")
            return output_path
        except Exception as e:
            print(f" 对比度调整失败: {e}")
            return None
    
    def brightness_adjustment(self, image_path, output_path, factor=1.2):
        """亮度调整测试"""
        try:
            img = cv2.imread(image_path).astype(np.float64)
            
            # 调整亮度
            adjusted_img = img * factor
            adjusted_img = np.clip(adjusted_img, 0, 255).astype(np.uint8)
            
            cv2.imwrite(output_path, adjusted_img)
            print(f" 亮度调整完成 (因子: {factor})：{output_path}")
            return output_path
        except Exception as e:
            print(f" 亮度调整失败: {e}")
            return None
    
    def gaussian_noise(self, image_path, output_path, noise_level=25):
        """高斯噪声测试"""
        try:
            img = cv2.imread(image_path)
            
            # 生成高斯噪声
            noise = np.random.normal(0, noise_level, img.shape).astype(np.int16)
            
            # 添加噪声
            noisy_img = img.astype(np.int16) + noise
            noisy_img = np.clip(noisy_img, 0, 255).astype(np.uint8)
            
            cv2.imwrite(output_path, noisy_img)
            print(f" 高斯噪声测试完成 (噪声级别: {noise_level})：{output_path}")
            return output_path
        except Exception as e:
            print(f" 高斯噪声失败: {e}")
            return None
    
    def jpeg_compression(self, image_path, output_path, quality=50):
        """JPEG压缩测试"""
        try:
            img = cv2.imread(image_path)
            
            # JPEG压缩参数
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            
            # 压缩和解压缩
            _, encoded_img = cv2.imencode('.jpg', img, encode_param)
            decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
            
            cv2.imwrite(output_path, decoded_img)
            print(f" JPEG压缩测试完成 (质量: {quality})：{output_path}")
            return output_path
        except Exception as e:
            print(f" JPEG压缩失败: {e}")
            return None
    
    def salt_pepper_noise(self, image_path, output_path, noise_ratio=0.05):
        """椒盐噪声测试"""
        try:
            img = cv2.imread(image_path)
            
            # 生成随机噪声位置
            noise = np.random.random(img.shape[:2])
            
            # 添加椒盐噪声
            img_copy = img.copy()
            img_copy[noise < noise_ratio/2] = 0      # 椒噪声（黑点）
            img_copy[noise > 1 - noise_ratio/2] = 255  # 盐噪声（白点）
            
            cv2.imwrite(output_path, img_copy)
            print(f" 椒盐噪声测试完成 (噪声比例: {noise_ratio})：{output_path}")
            return output_path
        except Exception as e:
            print(f" 椒盐噪声失败: {e}")
            return None
    
    def gaussian_blur(self, image_path, output_path, kernel_size=5):
        """高斯模糊测试"""
        try:
            img = cv2.imread(image_path)
            
            # 应用高斯模糊
            blurred_img = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
            
            cv2.imwrite(output_path, blurred_img)
            print(f" 高斯模糊测试完成 (核大小: {kernel_size})：{output_path}")
            return output_path
        except Exception as e:
            print(f" 高斯模糊失败: {e}")
            return None
    
    def median_filter(self, image_path, output_path, kernel_size=5):
        """中值滤波测试"""
        try:
            img = cv2.imread(image_path)
            
            # 应用中值滤波
            filtered_img = cv2.medianBlur(img, kernel_size)
            
            cv2.imwrite(output_path, filtered_img)
            print(f" 中值滤波测试完成 (核大小: {kernel_size})：{output_path}")
            return output_path
        except Exception as e:
            print(f" 中值滤波失败: {e}")
            return None
    
    def run_comprehensive_tests(self, watermarked_image_path, output_dir, password_wm=1, password_img=1, wm_shape=(100, 200)):
        """运行全面的鲁棒性测试"""
        print("="*60)
        print(" 开始DWT-DCT-SVD水印鲁棒性测试")
        print("="*60)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        extracted_dir = os.path.join(output_dir, "extracted_watermarks")
        os.makedirs(extracted_dir, exist_ok=True)
        
        results = {}
        
        # 测试列表
        tests = [
            ("horizontal_flip", self.horizontal_flip, {}),
            ("vertical_flip", self.vertical_flip, {}),
            ("rotation_15", self.rotation_test, {"angle": 15}),
            ("rotation_45", self.rotation_test, {"angle": 45}),
            ("crop_90", self.crop_test, {"crop_ratio": 0.9}),
            ("crop_80", self.crop_test, {"crop_ratio": 0.8}),
            ("resize_75", self.resize_test, {"scale_factor": 0.75}),
            ("resize_50", self.resize_test, {"scale_factor": 0.5}),
            ("contrast_150", self.contrast_adjustment, {"factor": 1.5}),
            ("contrast_70", self.contrast_adjustment, {"factor": 0.7}),
            ("brightness_120", self.brightness_adjustment, {"factor": 1.2}),
            ("brightness_80", self.brightness_adjustment, {"factor": 0.8}),
            ("gaussian_noise_15", self.gaussian_noise, {"noise_level": 15}),
            ("gaussian_noise_25", self.gaussian_noise, {"noise_level": 25}),
            ("jpeg_80", self.jpeg_compression, {"quality": 80}),
            ("jpeg_50", self.jpeg_compression, {"quality": 50}),
            ("salt_pepper_3", self.salt_pepper_noise, {"noise_ratio": 0.03}),
            ("salt_pepper_5", self.salt_pepper_noise, {"noise_ratio": 0.05}),
            ("gaussian_blur_3", self.gaussian_blur, {"kernel_size": 3}),
            ("gaussian_blur_5", self.gaussian_blur, {"kernel_size": 5}),
            ("median_filter_3", self.median_filter, {"kernel_size": 3}),
            ("median_filter_5", self.median_filter, {"kernel_size": 5}),
        ]
        
        for test_name, test_func, kwargs in tests:
            try:
                print(f"\n 执行测试: {test_name}")
                
                # 执行攻击
                attacked_path = os.path.join(output_dir, f"{test_name}.png")
                result_path = test_func(watermarked_image_path, attacked_path, **kwargs)
                
                if result_path and os.path.exists(result_path):
                    # 尝试提取水印
                    extracted_wm_path = os.path.join(extracted_dir, f"{test_name}_extracted.png")
                    extracted_path = self.watermark_system.extract_watermark(
                        result_path, 
                        extracted_wm_path,
                        password_wm=password_wm,
                        password_img=password_img,
                        wm_shape=wm_shape
                    )
                    
                    # 评估结果
                    if extracted_path and os.path.exists(extracted_path):
                        # 简单的成功判断（基于文件大小和内容）
                        success = os.path.getsize(extracted_path) > 1000  # 简单的大小检查
                        
                        results[test_name] = {
                            "success": success,
                            "attack_path": result_path,
                            "extracted_path": extracted_path,
                            "status": "成功" if success else "部分成功"
                        }
                        
                        print(f"   {test_name}: {results[test_name]['status']}")
                    else:
                        results[test_name] = {
                            "success": False,
                            "attack_path": result_path,
                            "extracted_path": None,
                            "status": "提取失败"
                        }
                        print(f"   {test_name}: 提取失败")
                else:
                    results[test_name] = {
                        "success": False,
                        "attack_path": None,
                        "extracted_path": None,
                        "status": "攻击失败",
                        "error": "攻击测试失败"
                    }
                    print(f"   {test_name}: 攻击失败")
                
            except Exception as e:
                print(f"   {test_name}: 错误 - {str(e)}")
                results[test_name] = {
                    "success": False,
                    "attack_path": None,
                    "extracted_path": None,
                    "status": "错误",
                    "error": str(e)
                }
        
        # 计算总体统计
        total_tests = len(results)
        successful_tests = sum(1 for result in results.values() if result.get('success', False))
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print(f" 测试完成！总体成功率: {success_rate:.1%} ({successful_tests}/{total_tests})")
        print("="*60)
        
        return results, success_rate 