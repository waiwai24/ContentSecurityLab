import cv2

# 注意：一次发送的data长度不能超过图像的像素值
# 例如：300*300的图像，3个通道，每个通道使用2个最低位，那么一次最多发送300*300*3*2/8=22500字节

class LSBSteganography:
    def __init__(self, channel_count=3, lsb_count=1):
        """
        初始化LSB隐写类
        
        参数:
            channel_count (int): 用于隐写的颜色通道数量 (1-3, 对应RGB)
            lsb_count (int): 每个颜色值使用的最低位数量 (1-8)
        """
        self.channel_count = min(max(1, channel_count), 3)  # 限制在1-3范围内
        self.lsb_count = min(max(1, lsb_count), 8)  # 限制在1-8范围内
        # 创建位掩码，用于清除指定数量的最低位
        self.mask = ~((1 << self.lsb_count) - 1)

    def encode(self, image_path, data, output_path):
        """
        将数据隐藏到图像中
        
        参数:
            image_path (str): 输入图像路径
            data (str): 要隐藏的数据
            output_path (str): 输出图像路径
        
        返回:
            bool: 成功返回True，失败返回False
        """
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像: {image_path}")
            return False
            
        data += 'EOF'  # 文件结束标记
        data_index = 0
        data_length = len(data) * 8  # 需要编码的总位数
        
        # 计算图像可以存储的最大位数
        max_bits = image.shape[0] * image.shape[1] * self.channel_count * self.lsb_count
        if data_length > max_bits:
            print(f"数据太大，无法在当前图像和设置下存储。最大: {max_bits//8} 字节，需要: {data_length//8} 字节")
            return False

        for row in range(image.shape[0]):
            for col in range(image.shape[1]):
                for channel in range(self.channel_count):
                    pixel_value = image[row, col, channel]
                    
                    # 处理每个像素的多个最低位
                    for bit_pos in range(self.lsb_count):
                        if data_index < data_length:
                            # 获取当前要编码的位
                            bit_to_encode = (ord(data[data_index // 8]) >> (7 - (data_index % 8))) & 1
                            
                            # 清除当前位位置上的值并设置新位
                            bit_mask = 1 << bit_pos
                            pixel_value = (pixel_value & ~bit_mask) | (bit_to_encode << bit_pos)
                            
                            data_index += 1
                    
                    image[row, col, channel] = pixel_value
                    
                    # 如果所有数据都已编码，提前退出
                    if data_index >= data_length:
                        break
                        
                if data_index >= data_length:
                    break
                    
            if data_index >= data_length:
                break

        cv2.imwrite(output_path, image)
        return True

    def decode(self, image_path):
        """
        从图像中提取隐藏数据
        
        参数:
            image_path (str): 包含隐藏数据的图像路径
        
        返回:
            str: 提取的数据
        """
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像: {image_path}")
            return ""
            
        data = ''
        current_byte = 0
        bits_collected = 0
        eof_marker = 'EOF'
        eof_index = 0

        for row in range(image.shape[0]):
            for col in range(image.shape[1]):
                for channel in range(self.channel_count):
                    pixel_value = image[row, col, channel]
                    
                    # 从每个像素的多个最低位提取数据
                    for bit_pos in range(self.lsb_count):
                        # 提取当前位
                        bit = (pixel_value >> bit_pos) & 1
                        current_byte = (current_byte << 1) | bit
                        bits_collected += 1

                        if bits_collected == 8:
                            char = chr(current_byte)
                            data += char
                            
                            # 检查是否到达EOF标记
                            if char == eof_marker[eof_index]:
                                eof_index += 1
                                if eof_index == len(eof_marker):
                                    # 删除EOF标记
                                    return data[:-len(eof_marker)]
                            else:
                                eof_index = 0
                                
                            current_byte = 0
                            bits_collected = 0

        return data  # 返回在到达EOF标记前收集的所有数据


# lsb = LSBSteganography(channel_count=3, lsb_count=2)
# lsb.encode('random.png', 'Secret Message', 'output_image.png')
# message = lsb.decode('output_image.png')
# print(message)