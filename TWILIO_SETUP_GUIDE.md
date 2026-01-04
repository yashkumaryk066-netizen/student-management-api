# Twilio Free Account Setup Guide for Advanced Notifications

To enable "Advance Level" real-time WhatsApp notifications for your ERP (like *Plan Renewed*, *New Request*, etc.), you need a **Twilio Free Account**.

I have already configured the code to use Twilio. You just need to create the account and get the keys.

## Step 1: Create Account
1. Go to [Twilio Sign Up](https://www.twilio.com/try-twilio).
2. Sign up for a free trial.
3. Verify your email and phone number.

## Step 2: Get Credentials
1. Log in to the Twilio Console Dashboard.
2. Scroll down to "Account Info".
3. Copy the **Account SID**.
4. Copy the **Auth Token**.

## Step 3: Set Up WhatsApp Sandbox (Crucial!)
1. Go to **Messaging > Try it out > Send a WhatsApp message**.
2. You will see a "Sandbox Number" (e.g., `+1 415 523 8886`) and a "Join Code" (e.g., `join something-random`).
3. **IMPORTANT:** Since this is a Free Account, you can ONLY send messages to numbers that have "Joined" your sandbox.
4. Send a WhatsApp message from your personal phone (and the Admin phone) to the Sandbox Number with the code (e.g., `join something-random`).
5. You should receive a confirmation like "You are all set!".

## Step 4: Configure Your Project
Open the `.env` file in your project root (`/home/tele/manufatures/.env`) and add these lines:

```bash
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886  <-- This is your sandbox number
ADMIN_WHATSAPP_NUMBER=+918356926231           <-- Your Admin Phone (Must send 'join' msg first)
```

## How It Works
*   **Renewal Request:** When a client clicks "Renew", the system uses these keys to send a WhatsApp alert to your `ADMIN_WHATSAPP_NUMBER`.
*   **Approval:** When you approve a client, the system sends a confirmation to the Client's phone. (**Note:** Free account requires the Client to also send the 'join' code to the sandbox number initially).

Once you upgrade to a Paid Twilio Account later, you can use your own branded number and message anyone without them joining.
