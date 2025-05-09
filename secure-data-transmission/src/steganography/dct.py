import cv2
import numpy as np
import random

class DCTSteganography:
    def __init__(self, channel_count=3, pixel_pairs=1):
        """
        初始化DCT隐写类
        
        参数:
            channel_count (int): 用于隐写的颜色通道数量 (1-3, 对应YUV通道)
            pixel_pairs (int): 每个8*8像素块中用于隐写的像素对数量
        """
        self.channel_count = min(max(1, channel_count), 3)  # 限制在1-3范围内
        self.pixel_pairs = min(max(1, pixel_pairs), 16)  # 限制在1-16范围内（最大像素对数量限制）
        
    def _binary_to_string(self, binary):
        """将二进制字符串转换为ASCII字符串"""
        return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
    
    def _string_to_binary(self, message):
        """将ASCII字符串转换为二进制字符串"""
        return ''.join(format(ord(char), '08b') for char in message)
    
    def _get_coefficients_for_encoding(self, dct_block, num_pairs):
        """获取用于编码的DCT系数对"""
        # 为了确保可重复性，我们选择固定位置的系数对
        # 避开DC系数(0,0)和主要的低频系数
        pairs = []
        positions = [(2, 1), (1, 2), (3, 0), (0, 3), (4, 0), (0, 4), 
                    (5, 0), (0, 5), (6, 0), (0, 6), (2, 2), (3, 1), 
                    (1, 3), (4, 1), (1, 4), (5, 1)]
        
        for i in range(min(num_pairs, len(positions))):
            pos = positions[i]
            pairs.append((pos, dct_block[pos]))
            
        return pairs
    
    def encode(self, image_path, message, output_path):
        """
        将消息隐藏到图像中
        
        参数:
            image_path (str): 输入图像路径
            message (str): 要隐藏的消息
            output_path (str): 输出图像路径
            
        返回:
            bool: 操作是否成功
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像: {image_path}")
            return False
        
        # 转换为YUV颜色空间
        yuv_image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        
        # 准备消息
        message += 'EOF'  # 添加结束标记
        binary_message = self._string_to_binary(message)
        message_length = len(binary_message)
        message_index = 0
        
        # 计算图像可以容纳的位数
        height, width = image.shape[:2]
        blocks_h = height // 8
        blocks_w = width // 8
        max_bits = blocks_h * blocks_w * self.channel_count * self.pixel_pairs
        
        if message_length > max_bits:
            print(f"消息太长，无法在当前图像和设置下存储。最大: {max_bits//8} 字节，需要: {message_length//8} 字节")
            return False
        
        # 对每个8x8块应用DCT变换
        for channel in range(self.channel_count):
            for y in range(0, height - height % 8, 8):
                for x in range(0, width - width % 8, 8):
                    if message_index >= message_length:
                        break
                        
                    # 提取8x8块
                    block = yuv_image[y:y+8, x:x+8, channel].astype(np.float32)
                    
                    # 应用DCT
                    dct_block = cv2.dct(block)
                    
                    # 获取系数对
                    coef_pairs = self._get_coefficients_for_encoding(dct_block, self.pixel_pairs)
                    
                    # 嵌入消息位
                    for i, (pos, _) in enumerate(coef_pairs):
                        if message_index < message_length:
                            bit = int(binary_message[message_index])
                            
                            # 根据消息位调整系数
                            # 如果消息位为1，确保系数为正
                            # 如果消息位为0，确保系数为负
                            if (bit == 1 and dct_block[pos] < 0) or (bit == 0 and dct_block[pos] > 0):
                                dct_block[pos] = -dct_block[pos]
                                
                            message_index += 1
                    
                    # 应用IDCT并更新图像
                    block = cv2.idct(dct_block)
                    yuv_image[y:y+8, x:x+8, channel] = block
                
                if message_index >= message_length:
                    break
            
            if message_index >= message_length:
                break
        
        # 转换回BGR并保存
        output_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR)
        cv2.imwrite(output_path, output_image)
        return True
    
    def decode(self, image_path):
        """
        从图像中提取隐藏消息
        
        参数:
            image_path (str): 包含隐藏消息的图像路径
            
        返回:
            str: 提取的消息
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像: {image_path}")
            return ""
        
        # 转换为YUV颜色空间
        yuv_image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        
        # 提取二进制消息
        binary_message = ""
        height, width = image.shape[:2]
        
        # 检查EOF标记
        eof_marker = 'EOF'
        eof_binary = self._string_to_binary(eof_marker)
        
        # 从每个8x8块提取消息
        for channel in range(self.channel_count):
            for y in range(0, height - height % 8, 8):
                for x in range(0, width - width % 8, 8):
                    # 提取8x8块
                    block = yuv_image[y:y+8, x:x+8, channel].astype(np.float32)
                    
                    # 应用DCT
                    dct_block = cv2.dct(block)
                    
                    # 获取系数对
                    coef_pairs = self._get_coefficients_for_encoding(dct_block, self.pixel_pairs)
                    
                    # 提取消息位
                    for i, (pos, _) in enumerate(coef_pairs):
                        # 如果系数为正，消息位为1
                        # 如果系数为负，消息位为0
                        bit = '1' if dct_block[pos] >= 0 else '0'
                        binary_message += bit
                        
                        # 检查是否到达EOF标记
                        if len(binary_message) >= len(eof_binary) and binary_message[-len(eof_binary):] == eof_binary:
                            # 去除EOF标记并返回消息
                            return self._binary_to_string(binary_message[:-len(eof_binary)])
        
        # 如果没有找到EOF标记，尝试解析所有收集到的位
        return self._binary_to_string(binary_message)

# dct = DCTSteganography(channel_count=3, pixel_pairs=2)
# dct.encode('input_image.png', 'Secret Message', 'output_image.png')
# message = dct.decode('output_image.png')
# print(message) 