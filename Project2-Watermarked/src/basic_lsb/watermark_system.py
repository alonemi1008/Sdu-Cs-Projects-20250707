# -*- coding: utf-8 -*-
"""
Digital Watermark System
Based on LSB (Least Significant Bit) Algorithm
Author: SDU Cyber Science and Technology School
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import os
import time

class WatermarkSystem:
    def __init__(self):
        self.delimiter = "###END###"  # 分隔符，用于标记水印结束
        
    def string_to_binary(self, text):
        """将字符串转换为二进制"""
        try:
            # 使用UTF-8编码处理中文
            binary_text = ''.join(format(byte, '08b') for byte in text.encode('utf-8'))
            # 添加分隔符
            delimiter_binary = ''.join(format(byte, '08b') for byte in self.delimiter.encode('utf-8'))
            return binary_text + delimiter_binary
        except Exception as e:
            print(f"文本转二进制错误: {e}")
            return ""
    
    def binary_to_string(self, binary):
        """将二进制转换为字符串"""
        try:
            # 按8位分组
            chars = []
            for i in range(0, len(binary) - 7, 8):
                byte = binary[i:i+8]
                if len(byte) == 8:
                    try:
                        char_value = int(byte, 2)
                        if 0 <= char_value <= 255:
                            chars.append(char_value)
                    except ValueError:
                        continue
            
            if not chars:
                return ""
            
            # 转换为字节串
            byte_data = bytes(chars)
            
            # 尝试解码为UTF-8
            try:
                text = byte_data.decode('utf-8', errors='ignore')
                # 查找分隔符
                if self.delimiter in text:
                    return text[:text.index(self.delimiter)]
                return text
            except UnicodeDecodeError:
                return ""
                
        except Exception as e:
            print(f"二进制转文本错误: {e}")
            return ""
    
    def embed_text_watermark(self, image_path, text, output_path):
        """在图片中嵌入文本水印"""
        try:
            # 打开图片并转换为RGB
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            width, height = img.size
            
            # 转换文本为二进制
            binary_text = self.string_to_binary(text)
            if not binary_text:
                raise ValueError("文本转换为二进制失败")
            
            print(f"水印文本: {text}")
            print(f"二进制长度: {len(binary_text)} 位")
            
            # 检查图片容量是否足够
            max_capacity = width * height * 3  # RGB三个通道
            if len(binary_text) > max_capacity:
                raise ValueError(f"图片容量不足！需要 {len(binary_text)} 位，但只有 {max_capacity} 位可用")
            
            # 获取像素数据
            pixels = list(img.getdata())
            
            # 嵌入水印
            binary_index = 0
            new_pixels = []
            
            for pixel in pixels:
                r, g, b = pixel
                
                # 修改RGB通道的LSB
                if binary_index < len(binary_text):
                    r = (r & 0xFE) | int(binary_text[binary_index])
                    binary_index += 1
                
                if binary_index < len(binary_text):
                    g = (g & 0xFE) | int(binary_text[binary_index])
                    binary_index += 1
                    
                if binary_index < len(binary_text):
                    b = (b & 0xFE) | int(binary_text[binary_index])
                    binary_index += 1
                
                new_pixels.append((r, g, b))
                
                if binary_index >= len(binary_text):
                    # 添加剩余未修改的像素
                    new_pixels.extend(pixels[len(new_pixels):])
                    break
            
            # 创建新图片
            watermarked_img = Image.new('RGB', (width, height))
            watermarked_img.putdata(new_pixels)
            watermarked_img.save(output_path, 'PNG')  # 强制保存为PNG格式
            
            print(f"文本水印嵌入成功！保存至 {output_path}")
            return output_path
            
        except Exception as e:
            print(f"嵌入文本水印时出错: {e}")
            return None
    
    def embed_image_watermark(self, host_image_path, watermark_image_path, output_path, alpha=0.3):
        """在图片中嵌入图片水印"""
        try:
            # 打开主图和水印图
            host_img = Image.open(host_image_path).convert('RGB')
            watermark_img = Image.open(watermark_image_path).convert('RGB')
            
            # 调整水印大小
            host_width, host_height = host_img.size
            watermark_size = (host_width // 4, host_height // 4)  # 水印为原图的1/4大小
            watermark_img = watermark_img.resize(watermark_size, Image.Resampling.LANCZOS)
            
            # 转换为numpy数组进行处理
            host_array = np.array(host_img)
            watermark_array = np.array(watermark_img)
            
            # 选择嵌入位置（右下角）
            start_x = host_width - watermark_size[0]
            start_y = host_height - watermark_size[1]
            
            # 嵌入水印（混合模式）
            host_region = host_array[start_y:start_y+watermark_size[1], start_x:start_x+watermark_size[0]]
            blended_region = (1 - alpha) * host_region + alpha * watermark_array
            
            # 将混合后的区域放回主图
            result_array = host_array.copy()
            result_array[start_y:start_y+watermark_size[1], start_x:start_x+watermark_size[0]] = blended_region
            
            # 保存结果
            result_img = Image.fromarray(result_array.astype(np.uint8))
            result_img.save(output_path, 'PNG')
            
            print(f"图片水印嵌入成功！保存至 {output_path}")
            return output_path
            
        except Exception as e:
            print(f"嵌入图片水印时出错: {e}")
            return None
    
    def extract_text_watermark(self, image_path):
        """从图片中提取文本水印"""
        try:
            # 打开图片
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 获取像素数据
            pixels = list(img.getdata())
            
            # 提取LSB
            binary_text = ""
            for pixel in pixels:
                r, g, b = pixel
                binary_text += str(r & 1)
                binary_text += str(g & 1)
                binary_text += str(b & 1)
            
            print(f"提取的二进制长度: {len(binary_text)}")
            
            # 转换为文本
            extracted_text = self.binary_to_string(binary_text)
            
            # 清理提取的文本（移除不可打印字符）
            if extracted_text:
                cleaned_text = ''.join(char for char in extracted_text if char.isprintable() or char in '\n\r\t')
                return cleaned_text
            
            return extracted_text
            
        except Exception as e:
            print(f"提取文本水印时出错: {e}")
            return ""
    
    def calculate_psnr(self, original_path, watermarked_path):
        """计算PSNR值评估图片质量"""
        try:
            original = cv2.imread(original_path)
            watermarked = cv2.imread(watermarked_path)
            
            if original is None or watermarked is None:
                return 0
            
            # 确保图片尺寸相同
            if original.shape != watermarked.shape:
                watermarked = cv2.resize(watermarked, (original.shape[1], original.shape[0]))
            
            mse = np.mean((original.astype(np.float64) - watermarked.astype(np.float64)) ** 2)
            if mse == 0:
                return float('inf')
            
            max_pixel = 255.0
            psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
            return psnr
            
        except Exception as e:
            print(f"计算PSNR时出错: {e}")
            return 0 