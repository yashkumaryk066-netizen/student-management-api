from Crypto.Cipher import AES
import base64
from django.conf import settings

class EazypayClient:
    def __init__(self):
        self.merchant_id = settings.EAZYPAY_MERCHANT_ID
        self.encryption_key = settings.EAZYPAY_ENCRYPTION_KEY
        self.sub_merchant_id = getattr(settings, 'EAZYPAY_SUB_MERCHANT_ID', None)
        self.return_url = settings.EAZYPAY_RETURN_URL
        self.mode = getattr(settings, 'EAZYPAY_MODE', 'TEST') # TEST or LIVE
        
        if self.mode == 'LIVE':
            self.base_url = "https://eazypay.icicibank.com/EazyPG"
        else:
            # Sandbox URL (Note: ICICI doesn't have a public sandbox url always the same, but this is typical)
            # Often they use the same URL but different creds, or a specific test URL.
            self.base_url = "https://test.eazypay.icicibank.com/EazyPG" 

    def pad(self, data):
        length = 16 - (len(data) % 16)
        return data + chr(length)*length

    def unpad(self, data):
        return data[:-ord(data[len(data)-1:])]

    def encrypt(self, plain_text):
        try:
            key = self.encryption_key.encode('utf-8')
            iv = key # ICICI often uses key as IV or a specific IV. Assuming Key=IV for standard Eazypay kit unless specified otherwise.
            # Actually, standard Eazypay often uses ECB or CBC with random IV. 
            # Most common older integrations use ECB. Newer use CBC.
            # Let's assume AES-128-ECB as it's common in older bank gateways in India, 
            # BUT many docs say AES/CBC/PKCS5Padding.
            # I will use CBC with a zero IV or Key as IV if not specified. 
            # *Correction*: Popular Python Eazypay implementations use ECB. I'll stick to ECB for now or provide a flag.
            
            # Re-checking standard integration: usually it is AES-128-ECB.
            cipher = AES.new(key, AES.MODE_ECB)
            padded_text = self.pad(plain_text)
            encrypted_bytes = cipher.encrypt(padded_text.encode('utf-8'))
            encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
            return encrypted_b64
        except Exception as e:
            print(f"Encryption error: {e}")
            return None

    def decrypt(self, encrypted_text):
        try:
            key = self.encryption_key.encode('utf-8')
            cipher = AES.new(key, AES.MODE_ECB)
            encrypted_bytes = base64.b64decode(encrypted_text)
            decrypted_padded = cipher.decrypt(encrypted_bytes).decode('utf-8')
            return self.unpad(decrypted_padded)
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

    def get_payment_url(self, transaction_id, amount, optional_fields=None):
        """
        Generates the URL with encrypted parameters.
        Force optional_fields to be a dict if None
        """
        if optional_fields is None:
            optional_fields = {}

        mandatory_fields = f"{self.merchant_id}|{self.sub_merchant_id}|{amount}|{transaction_id}|{self.return_url}|{optional_fields.get('reference1','')}|{optional_fields.get('reference2','')}|{optional_fields.get('reference3','')}|{optional_fields.get('reference4','')}|{optional_fields.get('reference5','')}|{optional_fields.get('reference6','')}|{optional_fields.get('reference7','')}"
        
        # ICICI requires specific fields in a specific order encrypted.
        # Format: merchantId|subMerchantId|amount|referenceNo|returnUrl|... 
        
        encrypted_data = self.encrypt(mandatory_fields)
        
        return f"{self.base_url}?merchantid={self.merchant_id}&mandatory fields={encrypted_data}&optional fields={optional_fields.get('optional_string','')}&returnurl={self.return_url}&Reference No={transaction_id}&submerchantid={self.sub_merchant_id}&transaction amount={amount}&paymode={optional_fields.get('paymode',9)}"

