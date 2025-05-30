"""
Views for handling M-Pesa payment transactions.
"""
import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from .models import Payment, MpesaTransaction
from merchandise.models import Order
from .serializers import (
    PaymentCreateSerializer, PaymentDetailSerializer,
    MpesaTransactionSerializer, MpesaTransactionCreateSerializer,
    MpesaTransactionDetailSerializer
)
from .daraja import initiate_stk_push, query_stk_status, process_callback
from .utils import update_transaction_status
from users.permissions import IsAdminOrManager, IsAdminOrManagerOrOwner


class MpesaTransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for M-Pesa transactions
    """
    queryset = MpesaTransaction.objects.all().order_by('-created_at')
    serializer_class = MpesaTransactionSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        elif self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated(), IsAdminOrManagerOrOwner()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # Regular users can only see their own transactions
        if self.request.user.is_authenticated and self.request.user.role not in ['ADMIN', 'MANAGER']:
            queryset = queryset.filter(payment__user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def initiate_order_payment(self, request):
        """
        Initiate an M-Pesa payment for an order
        """
        # Validate order_id and phone_number
        order_id = request.data.get('order_id')
        phone_number = request.data.get('phone_number')
        
        if not order_id:
            return Response(
                {"error": "Order ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not phone_number:
            return Response(
                {"error": "Phone number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check phone number format (should be 254XXXXXXXXX)
        if not phone_number.startswith('254') or not phone_number.isdigit() or len(phone_number) != 12:
            return Response(
                {"error": "Phone number must be in the format 254XXXXXXXXX"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the order
            order = Order.objects.get(id=order_id, user=request.user)
            
            # Check if order is already paid
            if order.status != 'PENDING':
                return Response(
                    {"error": f"Order is already in '{order.status}' status"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create a payment record
            payment_data = {
                'user': request.user,
                'amount': order.total_amount,
                'payment_type': 'ORDER',
                'payment_method': 'MPESA',
                'order': order
            }
            payment = Payment.objects.create(**payment_data)
            
            # Create M-Pesa transaction record
            mpesa_data = {
                'payment': payment,
                'phone_number': phone_number,
                'amount': order.total_amount,
                'reference': f"Order-{order.id}",
                'description': f"Payment for JKUELC Order #{order.id}"
            }
            mpesa_transaction = MpesaTransaction.objects.create(**mpesa_data)
            
            # Construct callback URL - use configured one if available, otherwise build from request
            callback_url = settings.MPESA_CALLBACK_URL
            if not callback_url:
                # Build callback URL from request (only works if server is publicly accessible)
                host = request.get_host()
                protocol = 'https' if request.is_secure() else 'http'
                callback_url = f"{protocol}://{host}{reverse('mpesa-callback')}"
                
            # Log the callback URL being used
            logger.info(f"Using M-Pesa callback URL: {callback_url}")
            
            # Initiate STK Push
            stk_response = initiate_stk_push(
                phone_number=phone_number,
                amount=order.total_amount,
                account_reference=f"Order-{order.id}",
                transaction_desc=f"Payment for JKUELC Order #{order.id}",
                callback_url=callback_url
            )
            
            # Update transaction with response data
            if 'error' not in stk_response:
                mpesa_transaction.merchant_request_id = stk_response.get('MerchantRequestID')
                mpesa_transaction.checkout_request_id = stk_response.get('CheckoutRequestID')
                mpesa_transaction.raw_response = stk_response
                mpesa_transaction.save()
                
                return Response({
                    'message': 'Payment initiated. Please check your phone to complete the transaction.',
                    'transaction_id': mpesa_transaction.id,
                    'checkout_request_id': mpesa_transaction.checkout_request_id
                })
            else:
                # Payment initiation failed
                mpesa_transaction.status = 'FAILED'
                mpesa_transaction.result_description = stk_response.get('error')
                mpesa_transaction.raw_response = stk_response
                mpesa_transaction.save()
                
                # Update payment status
                payment.status = 'FAILED'
                payment.save()
                
                return Response(
                    {"error": "Failed to initiate payment", "details": stk_response.get('error')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found or you don't have permission to pay for it"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def check_status(self, request, pk=None):
        """
        Check the status of an M-Pesa transaction
        """
        mpesa_transaction = self.get_object()
        
        if not mpesa_transaction.checkout_request_id:
            return Response(
                {"error": "Transaction has not been initiated with M-Pesa"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Query STK status
            status_response = query_stk_status(mpesa_transaction.checkout_request_id)
            
            # Update transaction with response data
            mpesa_transaction.raw_response = status_response
            
            if 'error' not in status_response:
                result_code = status_response.get('ResultCode')
                result_desc = status_response.get('ResultDesc')
                
                # Use utility function to update transaction status
                if result_code == 0:
                    update_transaction_status(
                        mpesa_transaction=mpesa_transaction,
                        status='COMPLETED',
                        result_code=result_code,
                        result_description=result_desc
                    )
                elif result_code == 1032:  # Request cancelled by user
                    update_transaction_status(
                        mpesa_transaction=mpesa_transaction,
                        status='CANCELLED',
                        result_code=result_code,
                        result_description=result_desc
                    )
                else:
                    update_transaction_status(
                        mpesa_transaction=mpesa_transaction,
                        status='FAILED',
                        result_code=result_code,
                        result_description=result_desc
                    )
                
                return Response({
                    'status': mpesa_transaction.status,
                    'result_code': result_code,
                    'result_description': result_desc
                })
            else:
                return Response(
                    {"error": "Failed to check transaction status", "details": status_response.get('error')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error checking transaction status: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def payment_status(self, request):
        """
        Check payment status for an order (customer-facing endpoint)
        """
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response(
                {"error": "order_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verify user has access to this order
            order = Order.objects.get(id=order_id)
            if request.user.role not in ['ADMIN', 'MANAGER'] and order.user != request.user:
                return Response(
                    {"error": "You do not have permission to check this order's payment status"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get payment status
            payments = Payment.objects.filter(order=order)
            if not payments.exists():
                return Response({
                    'order_id': order_id,
                    'payment_status': 'NO_PAYMENT',
                    'order_status': order.status,
                    'message': 'No payment has been initiated for this order'
                })
            
            # Get latest payment
            latest_payment = payments.order_by('-created_at').first()
            
            # Check if there's an M-Pesa transaction
            try:
                mpesa_transaction = MpesaTransaction.objects.get(payment=latest_payment)
                
                # If transaction is still pending and older than 2 minutes, check status
                if mpesa_transaction.status == 'PENDING' and \
                   (timezone.now() - mpesa_transaction.created_at).seconds > 120:
                    try:
                        # Check transaction status with M-Pesa
                        status_response = query_stk_status(mpesa_transaction.checkout_request_id)
                        
                        if 'error' not in status_response:
                            result_code = status_response.get('ResultCode')
                            result_desc = status_response.get('ResultDesc')
                            
                            if result_code == 0:
                                update_transaction_status(
                                    mpesa_transaction=mpesa_transaction,
                                    status='COMPLETED',
                                    result_code=result_code,
                                    result_description=result_desc
                                )
                            elif result_code == 1032:
                                update_transaction_status(
                                    mpesa_transaction=mpesa_transaction,
                                    status='CANCELLED',
                                    result_code=result_code,
                                    result_description=result_desc
                                )
                            else:
                                update_transaction_status(
                                    mpesa_transaction=mpesa_transaction,
                                    status='FAILED',
                                    result_code=result_code,
                                    result_description=result_desc
                                )
                    except Exception as e:
                        logger.error(f"Error checking transaction status for order {order_id}: {e}")
                
                return Response({
                    'order_id': order_id,
                    'payment_id': latest_payment.id,
                    'transaction_id': mpesa_transaction.id,
                    'payment_status': latest_payment.status,
                    'mpesa_status': mpesa_transaction.status,
                    'order_status': order.status,
                    'amount': latest_payment.amount,
                    'phone_number': mpesa_transaction.phone_number,
                    'mpesa_receipt': mpesa_transaction.mpesa_receipt_number,
                    'created_at': latest_payment.created_at.isoformat(),
                    'message': mpesa_transaction.result_description or ''
                })
                
            except MpesaTransaction.DoesNotExist:
                return Response({
                    'order_id': order_id,
                    'payment_id': latest_payment.id,
                    'payment_status': latest_payment.status,
                    'payment_method': latest_payment.payment_method,
                    'order_status': order.status,
                    'amount': latest_payment.amount,
                    'created_at': latest_payment.created_at.isoformat(),
                })
                
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting payment status: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Public endpoint for M-Pesa callbacks
def mpesa_callback(request):
    """
    Callback endpoint for M-Pesa to send transaction status
    """
    try:
        callback_data = request.data
        logger.info(f"Received M-Pesa callback: {callback_data}")
        
        # Process the callback data
        payment_info = process_callback(callback_data)
        
        if 'error' not in payment_info:
            checkout_request_id = payment_info.get('checkout_request_id')
            
            # Find the associated transaction
            try:
                mpesa_transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
                
                # Update transaction with callback data
                if payment_info.get('result_code') == 0:
                    # Transaction successful
                    update_transaction_status(
                        mpesa_transaction=mpesa_transaction,
                        status='COMPLETED',
                        receipt_number=payment_info.get('mpesa_receipt_number'),
                        transaction_date=payment_info.get('transaction_date'),
                        result_code=payment_info.get('result_code'),
                        result_description=payment_info.get('result_desc')
                    )
                    logger.info(f"Successfully processed M-Pesa payment for transaction {checkout_request_id}")
                else:
                    # Transaction failed
                    update_transaction_status(
                        mpesa_transaction=mpesa_transaction,
                        status='FAILED',
                        result_code=payment_info.get('result_code'),
                        result_description=payment_info.get('result_desc')
                    )
                    logger.warning(f"Failed M-Pesa payment for transaction {checkout_request_id}")
                
                # Store the full callback data
                mpesa_transaction.raw_response = callback_data
                mpesa_transaction.save(update_fields=['raw_response'])
                
                return Response({"ResultCode": 0, "ResultDesc": "Success"})
            
            except MpesaTransaction.DoesNotExist:
                # If no transaction is found, still acknowledge receipt to M-Pesa
                logger.warning(f"Received callback for unknown transaction: {checkout_request_id}")
                return Response({"ResultCode": 0, "ResultDesc": "Success"})
        else:
            # Error processing callback data
            logger.error(f"Error processing M-Pesa callback: {payment_info.get('error')}")
            return Response({"ResultCode": 0, "ResultDesc": "Success"})
    
    except Exception as e:
        # Log the error but still acknowledge receipt to M-Pesa
        logger.error(f"Exception in M-Pesa callback: {str(e)}")
        # Always return success to M-Pesa even if we have internal errors
        return Response({"ResultCode": 0, "ResultDesc": "Success"})
