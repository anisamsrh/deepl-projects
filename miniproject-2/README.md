# Receipt Validator

- [Receipt's Criteria]{}
- [Project's Setup]{}

## Receipt's Criteria
The program will looking for:
1. Merchant's name
2. Merchant's NPWP
3. Product information (name, qty, price per unit, and subtotal)
4. Tax information (tax rate and tax amount)
5. General purchase information (total amount before and after tax)

Each information will be evaluated adered to the following rules:
1. Merchant's name must be present
2. Merchant's NPWP must be present
3. Product information (name, qty, price per unit, and subtotal) should be present and complete for all items
4. Tax information (tax rate and tax amount) should be present with the right rate (PPN11%) and calculation
5. General purchase information (total amount before and after tax) should be present

Receipts will be automatically marked as **REJECTED** if these pieces of information is failed to be extracted:
- Merchant's name
- Merchant's NPWP
- Product information (not even an incomplete information)

Receipt will be marked as **ACCEPTED** if all criteria are met and **NEED REVIEW** conversely, such as due to missing information on one of the items.

## Setup
1. Create .env and put your API_KEY inside
```
GEMINI_KEY=YOUR_API_KEY
```
2. Build and run Docker Container
```
docker compose up -d --built
```