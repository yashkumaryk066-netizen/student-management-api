# Eazypay & Payment Credentials

To connect the entire system end-to-end, especially the **Automatic Verification**, you must provide the following credentials.

Standard Eazypay Integration requires:

1. **Merchant ID** (e.g. `123456`) - Provided by ICICI Bank.
2. **Encryption Key** (e.g. `123...`) - Provided by ICICI Bank. This is critical for the "Advanced Level" encryption we implemented.
3. **Sub Merchant ID** (e.g. `4567`) - If applicable.

### Where to put these?
Edit the `.env` file in the main directory:

```bash
EAZYPAY_MERCHANT_ID=YOUR_REAL_ID_HERE
EAZYPAY_ENCRYPTION_KEY=YOUR_REAL_KEY_HERE
```

### About the QR Code
I have added the QR code you provided to the Student Dashboard as a "Scan & Pay" option. 
**Note:** Payments made via this QR code are **NOT** automatically verified by the system because a static QR code does not talk to our backend. 
Use the "Automatic Payment" (Pay Now) button for auto-verification.
