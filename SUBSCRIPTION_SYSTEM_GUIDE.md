# Client Subscription & Onboarding

I have implemented the **Advanced Client Subscription System** that you requested.

### Features Implemented:
1.  **Plan-Based Onboarding**:
    *   Clients can buy **School**, **Coaching**, or **Institute** plans.
    *   The system automatically assigns the correct permissions and dashboard based on the plan.
2.  **Auto-Credential Generation**:
    *   Upon initiation, the system creates an Admin Account for the client.
    *   It generates a secure random password.
3.  **Subscription Tracking**:
    *   A new `ClientSubscription` model tracks start date, end date, and status.
    *   Payment verification (Auto or Manual) triggers the activation of the plan for 365 days.

### How to Test (API Flow):

**1. Purchase / Initiate Plan:**
`POST /api/subscription/buy/`
```json
{
  "plan_type": "SCHOOL",
  "email": "principal@topschool.com",
  "phone": "9876543210",
  "amount": "15000"
}
```
*Result*: Returns a payment link (or manual instructions) and creates a pending user.

**2. Success Callback (Simulated payment success):**
`GET /api/subscription/success/?email=principal@topschool.com`
*Result*: Activates the plan and returns the credentials.

### Next Steps:
*   You can now integrate a Pricing Page on the frontend that hits these APIs.
*   The system is backend-ready for SaaS sales! 🚀
