from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class ScrapybookscrapePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Clean price
        price = adapter.get("Price")
        adapter["Price"] = float(price.replace("£", ""))

        # Validate title
        if not adapter.get("Title"):
            raise DropItem("Missing Title")

        return item
