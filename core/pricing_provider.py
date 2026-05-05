DEFAULTS = {
    "Object Storage": {"size": "100GB"},
    "Compute": {"size": "medium", "os": "Linux"},
    "Data Warehouse": {"size": "small"}
}

CRITICAL_FIELDS = {
    "Compute": ["size"],
    "Object Storage": ["size"],
    "Data Warehouse": ["size"]
}
savitriagrawal96@ollama-vm:~/self-healing-ai/core$ cat pricing_provider.py
class PricingProvider:
    """
    Unified interface for all cloud pricing APIs.
    """

    def get_price(self, service, region, usage):
        raise NotImplementedError
