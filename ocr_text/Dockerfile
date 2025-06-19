# 官方镜像基于 python3.10.13
FROM ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddle:3.0.0

ENV PROJECT_NAME='image-ocr'

RUN apt-get update && apt-get install -y vim

ADD ./requirements.txt /image-ocr/requirements.txt
RUN pip install -r /image-ocr/requirements.txt

# 先调用一次，下载并加载模型
# RUN python -c "from paddleocr import PaddleOCR; PaddleOCR()"
