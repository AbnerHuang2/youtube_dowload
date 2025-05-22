import requests
from bs4 import BeautifulSoup
import json
import time

# 设置请求头，避免反爬
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept-Language': 'ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.emag.ro/',
}

# 获取自动补全关键词（建议词）
def get_search_suggestions(keyword: str):
    url = f"https://emag.ro/search-suggestions?q={keyword}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        try:
            data = resp.json()
            suggestions = [s['term'] for s in data.get('suggestions', [])]
            return suggestions
        except Exception:
            return []
    return []

# 获取商品信息
def get_product_list(keyword: str, page_limit=1):
    base_url = f"https://www.emag.ro/search/{keyword}/p{{}}/c"
    print(f"🔗 请求链接: {base_url}")
    all_products = []

    for page in range(1, page_limit + 1):
        url = base_url.format(page)
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            print(f"❌ 请求失败，状态码: {resp.status_code}")
            break
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.select('.card-item')

        for item in items:
            try:
                title_tag = item.select_one('.card-v2-title')
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True) if title_tag else "无标题"

                price_tag = item.select_one('.product-new-price')
                price = price_tag.get_text(strip=True).replace('\xa0Lei', '') if price_tag else "无价格"

                reviews_tag = item.select_one('.visible-xs-inline-block')
                reviews = reviews_tag.get_text(strip=True) if reviews_tag else "0 recenzii"
                reviews_count = int(''.join(filter(str.isdigit, reviews)))

                link_tag = item.select_one('a.card-v2-title')
                link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "无链接"

                all_products.append({
                    'title': title,
                    'price': price,
                    'reviews': reviews_count,
                    'url': link
                })

            except Exception as e:
                print(f"❌ Error parsing item: {e}")

        print(f"📄 已抓取第 {page} 页商品信息...")
        time.sleep(1)  # 避免被封IP

    return all_products

# 主程序
if __name__ == "__main__":
    keyword = "husa+telefon"
    print(f"🔍 搜索建议词 for '{keyword}':")
    suggestions = get_search_suggestions(keyword)
    print(suggestions)

    print(f"\n📦 正在抓取热销商品（关键词: {keyword}）...")
    products = get_product_list(keyword, page_limit=2)  # 爬前2页
    for i, p in enumerate(products, 1):
        print(f"{i}. {p['title']} | 💰 {p['price']} RON | ⭐ 评论: {p['reviews']} | 🔗 {p['url']}")
