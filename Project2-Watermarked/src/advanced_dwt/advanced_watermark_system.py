# -*- coding: utf-8 -*-
"""
Advanced Digital Watermark System
Based on DWT-DCT-SVD Algorithm (blind-watermark)
Author: SDU Cyber Science and Technology School
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import os
import time
from blind_watermark import WaterMark

class AdvancedWatermarkSystem:
    def __init__(self):
        """初始化高级水印系统"""
        self.bwm = None  # 将在嵌入时初始化
        
    def create_text_image(self, text, size=(200, 100), font_size=20):
        """将文本转换为图像"""
        try:
            # 创建白色背景的图像
            img = Image.new('RGB', size, color='white')
            draw = ImageDraw.Draw(img)
            
            # 尝试使用系统字体
            try:
                # Windows中文字体
                font = ImageFont.truetype("msyh.ttc", font_size)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # 计算文本位置使其居中
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            # 绘制黑色文字
            draw.text((x, y), text, fill='black', font=font)
            
            # 转换为灰度图
            gray_img = img.convert('L')
            
            return np.array(gray_img)
            
        except Exception as e:
            print(f"创建文本图像时出错: {e}")
            # 创建简单的黑白条纹作为备用水印
            watermark = np.zeros((64, 128))
            watermark[::4, :] = 255  # 每4行一个白色条纹
            return watermark.astype(np.uint8)
    
    def embed_text_watermark(self, host_image_path, text, output_path, password_wm=1, password_img=1):
        """嵌入文本水印"""
        try:
            print(f"开始嵌入文本水印: {text}")
            
            # 创建文本水印图像
            watermark_data = self.create_text_image(text, size=(200, 100), font_size=24)
            
            # 初始化盲水印对象
            self.bwm = WaterMark(password_wm=password_wm, password_img=password_img)
            
            # 读取宿主图像
            self.bwm.read_img(host_image_path)
            
            # 读取水印（从numpy数组）
            self.bwm.read_wm(watermark_data, mode='img')
            
            # 嵌入水印
            self.bwm.embed(output_path)
            
            print(f"文本水印嵌入成功！保存至: {output_path}")
            
            # 计算PSNR
            psnr = self.calculate_psnr(host_image_path, output_path)
            print(f"PSNR值: {psnr:.2f} dB")
            
            return output_path, psnr
            
        except Exception as e:
            print(f"嵌入文本水印失败: {e}")
            return None, 0
    
    def embed_image_watermark(self, host_image_path, watermark_image_path, output_path, password_wm=1, password_img=1):
        """嵌入图像水印"""
        try:
            print(f"开始嵌入图像水印")
            
            # 初始化盲水印对象
            self.bwm = WaterMark(password_wm=password_wm, password_img=password_img)
            
            # 读取宿主图像
            self.bwm.read_img(host_image_path)
            
            # 读取水印图像
            self.bwm.read_wm(watermark_image_path, mode='img')
            
            # 嵌入水印
            self.bwm.embed(output_path)
            
            print(f"图像水印嵌入成功！保存至: {output_path}")
            
            # 计算PSNR
            psnr = self.calculate_psnr(host_image_path, output_path)
            print(f"PSNR值: {psnr:.2f} dB")
            
            return output_path, psnr
            
        except Exception as e:
            print(f"嵌入图像水印失败: {e}")
            return None, 0
    
    def extract_watermark(self, watermarked_image_path, output_path, password_wm=1, password_img=1, wm_shape=None):
        """提取水印"""
        try:
            print(f"开始提取水印")
            
            # 初始化盲水印对象
            bwm_extract = WaterMark(password_wm=password_wm, password_img=password_img)
            
            # 如果没有指定水印尺寸，使用默认尺寸
            if wm_shape is None:
                wm_shape = (100, 200)  # 默认尺寸
            
            # 提取水印
            bwm_extract.extract(
                filename=watermarked_image_path,
                wm_shape=wm_shape,
                mode='img'
            )
            
            # 保存提取的水印
            extracted_wm = bwm_extract.wm
            if extracted_wm is not None:
                # 确保数据范围正确
                if extracted_wm.max() <= 1:
                    extracted_wm = (extracted_wm * 255).astype(np.uint8)
                else:
                    extracted_wm = extracted_wm.astype(np.uint8)
                
                # 保存为图像
                cv2.imwrite(output_path, extracted_wm)
                print(f"水印提取成功！保存至: {output_path}")
                return output_path
            else:
                print("水印提取失败")
                return None
                
        except Exception as e:
            print(f"提取水印时出错: {e}")
            return None
    
    def calculate_psnr(self, original_path, watermarked_path):
        """计算PSNR值"""
        try:
            # 读取图像
            original = cv2.imread(original_path)
            watermarked = cv2.imread(watermarked_path)
            
            if original is None or watermarked is None:
                return 0
            
            # 确保图像尺寸相同
            if original.shape != watermarked.shape:
                watermarked = cv2.resize(watermarked, (original.shape[1], original.shape[0]))
            
            # 计算MSE
            mse = np.mean((original.astype(np.float64) - watermarked.astype(np.float64)) ** 2)
            
            if mse == 0:
                return float('inf')
            
            # 计算PSNR
            max_pixel = 255.0
            psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
            
            return psnr
            
        except Exception as e:
            print(f"计算PSNR时出错: {e}")
            return 0
    
    def calculate_watermark_similarity(self, original_wm_path, extracted_wm_path):
        """计算水印相似度"""
        try:
            # 读取原始水印和提取的水印
            original_wm = cv2.imread(original_wm_path, cv2.IMREAD_GRAYSCALE)
            extracted_wm = cv2.imread(extracted_wm_path, cv2.IMREAD_GRAYSCALE)
            
            if original_wm is None or extracted_wm is None:
                return 0
            
            # 调整尺寸
            if original_wm.shape != extracted_wm.shape:
                extracted_wm = cv2.resize(extracted_wm, (original_wm.shape[1], original_wm.shape[0]))
            
            # 计算结构相似性（简化版）
            # 计算相关系数
            original_flat = original_wm.flatten().astype(np.float64)
            extracted_flat = extracted_wm.flatten().astype(np.float64)
            
            # 标准化
            original_norm = (original_flat - np.mean(original_flat)) / np.std(original_flat)
            extracted_norm = (extracted_flat - np.mean(extracted_flat)) / np.std(extracted_flat)
            
            # 计算相关系数
            correlation = np.corrcoef(original_norm, extracted_norm)[0, 1]
            
            # 转换为相似度百分比
            similarity = max(0, correlation) * 100
            
            return similarity
            
        except Exception as e:
            print(f"计算水印相似度时出错: {e}")
            return 0
    
    def create_difference_image(self, original_path, watermarked_path, output_path, amplify=10):
        """创建差异图像以可视化水印"""
        try:
            # 读取图像
            original = cv2.imread(original_path)
            watermarked = cv2.imread(watermarked_path)
            
            if original is None or watermarked is None:
                return None
            
            # 确保尺寸相同
            if original.shape != watermarked.shape:
                watermarked = cv2.resize(watermarked, (original.shape[1], original.shape[0]))
            
            # 计算差异
            diff = cv2.absdiff(original, watermarked)
            
            # 放大差异使其可见
            diff_amplified = np.clip(diff * amplify, 0, 255).astype(np.uint8)
            
            # 保存差异图像
            cv2.imwrite(output_path, diff_amplified)
            
            print(f"差异图像已保存至: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"创建差异图像时出错: {e}")
            return None 