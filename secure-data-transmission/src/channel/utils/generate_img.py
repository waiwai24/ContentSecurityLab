# 随机生成一张rgb不规则图并保存
import cv2
import numpy as np

def generate_random_img(width, height):
    texture = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            r = np.random.randint(0, 256)
            g = np.random.randint(0, 256)
            b = np.random.randint(0, 256)
            texture[i, j] = [b, g, r]
    cv2.imwrite('tmp/random.png', texture)

# generate_random_img(240, 240)


