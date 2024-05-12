import scrapy
import json
from poizonscraper.items import ProductItems
from poizonscraper.spiders.items_list_file import list_of_items


class PoizonspiderSpider(scrapy.Spider):
    name = "poizonspider"
    allowed_domains = ["poizon.com"]
    start_urls = ["https://poizon.com"]
    url_count = 1

    def parse(self, response):
        for link in list_of_items:
            print("Start URL =================================")
            yield scrapy.Request(url=link, callback=self.parse_product_items)

    def parse_product_items(self, response):
        script_text = response.css("script#__NEXT_DATA__::text").get()
        script_data = json.loads(script_text)
        spu_list = script_data.get("props", {}).get("pageProps", {}).get("spuList", [])

        for spu_link in spu_list:
            spu_id = spu_link.get("spuId")
            if spu_id:
                product_item_details_url = f"https://www.poizon.com/product/{spu_id}"
                yield scrapy.Request(
                    url=product_item_details_url,
                    callback=self.parse_product_item_details,
                )

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

                yield scrapy.Request(
                    url=next_page_url, callback=self.parse_product_items
                )
        else:
            pass
            # self.logger.info("No pagination items found. Ending parsing.")

    def parse_product_item_details(self, response):
        script_text = response.css("script#__NEXT_DATA__::text").get()
        script_data = json.loads(script_text)
        spu_item_details = (
            script_data.get("props", {}).get("pageProps", {}).get("goodsDetail", {})
        )

        item = ProductItems()
        item["Name"] = spu_item_details.get("detail", {}).get("title")
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


# import scrapy
# import json
# from poizonscraper.items import ProductItems
# from poizonscraper.spiders.items_list_file import list_of_items


# class PoizonspiderSpider(scrapy.Spider):
#     name = "poizonspider"
#     allowed_domains = ["poizon.com"]
#     start_urls = ["https://poizon.com"]
#     url_count = 1

#     # def parse(self, response):
#     #     for index, link in enumerate(list_of_items):
#     #         yield scrapy.Request(url=link, callback=self.parse_product_items)
#     #         print(f"Processing URL {index+1}: {link}")  # Print for reference
#             # self.parse_product_items(response=response, url=link)


#     def parse(self, response):
#     # Recursively iterate through the list_of_items
#         for index, link in enumerate(list_of_items):
#             yield scrapy.Request(url=link, callback=self.parse_link)

#     def parse_link(self, response):
#         for index, link in enumerate(response.meta.get('list_of_items', list_of_items)):
#             print(f"Processing URL {index+1}: {link}")  # Print for reference
#             yield scrapy.Request(url=link, callback=self.parse_product_items)

#         # Call parse function again for next link in the list (if any)
#         next_link_index = response.meta.get('list_of_items_index', 0) + 1
#         if next_link_index < len(list_of_items):
#             yield scrapy.Request(
#                 url=self.start_urls[0],  # Use the first url to trigger parse again
#                 callback=self.parse,
#                 meta={'list_of_items': list_of_items[next_link_index:], 'list_of_items_index': next_link_index}
#             )


#     def parse_product_items(self, response):
#         script_text = response.css("script#__NEXT_DATA__::text").get()
#         if not script_text:
#             self.logger.warning(f"No script data found for URL: {response.url}")
#             return

#         try:
#             script_data = json.loads(script_text)
#             spu_list = (
#                 script_data.get("props", {}).get("pageProps", {}).get("spuList", [])
#             )
#         except json.JSONDecodeError:
#             self.logger.error(f"Failed to parse JSON data for URL: {response.url}")
#             return

#         for spu_link in spu_list:
#             spu_id = spu_link.get("spuId")
#             if spu_id:
#                 product_item_details_url = f"https://www.poizon.com/product/{spu_id}"
#                 yield scrapy.Request(
#                     url=product_item_details_url,
#                     callback=self.parse_product_item_details,
#                 )

#         page_items = response.css("li.ant-pagination-item")

#         # Check if page_items is available
#         if page_items:
#             # Extract the titles of these list items
#             titles = page_items.css("::attr(title)").getall()

#             # Filter out non-numeric titles and convert them to integers
#             page_numbers = [int(title) for title in titles if title.isdigit()]

#             # Find the maximum page number
#             max_page_number = max(page_numbers)

#             if self.url_count <= max_page_number:
#                 # Increment the page count
#                 self.url_count += 1

#                 # Modify the URL to go to the next page
#                 if "page" in response.url:
#                     next_page_url = response.url.replace(
#                         f"page={self.url_count - 1}", f"page={self.url_count}"
#                     )
#                 else:
#                     next_page_url = f"{response.url}&page={self.url_count}"

#                 yield scrapy.Request(
#                     url=next_page_url, callback=self.parse_product_items
#                 )

#     def parse_product_item_details(self, response):
#         script_text = response.css("script#__NEXT_DATA__::text").get()
#         if not script_text:
#             self.logger.warning(f"No script data found for URL: {response.url}")
#             return

#         try:
#             script_data = json.loads(script_text)
#             spu_item_details = (
#                 script_data.get("props", {}).get("pageProps", {}).get("goodsDetail", {})
#             )
#         except json.JSONDecodeError:
#             self.logger.error(f"Failed to parse JSON data for URL: {response.url}")
#             return

#         item = ProductItems()
#         item["Name"] = spu_item_details.get("detail", {}).get("title")
#         item["Categories"] = spu_item_details.get("detail", {}).get("frontCategoryName")
#         item["Color"] = {"Black": {"Sizes": {}}}
#         item["Images"] = [
#             image.get("url") for image in spu_item_details.get("imageModels", [])
#         ]
#         item["Link"] = response.url
#         item["SpuId"] = spu_item_details.get("detail", {}).get("spuId")
#         item["CategoryId"] = spu_item_details.get("detail", {}).get("categoryId")
#         item["Brand"] = spu_item_details.get("detail", {}).get("brandName")
#         item["Vendor"] = "HS9528"
#         yield item
