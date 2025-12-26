import requests
import json
import hashlib
import os
import webbrowser
from typing import Dict, List, Any, Optional
import renpy

# 自定义异常类
class NoGameFound(Exception): pass
class DownloadNotFound(Exception): pass
class APIError(Exception): pass

class TouchGalCrawler:
    """TouchGal API Ren'Py适配版"""
    
    def __init__(self, cache_dir: str = "touchgal_cache", enable_nsfw: bool = True):
        self.base_url = "https://www.touchgal.us/api"
        self.search_url = f"{self.base_url}/search"
        self.download_url = f"{self.base_url}/patch/resource"
        self.cache_dir = cache_dir
        self.enable_nsfw = enable_nsfw
        self.session = requests.Session()
        self.session.timeout = 15
        
        # 创建缓存目录
        try:
            persistent_dir = renpy.config.basedir
            full_cache_dir = os.path.join(persistent_dir, cache_dir)
            os.makedirs(full_cache_dir, exist_ok=True)
            self.cache_dir = full_cache_dir
        except:
            os.makedirs(cache_dir, exist_ok=True)
    
    def search_game(self, keyword: str, limit: int = 15) -> List[Dict[str, Any]]:
        """搜索游戏信息（增强调试版）"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # 构造查询参数
        query_string = json.dumps([{"type": "keyword", "name": keyword}])
        
        payload = {
            "queryString": query_string,
            "limit": limit,
            "searchOption": {
                "searchInIntroduction": True,
                "searchInAlias": True,
                "searchInTag": True
            },
            "page": 1,
            "selectedType": "all",
            "selectedLanguage": "all",
            "selectedPlatform": "all",
            "sortField": "resource_update_time",
            "sortOrder": "desc",
            "selectedYears": ["all"],
            "selectedMonths": ["all"]
        }
        
        cookies = {"kun-patch-setting-store|state|data|kunNsfwEnable": "sfw"}
        if self.enable_nsfw:
            cookies = {"kun-patch-setting-store|state|data|kunNsfwEnable": "all"}

        try:
            # 调试信息
            print(f"[TouchGal] 正在搜索: {keyword}")
            print(f"[TouchGal] 请求URL: {self.search_url}")
            
            response = self.session.post(
                self.search_url,
                json=payload,
                headers=headers,
                cookies=cookies,
                timeout=15
            )
            
            # 打印响应状态码
            print(f"[TouchGal] 响应状态码: {response.status_code}")
            print(f"[TouchGal] 响应内容前500字符:\n{response.text[:500]}\n")
            
            if response.status_code != 200:
                raise APIError(f"API请求失败: {response.status_code}")
            
            data = response.json()
            
            # 打印数据结构
            print(f"[TouchGal] JSON数据类型: {type(data)}")
            if isinstance(data, dict):
                print(f"[TouchGal] JSON键: {list(data.keys())}")
            
            if not isinstance(data, dict) or "galgames" not in data:
                raise APIError("API返回了无效的数据结构")
            
            games = data["galgames"]
            print(f"[TouchGal] 找到 {len(games)} 个游戏")
            
            if not games:
                raise NoGameFound(f"未找到游戏: {keyword}")
            
            # 保存到缓存
            cache_file = os.path.join(self.cache_dir, f"search_{hashlib.md5(keyword.encode()).hexdigest()[:8]}.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(games, f, ensure_ascii=False, indent=2)
            
            return games
            
        except requests.RequestException as e:
            print(f"[TouchGal] 网络错误: {str(e)}")
            raise APIError(f"网络请求错误: {str(e)}")
        except Exception as e:
            print(f"[TouchGal] 处理错误: {str(e)}")
            raise APIError(f"处理错误: {str(e)}")
    
    def get_downloads(self, patch_id: int) -> List[Dict[str, Any]]:
        """获取游戏下载资源"""
        params = {"patchId": patch_id}
        
        try:
            print(f"[TouchGal] 获取下载资源，ID: {patch_id}")
            response = self.session.get(
                self.download_url,
                params=params,
                timeout=10
            )
            
            print(f"[TouchGal] 下载响应状态码: {response.status_code}")
            
            if response.status_code != 200:
                raise APIError(f"API请求失败: {response.status_code}")
            
            data = response.json()
            
            if not isinstance(data, list):
                raise APIError("API返回了无效的数据结构")
            
            if not data:
                raise DownloadNotFound(f"未找到ID为{patch_id}的下载资源")
            
            print(f"[TouchGal] 找到 {len(data)} 个下载资源")
            
            # 保存到缓存文件
            cache_file = os.path.join(self.cache_dir, f"download_{patch_id}.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return data
            
        except requests.RequestException as e:
            print(f"[TouchGal] 网络错误: {str(e)}")
            raise APIError(f"网络请求错误: {str(e)}")
        except Exception as e:
            print(f"[TouchGal] 处理错误: {str(e)}")
            raise APIError(f"处理错误: {str(e)}")
    
    def download_image(self, url: str) -> Optional[str]:
        """下载图片到本地"""
        if not url:
            return None
        
        filename = hashlib.md5(url.encode()).hexdigest() + ".jpg"
        images_dir = os.path.join(self.cache_dir, "images")
        filepath = os.path.join(images_dir, filename)
        os.makedirs(images_dir, exist_ok=True)
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"[TouchGal] 图片已保存: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"[TouchGal] 图片下载失败: {str(e)}")
            return None

# 创建爬虫实例
crawler = None

def init_crawler(cache_dir="touchgal_cache", enable_nsfw=True):
    """初始化爬虫"""
    global crawler
    try:
        crawler = TouchGalCrawler(cache_dir=cache_dir, enable_nsfw=enable_nsfw)
        return True, "爬虫初始化成功"
    except Exception as e:
        return False, f"爬虫初始化失败: {str(e)}"

def search_games(keyword: str):
    """搜索游戏"""
    if not crawler:
        return False, "爬虫未初始化", []
    
    try:
        games = crawler.search_game(keyword)
        return True, f"找到 {len(games)} 个游戏", games
    except NoGameFound as e:
        return False, str(e), []
    except APIError as e:
        return False, str(e), []
    except Exception as e:
        return False, f"未知错误: {str(e)}", []

def get_download_links(patch_id: int):
    """获取下载链接"""
    if not crawler:
        return False, "爬虫未初始化", []
    
    try:
        downloads = crawler.get_downloads(patch_id)
        return True, f"找到 {len(downloads)} 个下载资源", downloads
    except DownloadNotFound as e:
        return False, str(e), []
    except APIError as e:
        return False, str(e), []
    except Exception as e:
        return False, f"未知错误: {str(e)}", []