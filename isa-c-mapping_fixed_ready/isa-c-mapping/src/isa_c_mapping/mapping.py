from typing import Any


def to_isa_c(record: dict[str, Any]) -> dict[str, Any]:
    p = record.get("product", {}) or {}
    dl = record.get("gs1_digital_link", {}) or {}
    nutr = p.get("nutriments", {}) or {}

    def get(*path, default=None):
        cur = record
        for key in path:
            if isinstance(cur, dict):
                cur = cur.get(key, {})
            else:
                return default
        return cur if cur != {} else default

    out = {
        "identifiers": {
            "gtin": dl.get("GTIN") or get("product", "code"),
            "product_code": get("product", "code"),
            "gpc_category_code": record.get("gpcCategoryCode"),
            "country_code": record.get("countryCode"),
        },
        "product": {
            "name": p.get("product_name"),
            "brand": p.get("brands"),
            "quantity": p.get("quantity"),
            "allergens": p.get("allergens_from_ingredients"),
        },
        "packaging": {
            "material_type_code": record.get("packagingMaterialTypeCode"),
            "recycled_content_percent": record.get("recycledContentPercentage"),
            "is_recyclable": record.get("isRecyclable"),
        },
        "nutrition_per_100g": {
            "energy_kcal": nutr.get("energy-kcal_100g"),
            "fat": nutr.get("fat_100g"),
            "carbohydrates": nutr.get("carbohydrates_100g"),
            "proteins": nutr.get("proteins_100g"),
            "salt": nutr.get("salt_100g"),
        },
        "environmental": {
            "carbon_footprint": record.get("carbonFootprint"),
            "energy_consumption": record.get("energyConsumption"),
            "waste_generated": record.get("wasteGenerated"),
            "is_biodegradable": record.get("isBiodegradable"),
        },
        "trade_item_units": {
            "base_unit": record.get("isTradeItemABaseUnit"),
            "consumer_unit": record.get("isTradeItemAConsumerUnit"),
            "despatch_unit": record.get("isTradeItemADespatchUnit"),
            "orderable_unit": record.get("isTradeItemAnOrderableUnit"),
        },
        "digital_link": dl or None,
    }
    return _remove_nones(out)


def _remove_nones(obj):
    if isinstance(obj, dict):
        return {k: _remove_nones(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_remove_nones(v) for v in obj if v is not None]
    return obj
