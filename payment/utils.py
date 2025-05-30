"""
Utility functions for payment processing.
"""
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Payment, MpesaTransaction, Notification

logger = logging.getLogger('payment.utils')

def update_transaction_status(mpesa_transaction, status, receipt_number=None, transaction_date=None, 
                             result_code=None, result_description=None):
    """
    Update an M-Pesa transaction's status and related records (payment, order)
    
    Args:
        mpesa_transaction: The MpesaTransaction object to update
        status: New status (COMPLETED, FAILED, CANCELLED)
        receipt_number: M-Pesa receipt number (for completed transactions)
        transaction_date: Date of transaction from M-Pesa
        result_code: Result code from M-Pesa
        result_description: Result description from M-Pesa
    """
    # Update transaction status
    mpesa_transaction.status = status
    
    if result_code is not None:
        mpesa_transaction.result_code = str(result_code)
    
    if result_description:
        mpesa_transaction.result_description = result_description
    
    if receipt_number:
        mpesa_transaction.mpesa_receipt_number = receipt_number
    
    if transaction_date:
        mpesa_transaction.transaction_date = transaction_date
    
    mpesa_transaction.updated_at = timezone.now()
    mpesa_transaction.save()
    
    # Update associated payment record
    payment = mpesa_transaction.payment
    if payment:
        # Update payment status based on transaction status
        if status == 'COMPLETED':
            payment.status = 'COMPLETED'
            payment.transaction_id = receipt_number
            
            # Update order status if this is an order payment
            if payment.payment_type == 'ORDER' and payment.order:
                order = payment.order
                order.status = 'PAID'
                order.save()
                
                # Create notification for order payment
                Notification.objects.create(
                    user=payment.user,
                    title='Order Payment Successful',
                    content=f'Your payment of {payment.amount} KES for order #{order.id} has been completed successfully.',
                    type='PAYMENT',
                    reference_id=str(payment.id)
                )
        else:
            payment.status = 'FAILED'
            
            # Create notification for failed payment
            Notification.objects.create(
                user=payment.user,
                title='Payment Failed',
                content=f'Your payment of {payment.amount} KES was not completed. Reason: {result_description}',
                type='PAYMENT',
                reference_id=str(payment.id)
            )
        
        payment.save()
    
    logger.info(f"Updated transaction {mpesa_transaction.id} to status: {status}")
    return mpesa_transaction


def expire_pending_transactions():
    """
    Mark old pending transactions as failed after a certain time period.
    This should be run as a scheduled task.
    """
    # Transactions older than 1 hour are considered expired
    expiry_time = timezone.now() - timedelta(hours=1)
    
    # Get all pending transactions older than expiry time
    pending_transactions = MpesaTransaction.objects.filter(
        status='PENDING',
        created_at__lt=expiry_time
    )
    
    count = 0
    for transaction in pending_transactions:
        update_transaction_status(
            transaction, 
            status='FAILED',
            result_description='Transaction expired due to no response from M-Pesa'
        )
        count += 1
    
    logger.info(f"Expired {count} pending M-Pesa transactions")
    return count
