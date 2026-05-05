from core.defaults import DEFAULTS, CRITICAL_FIELDS


def apply_defaults(components):
    for comp in components:
        defaults = DEFAULTS.get(comp["type"], {})
        for k, v in defaults.items():
            if k not in comp:
                comp[k] = v
    return components


def find_missing(components):
    missing = []

    for comp in components:
        required = CRITICAL_FIELDS.get(comp["type"], [])
        for field in required:
            if not comp.get(field):
                missing.append((comp, field))

    return missing


def clarifier_agent(components):
    print("🤖 Clarifier Agent starting...")

    components = apply_defaults(components)

    missing = find_missing(components)

    if not missing:
        print("✅ No missing fields")
        return components

    for comp, field in missing:
        val = input(f"{comp['name']} → {field}? ")
        comp[field] = val

    return components
