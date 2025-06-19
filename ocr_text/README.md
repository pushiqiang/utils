

github: https://github.com/PaddlePaddle/PaddleOCR

## Usage
```python
from ocr_helper import PaddleImageHelper

img_base64 = "..."

# helper = PaddleImageHelper.from_bytes(b"...")
# helper = PaddleImageHelper.from_path("./test.jpg")
helper = PaddleImageHelper.from_base64(img_base64)

assert helper.mime == "image/jpeg"
assert helper.sha1 == "1929f48716716ba1968d72f0901d8b94adc781cf"
assert helper.filename == "1929f48716716ba1968d72f0901d8b94adc781cf.jpg"

# text = helper.predict()
# print(text)

```
