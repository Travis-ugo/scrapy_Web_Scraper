import scrapy
import json
from poizonscraper.items import ProductItems
from poizonscraper.poizonscraper.spiders.poizon_urls import poizon_urls


class PoizonspiderSpider(scrapy.Spider):
    name = "poizonspider"
    allowed_domains = ["poizon.com"]
    start_urls = ["https://poizon.com"]
    url_count = 1

    redis_key = "products_queue:start_urls"
    # Number of url to fetch from redis on each attempt
    redis_batch_size = 1
    # Max idle time(in seconds) before the spider stops checking redis and shuts down
    max_idle_time = 7

    keyword_fetch_list = ["Revenge", "JRs"]
    keyword_list = ["Mizuno+coat"]

    def start_requests(self):
        for keyword in self.keyword_list:
            poizon_search_url = f"https://www.poizon.com/search?keyword={keyword}"

            yield scrapy.Request(
                url=poizon_search_url, callback=self.parse, meta={"keyword": keyword}
            )

    def parse(self, response):
        print(f"URL: {response.url}")

        script_text = response.css("script#__NEXT_DATA__::text").get()
        script_data = json.loads(script_text)
        spu_list = script_data.get("props", {}).get("pageProps", {}).get("spuList", [])

        items = response.css(".GoodsList_goodsList__hPoCW .GoodsItem_goodsItem__pfNZb")

        for item in items:
            title = item.css(".GoodsItem_spuTitle__ED79N::text").get()
            link = item.css("::attr(href)").get()
            product_item_details_url = f"https://www.poizon.com{link}"
            yield scrapy.Request(
                url=product_item_details_url,
                callback=self.parse_product_item_details,
            )

        # for spu_link in spu_list:
        #     spu_id = spu_link.get("spuId")
        #     if spu_id:
        #         product_item_details_url = f"https://www.poizon.com/product/{spu_id}"
        #         yield scrapy.Request(
        #             url=product_item_details_url,
        #             callback=self.parse_product_item_details,
        #         )

        page_items = response.css("li.ant-pagination-item")

        # Check if page_items is available
        if page_items:
            # Extract the titles of these list items
            titles = page_items.css("::attr(title)").getall()

            # Filter out non-numeric titles and convert them to integers
            page_numbers = [int(title) for title in titles if title.isdigit()]

            # Find the maximum page number
            max_page_number = max(page_numbers)

            if self.url_count <= max_page_number:
                # Increment the page count
                self.url_count += 1

                # Modify the URL to go to the next page
                if "page" in response.url:
                    next_page_url = response.url.replace(
                        f"page={self.url_count - 1}", f"page={self.url_count}"
                    )
                else:
                    next_page_url = f"{response.url}&page={self.url_count}"

                yield scrapy.Request(url=next_page_url, callback=self.parse)
        else:
            pass
            # self.logger.info("No pagination items found. Ending parsing.")

        if self.keyword_fetch_list:
            self.keyword_list.pop(0)
            if not self.keyword_list:
                if self.keyword_fetch_list:
                    self.keyword_list.append(self.keyword_fetch_list.pop(0))
                    print(f"Keyword fetch: {self.keyword_fetch_list}")
                    print(f"Keyword: {self.keyword_list}")
                    yield from self.start_requests()

    def parse_product_item_details(self, response):
        script_text = response.css("script#__NEXT_DATA__::text").get()
        script_data = json.loads(script_text)
        spu_item_details = (
            script_data.get("props", {}).get("pageProps", {}).get("goodsDetail", {})
        )

        title = response.css(".MainInfo_title__YSsXk::text").get()

        # Using CSS selector to select the price
        price = response.css(".MainInfo_priceBar__tcUgc div::text").get()

        img_elements = response.css(".ImageSkeleton_skeleton__yq_Y9 img")

        # Printing the title and price
        # print("Title:", title.strip())  # Use strip() to remove leading and trailing whitespaces if needed
        # print("Price:", price.strip())

        item = ProductItems()
        item["Name"] = title.strip()  # spu_item_details.get("detail", {}).get("title")
        item["Categories"] = spu_item_details.get("detail", {}).get("frontCategoryName")
        item["Color"] = {"Black": {"Sizes": {}}}
        item["Images"] = [
            image.get("url") for image in spu_item_details.get("imageModels", [])
        ]
        item["Link"] = response.url
        item["SpuId"] = spu_item_details.get("detail", {}).get("spuId")
        item["CategoryId"] = spu_item_details.get("detail", {}).get("categoryId")
        item["Brand"] = spu_item_details.get("detail", {}).get("brandName")
        item["Vendor"] = "HS9528"
        yield item
