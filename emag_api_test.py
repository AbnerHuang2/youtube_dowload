import requests

def fetch_emag_products(keyword="husa telefon"):
    headers = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0',
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
    items = data.get("data").get("items", [])

    products = []
    for item in items:
        # id
        item_id = item.get("id", "N/A")
        name = item.get("name", "N/A")
        category_tags = item.get("category", {}).get("tags", [])
        price = item.get("offer", {}).get("price", {}).get("current", 0)
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
            "category_tags": category_tags,
            "price": price,
            "rating": rating,
            "reviews": reviews,
            "questions": questions,
            "answers": answers,
            "product_url": product_url,
            "popularity_score": popularity_score
        })

    return sorted(products, key=lambda x: x["reviews"], reverse=True)

def main():
    keyword = "husa telefon"
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
        print(f"分类标签: {', '.join(product['category_tags'])}")
        print(f"价格: {product['price']} RON")
        print(f"评分: {product['rating']} / 5")
        print(f"评论数: {product['reviews']}")
        print(f"问题数: {product['questions']}")
        print(f"回答数: {product['answers']}")
        print(f"详情页: {product['product_url']}")
        print(f"受欢迎程度评分: {product['popularity_score']}")

# 调用商品api获取商品信息
if __name__ == "__main__":
    main()
