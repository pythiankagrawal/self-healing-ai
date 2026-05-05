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
