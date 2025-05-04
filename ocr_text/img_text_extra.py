import cv2
from PIL import Image
import pytesseract


def image_text_extra(img_path: str):
    """图片文本提取"""
    img =cv2.imread(img_path)
    if img is None:
        print(f'Error: Image not found or cannot be loaded. image path: {img_path}')
        return None

    # 将图片转换为灰度图
    gray_img =cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 对灰度图进行二值化处理
    binary_img = cv2.adaptiveThreshold(
        gray_img,
        maxValue=255,  # 最大白色值，二值化后像素最大值
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # 取邻域的高斯加权平均值（权重中心更高）
        thresholdType=cv2.THRESH_BINARY,  # 常规黑白
        blockSize=15,  # 邻域大小（必须是奇数），小可能导致噪点多，过大则考虑的范围越大，但处理越模糊
        C=10  # 调节亮暗，从计算出的局部阈值中减去一个偏移量,减10微调，避免过亮或过暗。
    )
    # 降噪 binary_img = cv2.fastNlMeansDenoising(binary_img)

    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
    # --oem：OCR引擎模式
    #   oem 0: 传统引擎;
    #   oem 1: LSTM 神经网络;
    #   oem 2: 混合模式;
    #   oem 3：默认模式，让 Tesseract 自动选择最佳模式
    # --psm：页面分割模式。
    #   psm 3：默认模式，适用于普通文本；
    #   psm 6: 适用于单行文本；
    #   psm 11：适用于稀疏文本
    # preserve_interword_spaces 用于控制如何处理图像中单词之间的空格。
    #   设置为 1 时：保留原始空格布局
    #   设置为 0 时：使用 Tesseract 的标准空格处理逻辑

    # 使用 pytesseract 进行OCR识别, lang: 英文：eng、中文简体：chi_sim
    text = pytesseract.image_to_string(Image.fromarray(binary_img), lang='eng+chi_sim', config=custom_config)
    return text


if __name__ == "__main__":
    image_file = "./test.png"
    image_text = image_text_extra(image_file)
    print(image_text)
