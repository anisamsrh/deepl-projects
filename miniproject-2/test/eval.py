from PIL import Image
from tqdm import tqdm
import io
import os
import pandas as pd
import requests
import time

API_URL = "http://localhost:8000/analyze-claim"
DATASET_PATH = "../data"
OUTPUT_PATH = "evaluation_result.csv"
DELAY = 15 # 15 seconds between request

results = []

print("Starting evaluation....")

files = os.listdir(DATASET_PATH)
for f in tqdm(files, desc="Processing images", unit="file"):
    filepath = os.path.join(DATASET_PATH, f)

    start_time = time.time()
    try :
        img = Image.open(filepath)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="JPEG")
        img_byte_arr.seek(0)
        files_payload = {"file": (f, img_byte_arr, "image/jpeg")}
        response = requests.post(API_URL, files=files_payload)

        total_latency = round(time.time() - start_time, 2)

        if response.status_code == 200:
            res_json = response.json()

            # general groundtruth information
            g_truth = "accepted" if (int(f[0]) == 2) else "not accepted"
            
            # extracted information
            name = res_json.get("merchant_info", {}).get("store_name", "")
            npwp = res_json.get("merchant_info", {}).get("npwp", "")
            subtotal = res_json.get("financial_summary", {}).get("subtotal", 0)
            tax_amount = res_json.get("financial_summary", {}).get("tax_amount_extracted", 0)
            grand_total = res_json.get("financial_summary", {}).get("total_amount", 0)
            tax_percentage = res_json.get("financial_summary", {}).get("detected_ppn_rate", 0)

            # status information
            status = res_json.get("validation_result", {}).get("status", "unknown")
            has_name = res_json.get("validation_result", {}).get("validation_checks", {}).get("store_name_present", False)
            has_npwp = res_json.get("validation_result", {}).get("validation_checks", {}).get("npwp_present", False)
            items_extracted = res_json.get("validation_result", {}).get("validation_checks", {}).get("items_extracted", False)
            tax_valid = res_json.get("validation_result", {}).get("validation_checks", {}).get("ppn_valid", False)

            results.append({
                "filename": f,
                "groundtruth": g_truth,
                "name": name,
                "npwp": npwp,
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "grand_total": grand_total,
                "tax_percentage": tax_percentage,
                "status": status,
                "has_name": has_name,
                "has_npwp": has_npwp,
                "items_extracted": items_extracted,
                "tax_valid": tax_valid,
                "latency": total_latency
            })

        else:
            print(f"[{f}] Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[{f}] Exception: {e}")

    time.sleep(DELAY)

df = pd.DataFrame(results)
df.to_csv(OUTPUT_PATH, index=False)

print("Finish! Results saved to ", OUTPUT_PATH)