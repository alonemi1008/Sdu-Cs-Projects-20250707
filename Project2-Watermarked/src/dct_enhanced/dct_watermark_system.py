# -*- coding: utf-8 -*-
"""
DCT频域数字水印系统
基于离散余弦变换 (DCT) 的频域水印算法
山东大学网络空间安全学院
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import os
import time
from scipy.fftpack import dct, idct

class DCTWatermarkSystem:
    def __init__(self):
        """初始化DCT水印系统"""
        self.block_size = 8  # DCT块大小
        self.alpha = 0.1     # 水印强度系数（控制不可见性）
        
    def create_text_watermark(self, text, size=(128, 64), font_size=16):
        """创建文本水印图像"""
        try:
            # 创建白色背景的图像
            img = Image.new('L', size, color=255)  # 灰度图
            draw = ImageDraw.Draw(img)
            
            # 尝试使用系统字体
            try:
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
            draw.text((x, y), text, fill=0, font=font)
            
            # 转换为numpy数组并二值化
            watermark = np.array(img)
            watermark = (watermark < 128).astype(np.float32)  # 二值化
            
            return watermark
            
        except Exception as e:
            print(f"创建文本水印时出错: {e}")
            # 创建简单的条纹水印作为备用
            watermark = np.zeros((64, 128), dtype=np.float32)
            watermark[::4, :] = 1  # 每4行一个白色条纹
            return watermark
    
    def dct2(self, block):
        """2D DCT变换"""
        return dct(dct(block.T, norm='ortho').T, norm='ortho')
    
    def idct2(self, block):
        """2D IDCT变换"""
        return idct(idct(block.T, norm='ortho').T, norm='ortho')
    
    def embed_watermark_dct(self, host_image, watermark, alpha=None):
        """使用DCT在频域嵌入水印"""
        if alpha is None:
            alpha = self.alpha
            
        # 确保图像尺寸是8的倍数
        h, w = host_image.shape[:2]
        if len(host_image.shape) == 3:
            # 对于彩色图像，只处理Y通道（亮度）
            if host_image.shape[2] == 3:
                # 转换为YUV
                yuv = cv2.cvtColor(host_image, cv2.COLOR_RGB2YUV)
                Y = yuv[:, :, 0].astype(np.float32)
            else:
                Y = host_image[:, :, 0].astype(np.float32)
        else:
            Y = host_image.astype(np.float32)
        
        # 调整图像尺寸为8的倍数
        new_h = (h // self.block_size) * self.block_size
        new_w = (w // self.block_size) * self.block_size
        Y = Y[:new_h, :new_w]
        
        # 调整水印尺寸
        wm_h, wm_w = watermark.shape
        blocks_h = new_h // self.block_size
        blocks_w = new_w // self.block_size
        
        # 重新调整水印尺寸以匹配DCT块数量
        watermark_resized = cv2.resize(watermark, (blocks_w, blocks_h), interpolation=cv2.INTER_NEAREST)
        
        # 创建带水印的图像副本
        watermarked_Y = Y.copy()
        
        # 遍历每个8x8块
        for i in range(0, new_h, self.block_size):
            for j in range(0, new_w, self.block_size):
                # 提取8x8块
                block = Y[i:i+self.block_size, j:j+self.block_size]
                
                # DCT变换
                dct_block = self.dct2(block)
                
                # 获取对应的水印位
                wm_i, wm_j = i // self.block_size, j // self.block_size
                if wm_i < watermark_resized.shape[0] and wm_j < watermark_resized.shape[1]:
                    wm_bit = watermark_resized[wm_i, wm_j]
                    
                    # 在DCT系数中嵌入水印（选择中频系数）
                    # 选择位置(3,3)作为嵌入位置，这是一个中频系数
                    if wm_bit > 0.5:
                        dct_block[3, 3] += alpha * abs(dct_block[3, 3])
                    else:
                        dct_block[3, 3] -= alpha * abs(dct_block[3, 3])
                
                # IDCT变换
                watermarked_block = self.idct2(dct_block)
                watermarked_Y[i:i+self.block_size, j:j+self.block_size] = watermarked_block
        
        # 重建完整图像
        if len(host_image.shape) == 3:
            if host_image.shape[2] == 3:
                # 重建YUV图像
                watermarked_yuv = yuv.copy().astype(np.float32)
                watermarked_yuv[:new_h, :new_w, 0] = watermarked_Y
                
                # 转换回RGB
                watermarked_rgb = cv2.cvtColor(watermarked_yuv.astype(np.uint8), cv2.COLOR_YUV2RGB)
                
                # 如果原始尺寸不同，则调整
                if watermarked_rgb.shape[:2] != host_image.shape[:2]:
                    watermarked_rgb = cv2.resize(watermarked_rgb, (w, h))
                
                return watermarked_rgb
            else:
                # 处理其他彩色格式
                result = host_image.copy().astype(np.float32)
                result[:new_h, :new_w, 0] = watermarked_Y
                return result.astype(np.uint8)
        else:
            # 灰度图像
            result = np.zeros_like(host_image, dtype=np.float32)
            result[:new_h, :new_w] = watermarked_Y
            if result.shape != host_image.shape:
                result = cv2.resize(result, (w, h))
            return result.astype(np.uint8)
    
    def extract_watermark_dct(self, watermarked_image, watermark_shape):
        """从含水印图像中提取水印"""
        try:
            # 转换为灰度/Y通道
            if len(watermarked_image.shape) == 3:
                if watermarked_image.shape[2] == 3:
                    yuv = cv2.cvtColor(watermarked_image, cv2.COLOR_RGB2YUV)
                    Y = yuv[:, :, 0].astype(np.float32)
                else:
                    Y = watermarked_image[:, :, 0].astype(np.float32)
            else:
                Y = watermarked_image.astype(np.float32)
            
            # 调整尺寸
            h, w = Y.shape
            new_h = (h // self.block_size) * self.block_size
            new_w = (w // self.block_size) * self.block_size
            Y = Y[:new_h, :new_w]
            
            blocks_h = new_h // self.block_size
            blocks_w = new_w // self.block_size
            
            # 提取水印
            extracted_wm = np.zeros((blocks_h, blocks_w), dtype=np.float32)
            
            for i in range(0, new_h, self.block_size):
                for j in range(0, new_w, self.block_size):
                    # 提取8x8块
                    block = Y[i:i+self.block_size, j:j+self.block_size]
                    
                    # DCT变换
                    dct_block = self.dct2(block)
                    
                    # 提取水印位（基于DCT系数的符号或大小）
                    wm_i, wm_j = i // self.block_size, j // self.block_size
                    if wm_i < blocks_h and wm_j < blocks_w:
                        # 基于(3,3)位置的DCT系数判断水印位
                        extracted_wm[wm_i, wm_j] = 1 if dct_block[3, 3] > 0 else 0
            
            # 调整到目标尺寸
            if extracted_wm.shape != watermark_shape:
                extracted_wm = cv2.resize(extracted_wm, (watermark_shape[1], watermark_shape[0]), 
                                        interpolation=cv2.INTER_NEAREST)
            
            return extracted_wm
            
        except Exception as e:
            print(f"提取水印时出错: {e}")
            return np.zeros(watermark_shape, dtype=np.float32)
    
    def embed_text_watermark(self, host_image_path, text, output_path, alpha=0.05):
        """嵌入文本水印"""
        try:
            print(f"开始DCT频域文本水印嵌入: {text}")
            
            # 读取宿主图像
            host_image = cv2.imread(host_image_path)
            if host_image is None:
                print(f"无法读取图像: {host_image_path}")
                return None, 0
            
            host_image = cv2.cvtColor(host_image, cv2.COLOR_BGR2RGB)
            
            # 创建文本水印
            watermark = self.create_text_watermark(text, size=(128, 64), font_size=20)
            
            # 嵌入水印
            watermarked_image = self.embed_watermark_dct(host_image, watermark, alpha)
            
            # 保存结果
            watermarked_pil = Image.fromarray(watermarked_image.astype(np.uint8))
            watermarked_pil.save(output_path, 'PNG')
            
            print(f"DCT频域文本水印嵌入成功！保存至: {output_path}")
            
            # 计算PSNR
            psnr = self.calculate_psnr(host_image_path, output_path)
            print(f"PSNR值: {psnr:.2f} dB")
            
            return output_path, psnr
            
        except Exception as e:
            print(f"DCT频域文本水印嵌入失败: {e}")
            return None, 0
    
    def extract_text_watermark(self, watermarked_image_path, output_path, watermark_shape=(64, 128)):
        """提取文本水印"""
        try:
            print(f"开始DCT频域水印提取")
            
            # 读取含水印图像
            watermarked_image = cv2.imread(watermarked_image_path)
            if watermarked_image is None:
                print(f"无法读取图像: {watermarked_image_path}")
                return None
            
            watermarked_image = cv2.cvtColor(watermarked_image, cv2.COLOR_BGR2RGB)
            
            # 提取水印
            extracted_wm = self.extract_watermark_dct(watermarked_image, watermark_shape)
            
            # 转换为0-255范围并保存
            extracted_wm_img = (extracted_wm * 255).astype(np.uint8)
            
            # 保存提取的水印
            cv2.imwrite(output_path, extracted_wm_img)
            
            print(f"DCT频域水印提取成功！保存至: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"DCT频域水印提取失败: {e}")
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