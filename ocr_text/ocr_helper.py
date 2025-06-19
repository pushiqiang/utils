
import os
import json
import base64
import hashlib
import shutil
import asyncio
import filetype
import numpy as np

from io import BytesIO
from PIL import Image


_ocr = None


def _create_ocr():
    from paddleocr import PaddleOCR
    # 初始化 PaddleOCR 实例，device="gpu", 通过 device 参数使得在模型推理时使用 GPU
    return PaddleOCR(
        # 设置文本检测模型路径
        text_detection_model_name='PP-OCRv5_server_det',
        # 设置文本识别模型路径
        text_recognition_model_name='PP-OCRv5_server_rec',

        # 文档方向分类模型 默认true 检测整个文档图像的方向并纠正（即0度，90度，180度，270度）。
        use_doc_orientation_classify=False,
        # 文本图像矫正模型 默认true 纠正图像中的透视变形或弯曲，使文档看起来像是正面拍摄的平面图像。
        use_doc_unwarping=False,
        # 文本行方向分类模型 默认true 识别文本行是水平排列还是垂直排列。
        use_textline_orientation=True,

        # https://github.com/PaddlePaddle/PaddleOCR/issues/15455
        text_det_unclip_ratio=1.2,
        text_det_limit_side_len=1080,
        text_det_limit_type='max',

        # 文本识别阈值，得分大于该阈值的文本结果会被保留。 大于0的任意浮点数。如果不设置，将默认使用产线初始化的该参数值 0.0。即不设阈值。
        text_rec_score_thresh=0.5
    )


def get_paddle_ocr():
    global _ocr
    if _ocr is None:
        _ocr = _create_ocr()

    return _ocr


class PaddleImageHelper:
    def __init__(self, img_bytes: bytes):
        self._img_bytes = img_bytes
        self._sha1 = None
        self.mime = None
        self.extension = None
        self._check_image_mime(img_bytes)

        self.img = Image.open(BytesIO(img_bytes))
        self.img_np = np.array(self.img)

        self.text = None

    def save(self, path):
        """
        保存图片
        """
        self.img.save(path)

    @property
    def filename(self):
        return f"{self.sha1}.{self.extension}"

    @property
    def bytes_io(self):
        return BytesIO(self._img_bytes)

    @property
    def sha1(self):
        if not self._sha1:
            self._sha1 = hashlib.sha1(self._img_bytes).hexdigest()

        return self._sha1

    def _check_image_mime(self, img: bytes):
        kind = filetype.guess(img)
        if kind:
            self.mime = kind.mime
            self.extension = kind.extension

    @classmethod
    def from_base64(cls, base64_str: str):
        """
        加载 base64 编码的图片数据
        """
        return cls(img_bytes=base64.b64decode(base64_str))

    @classmethod
    def from_bytes(cls, img_bytes: bytes):
        """
        加载 bytes 格式的图片数据
        """
        return cls(img_bytes=img_bytes)

    @classmethod
    def from_path(cls, img_path: str):
        """
        通过路径加载图片
        """
        with open(img_path, "rb") as f:
            img_bytes = f.read()
            return cls(img_bytes=img_bytes)

    def _format_text(self, texts: list) -> str:
        text = "\n".join(texts)
        return text

    async def _predict(self) -> str:
        """
        PaddleOCR 图片 OCR 文本提取
        https://github.com/PaddlePaddle/PaddleOCR
        """
        # 当前飞桨只支持三通道图片格式
        # https://github.com/PaddlePaddle/PaddleOCR/issues/15382
        if self.img.mode == "RGBA":
            self.img_np = np.array(self.img.convert("RGB"))[:, :, ::-1]

        # 对示例图像执行 OCR 推理
        result = get_paddle_ocr().predict(input=self.img_np)

        texts = []
        for res in result:
            texts.extend(res.get("rec_texts"))

        text = self._format_text(texts)
        return text

    async def _shell_predict(self):
        """
        因为使用 python 有内存泄露，所以使用 shell 命令行执行
        https://github.com/PaddlePaddle/PaddleOCR/issues/7823
        """
        data_dir = "/tmp"

        input_path = os.path.join(data_dir, self.filename)
        output_path = os.path.join(data_dir, f"{self.sha1}_output")
        res_path = os.path.join(output_path, f"{self.sha1}_res.json")

        self.save(input_path)

        cmd = ["paddleocr", "ocr",
               "-i", input_path,
               "--use_doc_orientation_classify", "false",
               "--use_doc_unwarping", "false",
               "--use_textline_orientation", "true",
               "--save_path", output_path]

        text = None
        try:
            result = await asyncio.create_subprocess_shell(" ".join(cmd), stderr=asyncio.subprocess.PIPE)
            await result.wait()

            if result.returncode == 0:
                try:
                    with open(res_path, "r") as f:
                        res = json.loads(f.read())
                        text = self._format_text(res.get("rec_texts"))
                except Exception as e:
                    print(f"Get ocr result failed. {e}")
            else:
                print(f"OCR failed. {await result.stderr.read()}")
        finally:
            try:
                os.remove(input_path)
            except Exception as e:
                print(f"Remove input failed. {e}")
            try:
                shutil.rmtree(output_path)
            except Exception as e:
                print(f"Remove output failed. {e}")

        return text

    async def predict(self) -> str:
        return await self._shell_predict()
