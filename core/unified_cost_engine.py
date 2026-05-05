from core.pricing_config import PRICE_MAP, REGION_MULTIPLIER


class MultiCloudCostEngine:

    def get_cost(self, component, usage=1):

        ctype = component.get("type", "Unknown")
        region = component.get("region", "global")

        base = PRICE_MAP.get(ctype, 0.01)

        multiplier = REGION_MULTIPLIER.get(region, 1.0)

        return base * usage * multiplier
