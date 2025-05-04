
Pytesseract 是一个流行的开源OCR（光学字符识别）工具，用于从图像中提取文本。

## Linux 下安装 tesseract-ocr
```bash
sudo apt-get install tesseract-ocr

# 使用 Tesseract OCR 识别中文需要确保安装了中文语言包
sudo apt-get install tesseract-ocr-chi-sim  # 对于简体中文
sudo apt-get install tesseract-ocr-chi-tra  # 对于繁体中文
```

## Usage
```python
from img_text_extra import image_text_extra

image_file = "./test.png"
image_text = image_text_extra(image_file)
print(image_text)
```
