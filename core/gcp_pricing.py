import requests

class GCPPricing:

    def get_price(self, service_name, region="global", usage=1):

        # lightweight pricing approximation layer
        pricing_map = {
            "bigquery": 0.02,
            "gcs": 0.023,
            "pubsub": 0.015
        }

        for k in pricing_map:
            if k in service_name.lower():
                return pricing_map[k] * usage

        return 0.01 * usage
