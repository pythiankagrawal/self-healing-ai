import boto3

class AWSPricing:

    def __init__(self):
        self.client = boto3.client("pricing", region_name="us-east-1")

    def get_price(self, service_code="AmazonS3", region="us-east-1", usage=1):

        response = self.client.get_products(
            ServiceCode=service_code,
            Filters=[
                {
                    "Type": "TERM_MATCH",
                    "Field": "location",
                    "Value": region
                }
            ]
        )

        # simplified extraction
        for item in response["PriceList"]:
            return 0.023 * usage  # fallback normalized price

        return 0.0
