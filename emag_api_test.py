import random

import requests

USER_AGENTS = [
    # Chrome - Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
    # Chrome - macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36",
    # Edge - Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.2478.80",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36 Edg/113.0.1774.50",
    # Firefox - Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:114.0) Gecko/20100101 Firefox/114.0",
    # Firefox - macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.4; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.5; rv:114.0) Gecko/20100101 Firefox/114.0",
    # Safari - macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    # Safari - iPhone iOS
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    # Samsung Internet - Android
    "Mozilla/5.0 (Linux; Android 13; SM-G990B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/112.0.5615.138 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/18.0 Chrome/102.0.5005.167 Mobile Safari/537.36"
]


def fetch_emag_products(keyword="husa telefon"):
    headers = {
        'accept': 'application/json',
        'user-agent': random.choice(USER_AGENTS),
        'x-requested-with': 'XMLHttpRequest',
        'x-app-name': 'photon-static',
        'x-app-module': 'SortOptions',
        'x-request-source': 'www',
        'referer': f'https://www.emag.ro/search/{keyword.replace(" ", "%20")}?ref=effective_search'
    }

    params = {
        'source_id': 7,
        'templates[]': 'full',
        'url': f'/search/{keyword.replace(" ", "+")}/sort-popularity_cr_objectivesdesc',
        'sort[reviews]': 'desc',
        'listing_display_id': 2,
        'page[limit]': 120,
        'page[offset]': 0,
        'fields[items][image_gallery][fashion][limit]': 2,
        'fields[items][image][resized_images]': 1,
        'fields[items][resized_images]': '200x200,350x350,720x720',
        'fields[items][flags]': 1,
        'fields[items][offer][buying_options]': 1,
        'fields[items][offer][flags]': 1,
        'fields[items][offer][bundles]': 1,
        'fields[items][offer][gifts]': 1,
        'fields[items][characteristics]': 'listing',
        'fields[quick_filters]': 1
    }

    url = "https://www.emag.ro/search-by-url"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("❌ 请求失败，状态码：", response.status_code)
        return []

    data = response.json()
    # 响应json写入文件中
    with open("response.json", "w", encoding="utf-8") as f:
        f.write(response.text)
    items = data.get("data").get("items", [])

    products = []
    for item in items:
        # id
        item_id = item.get("id", "N/A")
        name = item.get("name", "N/A")
        part_number_key = item.get("part_number_key", "N/A")
        category_tags = item.get("category", {}).get("tags", [])
        # 受欢迎标签
        # 从item.get("unified_badges", [])返回的对象数组中获取到每个item的label值放入到unified_badges_tags
        unified_badges_tags = [badge.get("label") for badge in item.get("offer", {}).get("unified_badges", [])]
        # 改商品有多少个不同的卖家
        multiple_offers_count = item.get("multiple_offers_count", 0)
        # 该商品有多少个不同的卖家（包括二手）
        offers_count = item.get("offers_count", 0)
        price = item.get("offer", {}).get("price", {}).get("current", 0)
        price_before_tax = item.get("offer", {}).get("price", {}).get("net", 0)
        rating = item.get("feedback", {}).get("rating", 0)
        reviews = item.get("feedback", {}).get("reviews", {}).get("count", 0)
        questions = item.get("feedback", {}).get("questions", {}).get("count", 0)
        answers = item.get("feedback", {}).get("answers", 0)
        url_path = item.get("url", "").get("path", "")
        product_url = f"https://www.emag.ro{url_path}"
        popularity_score = round(rating * reviews, 2)

        products.append({
            "id": item_id,
            "name": name,
            "part_number_key": part_number_key,
            "category_tags": category_tags,
            "unified_badges_tags": unified_badges_tags,
            "multiple_offers_count": multiple_offers_count,
            "offers_count": offers_count,
            "price": price,
            "price_before_tax": price_before_tax,
            "rating": rating,
            "reviews": reviews,
            "questions": questions,
            "answers": answers,
            "product_url": product_url,
            "popularity_score": popularity_score
        })

    return sorted(products, key=lambda x: x["reviews"], reverse=True)

def main():
    keyword = "suport si docking telefoane" # husa telefon 手机壳
    products = fetch_emag_products(keyword)

    if not products:
        print("⚠️ 没有获取到商品数据")
        return
    # 展示 refer对应的url
    print(f"🔗 请求链接: https://www.emag.ro/search/{keyword.replace(' ', '%20')}?ref=effective_search")
    print(f"🔗 最受欢迎: https://www.emag.ro/search/{keyword.replace(' ', '%20')}/sort-popularity_cr_objectivesdesc")
    print(f"🔗 按评论数排序: https://www.emag.ro/search/{keyword.replace(' ', '%20')}/sort-reviewsdesc")
    print("🔥 Top 10 受欢迎商品（按评论数排序）:")
    for idx, product in enumerate(products[:10], start=1):
        print(f"\n#{idx}")
        print(f"ID: {product['id']}")
        print(f"名称: {product['name']}")
        print(f"型号: {product['part_number_key']}")
        print(f"分类标签: {', '.join(product['category_tags'])}")
        print(f"受欢迎标签: {', '.join(product['unified_badges_tags'])}")
        print(f"卖家数量: {product['multiple_offers_count']}")
        print(f"总卖家数量: {product['offers_count']}")
        print(f"价格: {product['price']} RON")
        print(f"税前价格: {product['price_before_tax']} RON")
        print(f"评分: {product['rating']} / 5")
        print(f"评论数: {product['reviews']}")
        print(f"问题数: {product['questions']}")
        print(f"回答数: {product['answers']}")
        print(f"详情页: {product['product_url']}")
        print(f"受欢迎程度评分: {product['popularity_score']}")

# 调用商品api获取商品信息
if __name__ == "__main__":
    main()
