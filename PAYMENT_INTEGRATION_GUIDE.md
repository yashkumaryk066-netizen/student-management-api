# Payment Gateway Integration Guide (Eazypay)

## Overview
This project now integrates **ICICI Eazypay** for handling secure payments. The integration includes AES-128 encryption, auto-verification via callbacks, and secure status tracking.

## Configuration
Ensure the following variables are set in your `.env` file or environment:

```bash
EAZYPAY_MERCHANT_ID=your_merchant_id
EAZYPAY_ENCRYPTION_KEY=your_128_bit_key_here
EAZYPAY_SUB_MERCHANT_ID=your_sub_merchant_id
EAZYPAY_RETURN_URL=https://yourdomain.com/api/payment/eazypay/callback/
EAZYPAY_MODE=TEST  # Change to LIVE in production
```

## API Endpoints

### 1. Initiate Payment
**URL**: `/api/payment/eazypay/init/`
**Method**: `POST`
**Auth**: Required (Bearer Token)
**Body**:
```json
{
    "amount": "100.00",
    "description": "Tuition Fee"
}
```
**Response**:
```json
{
    "transaction_id": "unique_txn_id",
    "payment_url": "https://test.eazypay.icicibank.com/...",
    "status": "INITIATED"
}
```
**Action**: Redirect the user's browser to `payment_url`.

### 2. Payment Callback (Auto-Verify)
**URL**: `/api/payment/eazypay/callback/`
**Method**: `POST`
**Auth**: Open (Server-to-Server)
**Description**: 
This endpoint is called automatically by Eazypay after payment.
- It decrypts the response.
- It verifies the `Response_Code`.
- If successful (`E000`), it updates the payment status to `PAID` and extends the subscription if applicable.

## Security Features
- **AES Encryption**: All sensitive data passed in the URL uses AES encryption compatible with Eazypay's standard.
- **Transaction ID Tracking**: Every payment has a unique ID stored in the database before leaving the system.
- **Secure Callback**: The callback verifies the transaction ID against the database before applying changes.

## Testing
1. Use `EAZYPAY_MODE=TEST`.
2. Initiate a payment.
3. Use the returned URL to simulate payment (if using a simulator) or inspect the generated URL for correct parameters.
4. Manually POST to the callback URL (if testing locally without a public IP) using a tool like Postman with the expected bank payload.
