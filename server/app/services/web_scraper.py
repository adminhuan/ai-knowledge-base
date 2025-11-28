import re
import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict
from urllib.parse import urlparse


class WebScraper:
    """网页抓取服务"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.timeout = 15.0
    
    @staticmethod
    def is_valid_url(text: str) -> bool:
        """检查是否为有效URL"""
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(text.strip()))
    
    @staticmethod
    def extract_url(text: str) -> Optional[str]:
        """从文本中提取URL"""
        # 更完善的URL匹配，支持路径中的各种字符
        url_pattern = re.compile(
            r'https?://'
            r'[^\s<>\"\'\u4e00-\u9fff]+',  # 匹配到空格、引号或中文前
            re.IGNORECASE)
        match = url_pattern.search(text)
        if match:
            url = match.group(0)
            # 清理末尾可能的标点符号
            url = url.rstrip('.,;:!?')
            return url
        return None
    
    async def fetch_url(self, url: str) -> Dict:
        """抓取网页内容（使用 Jina Reader API 支持 JS 渲染）"""
        try:
            # 优先使用 Jina Reader API（支持 JS 渲染，免费）
            jina_url = f"https://r.jina.ai/{url}"
            async with httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True
            ) as client:
                response = await client.get(jina_url)
                
                if response.status_code == 200:
                    content = response.text
                    # 解析 Jina 返回的 Markdown 格式
                    lines = content.split('\n')
                    title = ""
                    body_lines = []
                    in_content = False
                    
                    for line in lines:
                        if line.startswith('Title:'):
                            title = line[6:].strip()
                        elif line.startswith('Markdown Content:'):
                            in_content = True
                        elif in_content:
                            body_lines.append(line)
                    
                    body = '\n'.join(body_lines).strip()
                    if len(body) > 8000:
                        body = body[:8000] + "\n\n[内容已截断...]"
                    
                    return {
                        'success': True,
                        'title': title,
                        'url': url,
                        'content': body
                    }
                
                # Jina 失败则回退到原始方法
                return await self._fetch_url_fallback(url)
                
        except Exception as e:
            # 出错时回退到原始方法
            return await self._fetch_url_fallback(url)
    
    async def _fetch_url_fallback(self, url: str) -> Dict:
        """回退：直接抓取网页"""
        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '')
                if 'text/html' not in content_type and 'text/plain' not in content_type:
                    return {
                        'success': False,
                        'error': f'不支持的内容类型: {content_type}'
                    }
                
                html = response.text
                return self._parse_html(html, url)
                
        except httpx.TimeoutException:
            return {'success': False, 'error': '请求超时'}
        except httpx.HTTPStatusError as e:
            return {'success': False, 'error': f'HTTP错误: {e.response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': f'抓取失败: {str(e)}'}
    
    def _parse_html(self, html: str, url: str) -> Dict:
        """解析HTML内容"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除脚本和样式
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'iframe']):
            tag.decompose()
        
        # 获取标题
        title = ''
        if soup.title:
            title = soup.title.string or ''
        if not title:
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
        
        # 获取正文内容
        content = ''
        
        # 尝试找到主要内容区域
        main_content = (
            soup.find('article') or 
            soup.find('main') or 
            soup.find(class_=re.compile(r'(content|article|post|entry|main)', re.I)) or
            soup.find(id=re.compile(r'(content|article|post|entry|main)', re.I)) or
            soup.body
        )
        
        if main_content:
            # 获取所有段落文本
            paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li', 'td', 'th', 'span', 'div'])
            texts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 10:
                    texts.append(text)
            content = '\n\n'.join(texts)
        
        if not content:
            content = soup.get_text(separator='\n', strip=True)
        
        # 清理内容
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)
        
        # 限制长度（避免token过多）
        max_length = 8000
        if len(content) > max_length:
            content = content[:max_length] + '\n\n[内容已截断...]'
        
        # 获取域名
        domain = urlparse(url).netloc
        
        return {
            'success': True,
            'url': url,
            'domain': domain,
            'title': title.strip(),
            'content': content.strip(),
            'length': len(content)
        }


web_scraper = WebScraper()
