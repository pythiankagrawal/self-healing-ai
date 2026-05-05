import json

NORMALIZATION_MAP = {
    "Object Storage": ["gcs", "bucket", "s3"],
    "Streaming Queue": ["pubsub", "kafka"],
    "Data Warehouse": ["bigquery", "bq"],
    "Compute": ["vm", "compute"]
}


#def normalize_type(raw):
#    raw = raw.lower()
#
#    for k, vals in NORMALIZATION_MAP.items():
#        if any(v in raw for v in vals):
#            return k
#
#    return "Unknown"
#

def normalize_type(raw):

    # --------------------------
    # CASE 1: list → take first item
    # --------------------------
    if isinstance(raw, list):
        if len(raw) == 0:
            return "Unknown"
        raw = raw[0]

    # --------------------------
    # CASE 2: dict → try name field
    # --------------------------
    if isinstance(raw, dict):
        raw = raw.get("type", "Unknown")

    # --------------------------
    # CASE 3: None handling
    # --------------------------
    if raw is None:
        return "Unknown"

    # --------------------------
    # CASE 4: final normalization
    # --------------------------
    raw = str(raw).lower()

    if "storage" in raw or "gcs" in raw:
        return "Object Storage"

    if "pubsub" in raw or "queue" in raw:
        return "Streaming Queue"

    if "bigquery" in raw or "warehouse" in raw:
        return "Data Warehouse"

    if "api" in raw or "integration" in raw:
        return "API Layer"

    if "compute" in raw or "vm" in raw:
        return "Compute"

    return "Unknown"

#def normalize_components(components):
#    output = []
#
#    for i, c in enumerate(components):
#        comp = {}
#
#        comp["name"] = c.get("name", f"comp-{i+1}")
#        comp["type"] = normalize_type(c.get("type", ""))
#        comp["region"] = c.get("region", "asia-south1")
#
#        output.append(comp)
#
#    return output
#

def normalize_components(components):

    normalized = []

    for c in components:

        comp = {}

        comp["name"] = c.get("name", "unknown")

        comp["type"] = normalize_type(c.get("type"))

        comp["region"] = c.get("region", "global")

        normalized.append(comp)

    return normalized

def clean_output(raw):
    if not raw:
        return []

    raw = raw.strip().replace("```json", "").replace("```", "")

    try:
        return json.loads(raw)
    except:
        pass

    try:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        return json.loads(raw[start:end])
    except:
        pass

    return []


def fallback_parser(text):
    text = text.lower()
    comps = []

    if "gcs" in text:
        comps.append({"name": "gcs-1", "type": "Object Storage", "region": "asia-south1"})

    if "bigquery" in text:
        comps.append({"name": "bq-1", "type": "Data Warehouse", "region": "asia-south1"})

    if "pubsub" in text:
        comps.append({"name": "pubsub-1", "type": "Streaming Queue", "region": "asia-south1"})

    return comps
