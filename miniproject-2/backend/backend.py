from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from google import genai
from PIL import Image
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import io
import json
import os

from .validation_logic import validate_claim

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))
app = FastAPI(title="Claim Document Validation API")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
PROMPT_EXTRACTION = """
Anda adalah asisten ekstraksi dokumen keuangan. Analisis gambar struk/faktur/resi ini dan ekstrak informasi berikut ke dalam format JSON murni TANPA markdown formatting tambahan:

{
  "store_name": "Nama toko/merchant jika ada, null jika tidak ada",
  "npwp": "Nomor NPWP jika ada, null jika tidak ada",
  "items": [
    {
      "item_name": "Nama barang",
      "quantity": 1,
      "price_per_unit": 10000,
      "total_price": 10000
    }
  ],
  "subtotal": 100000, dpp (dasar pengenaan pajak) atau harga sebelum pajak
  "tax_amount": 11000,
  "grand_total": 111000, total harga yang dibayar oleh pelanggam
  "tax_percentage": 10
}

Aturan Ekstraksi:
1. Pastikan semua harga dan nominal berupa angka murni (number) tanpa "Rp" atau titik/koma pemisah ribuan. Jika tidak ditemukan, kembalikan 0
2. Jika item tidak memiliki quantity, asumsikan 1.
3. Ekstrak NPWP secara teliti jika tercantum pada dokumen.
"""

@app.post("/analyze-claim")
@limiter.limit("5/minute")
async def analyze_claim(request: Request, file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Document must be an image.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        response = client.models.generate_content(
            model = 'gemini-3-flash-preview',
            contents = [PROMPT_EXTRACTION, image])
        clean_json_str = response.text.replace("```json", "").replace("```", "").strip()
        extracted_data = json.loads(clean_json_str)
        result = validate_claim(extracted_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
