from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _
from orders.models import Cart, CartItems
from course.models import Course, Enrollment
from .serializers import CourseInformationSerializer
from orders.services import _calculate_all_order_totals_helper, get_craft_user_by_email
from accounts.models import Address
from returnrequest.models import Transaction
from Handcrafts.business_config import calculate_course_split
from notifications.services import create_notification_for_user
import uuid
from .models import PaymentHistory, StripeWebhookEvent
from django.views.decorators.csrf import csrf_exempt
from notifications.services import create_notification_for_user

# Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentViewSet(viewsets.ViewSet):
    """
    Handles payment processing for Orders.
    """

    @action(detail=False, methods=["post"])
    def process_order_payment(self, request):
        user = request.user
        cart = get_object_or_404(Cart, User=user)
        address_id = request.data.get("address_id")
        coupon_code = request.data.get("coupon_code")

        try:
            address = Address.objects.get(user=user, id=address_id)
        except Address.DoesNotExist:
            raise ValidationError(_("Address not found or does not belong to the user."))

        cart_items = CartItems.objects.filter(CartID=cart)

        if not cart_items.exists():
            raise ValidationError({"message": _("Cart is empty. Cannot create order.")})

        totals = _calculate_all_order_totals_helper(cart_items, coupon_code, address, user)

        payment_history = PaymentHistory.objects.create(
            user=user,
            cart=cart,
            payment_status='pending',
            address_id=address,
            coupon_code=coupon_code,
        )

        success_url = f"crafterapp://payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = "crafterapp://payment/failure"

        session_data = {
            "mode": "payment",
            "client_reference_id": str(payment_history.id),
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }

        delivery_fee = totals['delivery_fee'] if totals['delivery_fee'] else Decimal("0.00")
        
        for item in cart_items:
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(item.Product.UnitPrice * Decimal("100")),
                        "currency": "EGP",
                        "product_data": {
                            "name": item.Product.ProductName,
                            "description": item.Product.ProductDescription,
                        },
                    },
                    "quantity": item.Quantity,
                }
            )

        if delivery_fee > 0:
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(delivery_fee * Decimal("100")),
                        "currency": "EGP",
                        "product_data": {
                            "name": _("Delivery Fee"),
                        },
                    },
                    "quantity": 1,
                }
            )

        if totals['discount_amount'] > 0:
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": -int(totals['discount_amount'] * Decimal("100")),
                        "currency": "EGP",
                        "product_data": {
                            "name": _("Discount"),
                        },
                    },
                    "quantity": 1,
                }
            )
        
        try:
            session = stripe.checkout.Session.create(
                **session_data, 
                idempotency_key=str(uuid.uuid4())
            )
            payment_history.stripe_session_id = session.id
            payment_history.save()
            return Response({"status": "success", "url": session.url})
        except stripe.error.StripeError as e:
            payment_history.payment_status = 'failed'
            payment_history.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CoursePaymentViewSet(viewsets.ViewSet):
    """
    Handles payment processing for Courses.
    """

    @action(detail=False, methods=["post"])
    def process_course_payment(self, request):
        serializer = CourseInformationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course_id = serializer.validated_data["course_id"]
        course = get_object_or_404(Course, CourseID=course_id)
        
        buyer = request.user
        
        if buyer == course.Supplier.user:
            return Response({"error": _("You cannot purchase your own course.")}, status=status.HTTP_400_BAD_REQUEST)

        if Enrollment.objects.filter(Course=course, EnrolledUser=buyer).exists():
            return Response({"error": _("You are already enrolled in this course.")}, status=status.HTTP_400_BAD_REQUEST)

        payment_history = PaymentHistory.objects.create(
            user=buyer,
            course=course,
            payment_status='pending'
        )

        success_url = f"crafterapp://payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = "crafterapp://payment/failure"

        session_data = {
            "mode": "payment",
            "client_reference_id": f"course:{course.CourseID}",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [{
                "price_data": {
                    "unit_amount": int(course.Price * Decimal("100")),
                    "currency": "EGP",
                    "product_data": {
                        "name": course.CourseTitle,
                    },
                },
                "quantity": 1,
            }],
        }
        
        try:
            session = stripe.checkout.Session.create(
                **session_data,
                idempotency_key=str(uuid.uuid4())
            )
            payment_history.stripe_session_id = session.id
            payment_history.save()
            return Response({"status": "success", "url": session.url})
        except stripe.error.StripeError as e:
            payment_history.payment_status = 'failed'
            payment_history.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def payment_completed(request):
    """
    Endpoint for successful payment redirect.
    Returns a deep link URL for the mobile app.
    """
    session_id = request.GET.get('session_id')
    
    deep_link = f"crafterapp://payment/success?session_id={session_id}"
    return Response({"status": "success", "redirect_url": deep_link})

@api_view(['GET'])
def payment_canceled(request):
    """
    Endpoint for canceled payment redirect.
    Returns a deep link URL for the mobile app.
    """
    deep_link = "crafterapp://payment/failure"
    return Response({"status": "canceled", "redirect_url": deep_link})

@csrf_exempt
@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        )
    except ValueError as e:
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        return Response(status=400)

    # Idempotency check
    if StripeWebhookEvent.objects.filter(event_id=event['id']).exists():
        return Response({'status': 'already processed'}, status=200)

    StripeWebhookEvent.objects.create(event_id=event['id'], event_type=event['type'])

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        try:
            history = PaymentHistory.objects.get(stripe_session_id=session.get('id'))
            history.payment_status = 'succeeded'
            history.save()
            
            if history.order:
                history.order.Status = 'PROCESSING'
                history.order.save()
            elif history.course:
                Enrollment.objects.get_or_create(Course=history.course, EnrolledUser=history.user)
                
                # Apply Course Revenue Sharing
                course_split = calculate_course_split(history.course.Price)
                instructor_revenue = course_split["instructor_revenue"]
                platform_commission = course_split["platform_commission"]
                
                instructor = history.course.Supplier.user
                instructor.Balance += instructor_revenue
                instructor.save(update_fields=['Balance'])
                
                # Record transaction for instructor
                Transaction.objects.create(
                    user=instructor, 
                    transaction_type=Transaction.TransactionType.PURCHASED_COURSE, 
                    amount=instructor_revenue
                )
                
                # Record transaction for platform
                Craft = get_craft_user_by_email("CraftEG@craft.com")
                if Craft:
                    Craft.Balance += platform_commission
                    Craft.save(update_fields=['Balance'])
                    Transaction.objects.create(
                        user=Craft, 
                        transaction_type=Transaction.TransactionType.PURCHASED_COURSE, 
                        amount=platform_commission
                    )
                
            create_notification_for_user(history.user, "Payment Successful", "Your payment has been successfully processed.")
        except PaymentHistory.DoesNotExist:
            pass

    return Response(status=200)