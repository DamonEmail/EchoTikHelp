import requests
import json
import time
import os
from datetime import datetime
import random
from typing import Dict, List, Optional
import re

class EchoTikCrawler:
    def __init__(self):
        """
        初始化爬虫类
        - 设置API接口地址
        - 配置请求头（包含必要的Cookie）
        - 创建数据存储目录
        - 设置请求相关的配置参数
        """
        # API接口地址
        self.base_url = "https://echotik.live/api/v1/data/products"
        
        # 请求头配置
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'x-lang': 'zh-CN',
            'x-region': 'MY',
            'x-currency': 'MYR',
            'authorization': 'Bearer 1011344|Z2qaaigWhNiaJDi9gW6C893duB0IjMaNjfQTBakg',
            'origin': 'https://echotik.live',
            'referer': 'https://echotik.live/products',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'Cookie': 'AGL_USER_ID=0c5a07a3-bf42-4ac8-986f-9adf9e792528; is_first_visit=false; lang=zh-CN; region=MY; currency=MYR; token=1001653|uUEgbEJ94aDJ8OmOcEE6Dhi4P1NEPHTJTwI8v8bk'
        }
        
        # 创建数据存储目录
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 请求配置
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 5  # 重试等待时间（秒）
        self.request_delay = (1, 3)  # 修改为1-3秒的随机延迟
        
        # 添加默认的请求参数
        self.default_params = {
            'page': '1',
            'per_page': '50',
            'product_categories': '',  # 可选
            'keyword': '',            # 新增关键词搜索支持
            'price': '',
            'commission_rate': '',
            'related_influencers': '',
            'videos_count': '',
            'views_count': '',
            'dateRange': '7',
            'order': 'total_sale_nd_cnt',
            'sort': 'desc'
        }

    def update_cookie(self, cookie: str = None):
        """更新Cookie和authorization"""
        if cookie:
            self.headers['Cookie'] = cookie
            # 从cookie中提取token
            token_match = re.search(r'token=([^;]+)', cookie)
            if token_match:
                token = token_match.group(1)
                self.headers['authorization'] = f'Bearer {token}'

    def _make_request(self, params: Dict) -> Optional[Dict]:
        """
        发送API请求并处理响应
        """
        for attempt in range(self.max_retries):
            try:
                # 随机延迟
                time.sleep(random.uniform(*self.request_delay))
                
                # 打印详细的请求信息
                print("\n" + "="*50)
                print("请求信息:")
                print(f"URL: {self.base_url}")
                print(f"参数: {json.dumps(params, indent=2, ensure_ascii=False)}")
                print(f"请求头: {json.dumps(self.headers, indent=2, ensure_ascii=False)}")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                
                # 打印响应信息
                print("\n响应信息:")
                print(f"状态码: {response.status_code}")
                print(f"响应头: {json.dumps(dict(response.headers), indent=2, ensure_ascii=False)}")
                
                # 尝试解析响应内容
                try:
                    data = response.json()
                    print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)[:2000]}...")  # 显示前2000个字符
                    
                    # 检查响应状态
                    if response.status_code == 200:
                        if data.get('data') and isinstance(data['data'], list):
                            print(f"✓ 成功获取数据，共 {len(data['data'])} 条记录")
                            return data
                        else:
                            print("× API返回格式异常:")
                            print(f"  - code: {data.get('code')}")
                            print(f"  - message: {data.get('msg')}")
                            print(f"  - 完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"× HTTP状态码异常: {response.status_code}")
                        if data:
                            print(f"  错误信息: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                except json.JSONDecodeError:
                    print("× 响应内容不是有效的JSON格式")
                    print(f"原始响应内容: {response.text[:1000]}...")
                    
                # 检查是否需要更新Cookie
                if response.status_code == 401 or 'token expired' in response.text.lower():
                    print("× Token已过期，需要更新Cookie")
                    self.update_cookie()
                    continue
                
            except requests.RequestException as e:
                print(f"× 请求异常 (尝试 {attempt + 1}/{self.max_retries}):")
                print(f"  - 错误类型: {type(e).__name__}")
                print(f"  - 错误信息: {str(e)}")
                if attempt < self.max_retries - 1:
                    print(f"  等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                continue
            
        print("× 所有重试都失败了")
        return None

    def _save_data(self, all_products: List[Dict]):
        """
        保存商品数据到JSON文件，保留所有基础字段，排除复杂对象字段
        """
        simplified_products = []
        for product in all_products:
            # 创建一个新的字典来存储所有基础字段
            simplified_product = {}
            
            # 排除这些复杂对象字段
            exclude_fields = {'seller', 'sale_props', 'skus', 'sales_trending'}
            
            # 复制所有非复杂对象的字段
            for key, value in product.items():
                if key not in exclude_fields:
                    simplified_product[key] = value
            
            simplified_products.append(simplified_product)
        
        # 生成文件名（使用日期、分类和关键词）
        filename_parts = ['products']
        if self.default_params.get('product_categories'):
            filename_parts.append(f"cat{self.default_params['product_categories']}")
        if self.default_params.get('keyword'):
            filename_parts.append(f"kw{self.default_params['keyword']}")
        filename_parts.append(datetime.now().strftime("%Y%m%d"))
        
        filename = os.path.join(self.data_dir, '_'.join(filename_parts) + '.json')
        
        # 如果文件已存在，读取已有数据并合并
        existing_products = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_products = json.load(f)
            except json.JSONDecodeError:
                pass
        
        # 合并数据并去重（基于product_id）
        all_products_dict = {p['product_id']: p for p in existing_products + simplified_products}
        final_products = list(all_products_dict.values())
        
        # 保存数据
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_products, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到: {filename}")
        print(f"当前文件共包含 {len(final_products)} 个商品数据")

    def crawl(self, start_page: int = 1, end_page: int = None):
        """
        爬取商品数据，实时保存到文件
        """
        current_page = start_page
        saved_count = 0
        
        try:
            while True:
                print(f"正在爬取第 {current_page} 页...")
                
                params = {
                    **self.default_params,
                    'page': current_page
                }
                
                response_data = self._make_request(params)
                if not response_data:
                    print(f"爬取第 {current_page} 页失败，跳过")
                    break
                    
                products = response_data.get('data', [])
                if not products:
                    print("没有更多数据")
                    break
                
                # 立即保存本页数据
                self._save_data(products)
                saved_count += len(products)
                print(f"已保存 {saved_count} 条商品数据")
                
                # 获取总页数和总数据量
                meta = response_data.get('meta', {})
                total_pages = meta.get('last_page', 0)
                total_items = meta.get('total', 0)
                print(f"总数据量: {total_items}, 总页数: {total_pages}")
                
                # 检查是否达到结束页
                if end_page and current_page >= end_page:
                    print("已达到指定的结束页码")
                    break
                    
                # 检查是否是最后一页
                if current_page >= total_pages:
                    print("已到达最后一页")
                    break
                    
                current_page += 1
                
        except KeyboardInterrupt:
            print("\n用户中断爬取")
            print(f"已保存 {saved_count} 条数据")
        except Exception as e:
            print(f"程序异常: {str(e)}")
            print(f"已保存 {saved_count} 条数据")
        
        print(f"爬取完成，共保存 {saved_count} 条商品数据")
        return saved_count

def main():
    """主函数"""
    try:
        crawler = EchoTikCrawler()
        # 不指定end_page，爬取所有数据
        crawler.crawl(start_page=1)
    except Exception as e:
        print(f"程序异常: {str(e)}")

if __name__ == "__main__":
    main() 