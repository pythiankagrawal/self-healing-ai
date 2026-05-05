import requests

class AzurePricing:

    BASE_URL = "https://prices.azure.com/api/retail/prices"

    def get_price(self, service_name, region="global", usage=1):

        params = {
            "$filter": f"armRegionName eq '{region}' and serviceName eq '{service_name}'"
        }

        res = requests.get(self.BASE_URL, params=params).json()

        items = res.get("Items", [])

        if not items:
            return 0.0

        price = items[0].get("retailPrice", 0)

        return price * usage
