import re

def validate_claim(extracted_data: dict) -> dict: 
    rejection_reasons = []

    store_name = extracted_data.get("store_name")
    npwp = extracted_data.get("npwp")
    items = extracted_data.get("items", [])
    subtotal = extracted_data.get("subtotal") or 0
    tax_amount = extracted_data.get("tax_amount") or 0
    grand_total = extracted_data.get("grand_total") or 0
    tax_percentage = extracted_data.get("tax_percentage") or 0

    # check store name
    has_store_name = bool(store_name and store_name.strip() and store_name.lower() != "null")
    if not has_store_name:
        rejection_reasons.append("Merchant's name is not found.")
    # check npwp
    has_npwp = bool(npwp and len(re.sub(r'\D', '', str(npwp))) >= 12)
    if not has_npwp:
        rejection_reasons.append("Merchant's NPWP is not valid or not found.")
    # check items
    has_items = len(items) > 0
    if not has_items:
        rejection_reasons.append("No items is found in the receipt.")
    # is each item has name, qty, price per unit, and total price?
    items_valid = True
    for item in items:
        item_name = item.get("item_name")
        quantity = item.get("quantity")
        price_per_unit = item.get("price_per_unit")
        total_price = item.get("total_price")

        if not item_name or not str(item_name).strip():
            rejection_reasons.append(f"Item name is missing for one of the items.")
            items_valid = False
        if quantity is None or quantity <= 0:
            rejection_reasons.append(f"Quantity is missing or invalid for item '{item_name}'.")
            items_valid = False
        if price_per_unit is None or price_per_unit <= 0:
            rejection_reasons.append(f"Price per unit is missing or invalid for item '{item_name}'.")
            items_valid = False
        if total_price is None or total_price <= 0:
            rejection_reasons.append(f"Total price is missing or invalid for item '{item_name}'.")
            items_valid = False
    
    # check ppn
    # is tax amount shown?
    tax_valid = True
    has_tax = tax_percentage > 0 or tax_amount > 0
    if not has_tax:
        rejection_reasons.append("Tax amount is not shown or not valid.")
        tax_valid = False
    if has_tax:
        # is tax amount correctly calcullated?
        if tax_amount == 0 and subtotal and grand_total:
            tax_amount = grand_total - subtotal
        if tax_percentage > 0 and subtotal and tax_amount:
            expected_tax_amount = round(subtotal * (tax_percentage / 100))
            if tax_amount != expected_tax_amount:
                rejection_reasons.append(f"Tax amount is not correctly calculated. Expected: {expected_tax_amount}, Found: {tax_amount}.")
                tax_valid = False
        # is tax amount adere to regulation?
        if tax_percentage == 0:
            if subtotal and tax_amount:
                tax_percentage = round(tax_amount / subtotal * 100)
                grand_total = grand_total or subtotal + tax_amount
            elif subtotal and grand_total:
                tax_amount = tax_amount or grand_total - subtotal
                tax_percentage = round(tax_amount / subtotal * 100)
            elif tax_amount and grand_total:
                subtotal = subtotal or grand_total - tax_amount
                tax_percentage = round(tax_amount / subtotal * 100)
        if tax_percentage > 11:
            rejection_reasons.append("Tax percentage exceeds the allowed limit of 11%.")
            tax_valid = False

    # decide final status
    if not has_store_name or not has_npwp or not has_items:
        status = "rejected"
    elif rejection_reasons:
        status = "needs_review"
    else:
        status = "approved"

    return {
        "merchant_info": {
            "store_name": store_name,
            "npwp": npwp,
            "has_store_name": has_store_name,
            "has_npwp": has_npwp
        },
        "items": items,
        "financial_summary": {
            "subtotal": subtotal,
            "tax_amount_extracted": tax_amount,
            "total_amount": grand_total,
            "detected_ppn_rate": tax_percentage
        },
        "validation_result": {
            "status": status,
            "validation_checks": {
                "store_name_present": has_store_name,
                "npwp_present": has_npwp,
                "items_extracted": has_items and items_valid,
                "ppn_valid": tax_valid
            },
            "rejection_reasons": rejection_reasons
        }
    }
