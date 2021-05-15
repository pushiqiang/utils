## Dockerfile常用模板
### Dockerfile_template

### Dockerfile_selenium_python3

```python
# pip3 install selenium beautifulsoup4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options, executable_path='/usr/bin/chromedriver')

driver.get(url='url')
self.driver.execute_script('window.scrollBy(0,500)')

html = self.driver.page_source
soup = BeautifulSoup(html, 'lxml')

```

## 给正在运行的Docker容器动态绑定卷组（动态添加Volume）

需求：将物理机的目录`/tmp/test`挂载到正在运行的容器test（test容器id：955138b6c3ed）中的`/src`目录


```
$ chmod +x dynamic_mount_docker_volume
$ docker run --rm -v /usr/local/bin:/target jpetazzo/nsenter
$ ./dynamic_mount_docker_volume 955138b6c3ed /tmp/test /src

```

命令说明：

1. 给dynamic_mount_docker_volume赋可执行权限

2. 下载nsenter 参见：https://github.com/jpetazzo/nsenter

3. 执行脚本给运行的容器挂载卷


## subprocess.Popen 实时获取docker events事件

python event_monitor.py
