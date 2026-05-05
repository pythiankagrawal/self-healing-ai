def build_parser_prompt(user_input):
    return f"""
You are a JSON API.

Return ONLY valid JSON list.

[
  {{
    "name": "string",
    "type": "Object Storage | Streaming Queue | Data Warehouse | Compute | Database | API",
    "region": "string"
  }}
]

INPUT:
{user_input}
"""
