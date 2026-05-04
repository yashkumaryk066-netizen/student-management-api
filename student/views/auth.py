from .base import *
from rest_framework_simplejwt.views import TokenObtainPairView
from student.serializers import CustomTokenObtainPairSerializer, UserProfileSerializer
from student.models import ClientSubscription, UserProfile, Payment
from datetime import date, timedelta
from decimal import Decimal
from student.plan_permissions import PLAN_PRICING

class SecuredTokenObtainPairView(TokenObtainPairView):
    """
    SECURITY FIX #14: Rate limited login endpoint
    """
    from student.throttling import LoginRateThrottle
    throttle_classes = [LoginRateThrottle]
    serializer_class = CustomTokenObtainPairSerializer

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request):
        import traceback
        try:
            from student.plan_permissions import get_user_plan, PLAN_FEATURES
            
            user = request.user
            logger.info(f"📡 API PROFILE ACCESS: {user.username} (SuperUser: {user.is_superuser})")
            
            # 1. GOD MODE: Immediate Return for SuperUser
            # Bypass all other checks if superuser
            if user.is_superuser:
                return Response({
                    "username": user.username,
                    "email": user.email,
                    "role": "ADMIN",
                    "id": user.id,
                    "is_superuser": True,
                    "user_full_name": user.get_full_name() or "Super Administrator",
                    "full_name": user.get_full_name() or "Super Administrator", # Match Serializer
                    "available_features": PLAN_FEATURES.get('SUPER_ADMIN', []),
                    # Mock profile data to prevent frontend crashes
                    "institution_name": "Y.S.M CENTRAL COMMAND", 
                    "institution_logo": None,
                    "digital_signature": None,
                    "phone": "",
                    "address": "System Root",
                    "institution_type": "EDUCATION SYSTEM",  # FIX L-3: consistent value
                    "subscription_plan": "ENTERPRISE",
                    "must_change_password": False
                })
            
            # Check profile and role
            profile = getattr(user, 'profile', None)
            role = profile.role if profile else 'STUDENT'
            
            # Get Features using Dynamic Resolver (PREMIUM FIX)
            from student.plan_permissions import get_effective_permissions, get_upgrade_options
            features = list(get_effective_permissions(user))
            upgrade_options = get_upgrade_options(user)

            data = {
                "username": user.username,
                "email": user.email,
                "role": role,
                "id": user.id,
                "is_superuser": user.is_superuser,
                "user_full_name": user.get_full_name(),
                "available_features": features,
                "upgrade_options": upgrade_options, # NEW: Dynamic Upgrade Path
                "subscription_plan": profile.subscription_plan if profile else "BASIC", # Return tier info
                "must_change_password": profile.force_password_change if profile else False
            }
            
            if profile:
                 profile_data = UserProfileSerializer(profile).data
                 # Ensure full URLs for images
                 if profile.institution_logo:
                     profile_data['institution_logo'] = request.build_absolute_uri(profile.institution_logo.url)
                 if profile.digital_signature:
                     profile_data['digital_signature'] = request.build_absolute_uri(profile.digital_signature.url)
                 data.update(profile_data)
                 
            return Response(data)
        except Exception as e:
            logger.error("❌ CRITICAL ERROR IN PROFILE VIEW ❌", exc_info=True)
            return Response({"error": "An internal error occurred. Please try again."}, status=500)
    
    def put(self, request):
        """Update user profile information"""
        user = request.user
        data = request.data
        
        # Update User model fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        # FIX H-5: Email uniqueness check before allowing update
        if 'email' in data:
            new_email = (data['email'] or '').strip().lower()
            if new_email and new_email != user.email.lower():
                if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
                    return Response({'error': 'This email address is already in use by another account.'}, status=400)
                user.email = new_email
        user.save()
        
        # Update Profile model fields if profile exists
        if hasattr(user, 'profile'):
            profile = user.profile
            if 'phone' in data:
                profile.phone = data['phone']
            if 'institution_name' in data:
                profile.institution_name = data['institution_name']
            if 'address' in data:
                profile.address = data['address']

            # --- GEOFENCING CONFIGURATION (For Attendance) ---
            if 'location_lat' in data and data['location_lat']:
                try:
                    profile.location_lat = float(data['location_lat'])
                except (ValueError, TypeError):
                    pass # Keep existing if invalid
                    
            if 'location_long' in data and data['location_long']:
                try:
                    profile.location_long = float(data['location_long'])
                except (ValueError, TypeError):
                    pass
            
            if 'attendance_radius' in data and data['attendance_radius']:
                try:
                    profile.attendance_radius = int(data['attendance_radius'])
                except (ValueError, TypeError):
                    profile.attendance_radius = 100 # Default fallback
            
            # File Uploads (Branding)
            # request.FILES contains the files when using MultiPartParser
            # SECURITY FIX #3: File upload validation
            from student.security_utils import validate_file_upload
            from django.core.exceptions import ValidationError
            
            if 'institution_logo' in request.FILES:
                try:
                    validated_logo = validate_file_upload(
                        request.FILES['institution_logo'],
                        allowed_types=['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
                        max_size_mb=5
                    )
                    profile.institution_logo = validated_logo
                except ValidationError as e:
                    return Response({"error": f"Invalid logo file: {str(e)}"}, status=400)
            
            if 'digital_signature' in request.FILES:
                try:
                    validated_sig = validate_file_upload(
                        request.FILES['digital_signature'],
                        allowed_types=['image/jpeg', 'image/png'],
                        max_size_mb=2
                    )
                    profile.digital_signature = validated_sig
                except ValidationError as e:
                    return Response({"error": f"Invalid signature file: {str(e)}"}, status=400)

            profile.save()
        
        return Response({
            "message": "Profile updated successfully",
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        })
    
    def patch(self, request):
        return self.put(request)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            current_password = request.data.get('current_password') or request.data.get('old_password')
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password') or new_password # Default to new_password if not provided

            if not current_password or not new_password:
                return Response({'error': 'Please provide current and new passwords.'}, status=400)
            
            if new_password != confirm_password:
                 return Response({'error': 'New passwords do not match.'}, status=400)

            user = request.user
            if not user.check_password(current_password):
                return Response({'error': 'Incorrect current password.'}, status=400)

            # Optional: Add password complexity checks here

            user.set_password(new_password)
            user.save()
            
            # Reset the force change flag if it exists
            if hasattr(user, 'profile'):
                user.profile.force_password_change = False
                user.profile.save()
            
            # Optional: Refresh session/tokens if needed, or let frontend handle re-login
            
            return Response({'message': 'Password updated successfully. Please login again with the new password.'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class ClientSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # 1. GOD MODE: Infinite Subscription for SuperUser
        if request.user.is_superuser:
            return Response({
                 "plan_type": "SUPER_ADMIN",
                 "status": "ACTIVE",
                 "valid_until": "2099-12-31",
                 "days_left": 9999,
                 "plan": "SUPER_ADMIN",
                 "amount_paid": 0,
                 "start_date": "2024-01-01",
                 "end_date": "2099-12-31",
            })

        # Auto-create subscription if missing (Advance Level User Experience)
        if not hasattr(request.user, 'subscription'):
            try:
                # Create an EXPIRED 'COACHING' subscription to minimize access risk
                ClientSubscription.objects.create(
                    user=request.user,
                    plan_type='COACHING',
                    status='EXPIRED',
                    start_date=date.today(),
                    end_date=date.today()
                )
            except Exception:
                pass # Fallback to NO_SUBSCRIPTION response if creation fails

        if hasattr(request.user, 'subscription'):
             sub = request.user.subscription
             plan_type = sub.plan_type
             current_price = PLAN_PRICING.get(plan_type, Decimal('0.00'))
             
             return Response({
                 "plan_type": plan_type,
                 "status": sub.status,
                 "valid_until": sub.end_date,
                 "days_left": sub.days_remaining,
                 "plan": plan_type, # Backward compat
                 "amount_paid": sub.amount_paid,
                 "start_date": sub.start_date,
                 "end_date": sub.end_date,
                 "price": current_price,
             })
        return Response({"status": "NO_SUBSCRIPTION", "days_left": 0, "price": 0})

class SubscriptionRenewalView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        plan_type = (request.data.get('plan_type') or '').upper()
        payment_id = request.data.get('payment_id') or request.data.get('transaction_id')
        amount = request.data.get('amount', 0)
        
        if not plan_type or not payment_id:
            return Response({"error": "Plan type and payment ID required"}, status=400)
        
        subscription = ClientSubscription.objects.filter(user=request.user).first()
        if not subscription:
            return Response({"error": "No subscription found"}, status=404)
        
        # Verify payment logic would go here
        
        with transaction.atomic():
            today = date.today()
            if subscription.end_date and subscription.end_date > today:
                subscription.end_date += timedelta(days=30)
            else:
                subscription.end_date = today + timedelta(days=30)
            
            subscription.status = 'ACTIVE'
            subscription.plan_type = plan_type
            subscription.amount_paid += Decimal(str(amount))
            subscription.save()
            
            # Update UserProfile expiry
            if hasattr(request.user, 'profile'):
                request.user.profile.subscription_expiry = subscription.end_date
                request.user.profile.save()
        
        return Response({
            "message": "Subscription renewed successfully",
            "new_expiry": subscription.end_date
        })

class PublicSubscriptionSubmitView(APIView):
    """Public endpoint for new subscription signup"""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # Import pricing from centralized source to avoid duplication
    from student.plan_permissions import PLAN_PRICING 
    PLAN_MAP = {
        'coaching center': 'COACHING',
        'coaching': 'COACHING',
        'school': 'SCHOOL',
        'modern school': 'SCHOOL',
        'institute': 'INSTITUTE',
        'institute / university': 'INSTITUTE',
        'institute/university': 'INSTITUTE',
        'university': 'INSTITUTE',
        'coaching_center': 'COACHING',
        'COACHING': 'COACHING',
        'SCHOOL': 'SCHOOL',
        'INSTITUTE': 'INSTITUTE',
    }

    def _normalize_plan_type(self, raw_plan):
        if not raw_plan:
            return None
        raw = str(raw_plan).strip()
        return self.PLAN_MAP.get(raw) or self.PLAN_MAP.get(raw.lower()) or self.PLAN_MAP.get(raw.upper())

    def _generate_unique_username(self, email):
        base = (email.split('@')[0] or 'client').lower()
        safe_base = ''.join(ch for ch in base if ch.isalnum() or ch in ['_', '.'])[:20] or 'client'
        username = safe_base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{safe_base}{counter}"
            counter += 1
        return username

    def _handle_legacy_signup(self, data):
        username = data.get('username')
        email = (data.get('email') or '').strip().lower()
        password = data.get('password')
        plan_type = (data.get('plan_type') or 'COACHING').upper()
        payment_id = data.get('payment_id')
        institution_name = data.get('institution_name', 'New Institution')

        if not all([username, email, password, plan_type, payment_id]):
            return Response(
                {"error": "All fields required (username, email, password, plan_type, payment_id)"},
                status=400
            )

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=400)
            
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=400)

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            
            UserProfile.objects.create(
                user=user,
                role='CLIENT',
                institution_type=plan_type,
                institution_name=institution_name
            )
            
            ClientSubscription.objects.create(
                user=user,
                plan_type=plan_type,
                transaction_id=payment_id,
                status='PENDING'
            )
            
        return Response({"message": "Registration successful! Please wait for approval."}, status=201)

    def post(self, request):
        data = request.data
        
        # Check if legacy structure
        if 'username' in data and 'password' in data:
            return self._handle_legacy_signup(data)
            
        # New "Advanced" Onboarding Flow
        from decimal import Decimal
        from student.plan_permissions import PLAN_PRICING 
        
        # 1. Normalize Data
        email = (data.get('email') or '').strip().lower()
        phone = data.get('phone')
        institution_name = data.get('institution_name')
        plan_type = self._normalize_plan_type(data.get('plan_type'))
        utr = (data.get('utr') or data.get('transaction_id') or '').strip().upper()

        try:
            amount = Decimal(str(data.get('amount', '0')))
        except Exception:
            return Response({"error": "Invalid amount format"}, status=400)

        if not all([email, phone, institution_name, plan_type, utr]):
            return Response(
                {"error": "Missing required fields (email, phone, institution_name, plan_type, utr)"},
                status=400
            )

        if len(utr) < 10:
            return Response({"error": "UTR/Transaction ID must be at least 10 characters"}, status=400)

        expected_amount = PLAN_PRICING.get(plan_type)
        if expected_amount is None:
            return Response({"error": "Invalid plan type selected"}, status=400)
        if amount < expected_amount:
            return Response({"error": f"Invalid amount. {plan_type} requires at least {expected_amount}"}, status=400)

        if Payment.objects.filter(transaction_id=utr).exists():
            return Response({"error": "Duplicate UTR/Transaction ID. Request already submitted."}, status=400)

        from student.security_utils import validate_file_upload
        from django.core.exceptions import ValidationError

        institution_logo = request.FILES.get('institution_logo')
        digital_signature = request.FILES.get('digital_signature')

        if institution_logo:
            try:
                institution_logo = validate_file_upload(
                    institution_logo,
                    allowed_types=['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
                    max_size_mb=5
                )
            except ValidationError as e:
                return Response({"error": f"Invalid logo file: {str(e)}"}, status=400)

        if digital_signature:
            try:
                digital_signature = validate_file_upload(
                    digital_signature,
                    allowed_types=['image/jpeg', 'image/png'],
                    max_size_mb=2
                )
            except ValidationError as e:
                return Response({"error": f"Invalid signature file: {str(e)}"}, status=400)

        try:
            with transaction.atomic():
                user = User.objects.filter(email__iexact=email).first()
                if user and (user.is_superuser or user.is_staff):
                    return Response(
                        {"error": "This email is reserved for a privileged account. Use a different email."},
                        status=400
                    )

                if not user:
                    user = User.objects.create_user(
                        username=self._generate_unique_username(email),
                        email=email
                    )
                    user.set_unusable_password()
                    user.save()

                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'role': 'CLIENT',
                        'institution_type': plan_type
                    }
                )
                if not user.is_superuser:
                    profile.role = 'CLIENT'
                profile.phone = phone
                profile.institution_type = plan_type
                profile.institution_name = institution_name
                if institution_logo:
                    profile.institution_logo = institution_logo
                if digital_signature:
                    profile.digital_signature = digital_signature
                profile.save()

                payment = Payment.objects.create(
                    user=user,
                    payment_type='SUBSCRIPTION',
                    amount=amount,
                    transaction_id=utr,
                    payment_mode='UPI',
                    due_date=date.today(),
                    status='PENDING_VERIFICATION',
                    description=f"Initial Subscription Request: {plan_type}",
                    metadata={
                        "email": email,
                        "plan_type": plan_type,
                        "plan_raw": data.get('plan_type'),
                        "institution_name": institution_name,
                        "phone": phone,
                        "submitted_from": "PUBLIC_PRICING_MODAL"
                    }
                )

                ClientSubscription.objects.update_or_create(
                    user=user,
                    defaults={
                        'plan_type': plan_type,
                        'status': 'PENDING',
                        'transaction_id': utr
                    }
                )

            # Notify user that verification is in progress (best effort)
            try:
                from student.services.email_service import send_payment_received_email
                send_payment_received_email(
                    email=email,
                    institution_name=institution_name,
                    plan_type=plan_type,
                    amount=str(amount),
                    utr=utr
                )
            except Exception:
                logger.warning("Could not send payment received email", exc_info=True)

            return Response({
                "status": "SUBMITTED_FOR_VERIFICATION",
                "message": "Payment submitted successfully!",
                "details": {
                    "utr_number": utr,
                    "amount": str(amount),
                    "plan_type": plan_type,
                    "verification_status": "PENDING"
                },
                "next_steps": [
                    "Admin will verify your payment with bank statement",
                    "You will receive credentials via email/SMS within 1-2 hours",
                    "Check your email for updates"
                ],
                "estimated_activation": "1-2 hours"
            }, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class UserPlanFeaturesView(APIView):
    """Get features available in user's plan"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from student.plan_permissions import get_user_features, get_user_plan, get_upgrade_options, PLAN_PRICING
        
        # Use the new dynamic resolver
        features_dict = get_user_features(request.user)
        current_plan = get_user_plan(request.user) # Institution Type (e.g. SCHOOL)
        
        upgrade_options = get_upgrade_options(request.user)
        current_price = PLAN_PRICING.get(current_plan, 0)
        
        return Response({
            "plan": current_plan,
            # Return list of feature keys for backward compatibility
            "features": list(features_dict.keys()),
            "features_meta": features_dict, # Rich metadata for UI
            "upgrade_options": upgrade_options, # Dynamic Upgrade Path
            "current_price": current_price
        })
