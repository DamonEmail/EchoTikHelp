import requests
import json
import time
import hashlib
import base64
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Alibaba1688Tester:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://re.1688.com"
        self.api_url = "https://h5api.m.1688.com/h5"
        self.driver = None
        
    def init_browser(self):
        """初始化浏览器"""
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # 调试时可以看到浏览器
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=options)
        
    def close_browser(self):
        if self.driver:
            self.driver.quit()
            
    def test_image_upload(self, image_url: str):
        """测试1688图片上传流程"""
        try:
            print("\n=== 1688图片上传测试 ===")
            
            # 1. 使用Selenium访问1688识图页面
            print("\n1. 访问1688识图页面...")
            self.init_browser()
            self.driver.get(self.base_url)
            
            # 等待页面加载完成
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 获取所有cookies和localStorage
            cookies = self.driver.get_cookies()
            token = self.driver.execute_script('return localStorage.getItem("_m_h5_tk");')
            
            print("\nCookies:")
            for cookie in cookies:
                print(f"{cookie['name']}: {cookie['value']}")
                self.session.cookies.set(cookie['name'], cookie['value'])
            print(f"\nToken: {token}")
            
            # 2. 下载并转换图片
            print("\n2. 下载目标图片...")
            img_response = requests.get(image_url)
            if img_response.status_code != 200:
                raise Exception("图片下载失败")
            
            image_base64 = base64.b64encode(img_response.content).decode('utf-8')
            print(f"图片大小: {len(img_response.content)} 字节")
            print(f"Base64长度: {len(image_base64)}")
            
            # 3. 准备上传数据
            print("\n3. 准备上传数据...")
            timestamp = str(int(time.time() * 1000))
            data = {
                "imageBase64": image_base64,
                "appName": "searchImageUpload",
                "appKey": "pvvljh1grxcmaay2vgpe9nb68gg9ueg2"
            }
            
            # 4. 获取token并计算签名
            m_h5_tk = None
            for cookie in self.session.cookies:
                if cookie.name == '_m_h5_tk':
                    m_h5_tk = cookie.value.split('_')[0]
                    break
            
            if not m_h5_tk:
                raise Exception("获取token失败")
            
            print(f"\n获取到token: {m_h5_tk}")
            
            # 计算签名
            sign_content = f"{m_h5_tk}&{timestamp}&12574478&{json.dumps(data)}"
            sign = hashlib.md5(sign_content.encode('utf-8')).hexdigest()
            
            # 5. 发送上传请求
            print("\n4. 发送上传请求...")
            
            # 构建请求参数
            params = {
                'jsv': '2.6.1',
                'appKey': '12574478',
                't': timestamp,
                'sign': sign,
                'api': 'mtop.1688.imageService.putImage',
                'v': '1.0',
                'type': 'originaljson',
                'dataType': 'jsonp',
                'timeout': '20000',
                'ignoreLogin': 'true',
                'prefix': 'h5api',
                'ecode': '0',
                'jsonpIncPrefix': 'search1688'
            }
            
            # 构建请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://re.1688.com',
                'Referer': 'https://re.1688.com/',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site'
            }
            
            # 发送请求
            upload_url = f"{self.api_url}/mtop.1688.imageservice.putimage/1.0/?{urlencode(params)}"
            print(f"请求URL: {upload_url}")
            
            response = self.session.post(
                upload_url,
                data={'data': json.dumps(data)},
                headers=headers
            )
            
            print(f"\n状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应内容: {response.text[:500]}")
            
        except Exception as e:
            print(f"\n测试过程出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            self.close_browser()

if __name__ == "__main__":
    # 测试图片URL
    test_image = "https://cdn.echotik.shop/39982c57082d96f57ee85dd3d5827104/67d7e62e/product-cover/1012/1730666721212401166_0.jpeg"
    
    tester = Alibaba1688Tester()
    tester.test_image_upload(test_image) 