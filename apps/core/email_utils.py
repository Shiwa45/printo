# apps/core/email_utils.py
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class EmailNotificationService:
    """Service for sending email notifications"""
    
    @staticmethod
    def send_order_confirmation(order, user_email=None):
        """Send order confirmation email"""
        try:
            email = user_email or order.user.email if order.user else order.guest_email
            if not email:
                logger.warning(f"No email address for order {order.order_number}")
                return False
            
            context = {
                'order': order,
                'order_items': order.items.all(),
                'site_name': 'Drishthi Printing',
                'support_email': settings.DEFAULT_FROM_EMAIL,
                'site_url': getattr(settings, 'SITE_URL', 'https://drishthi.com')
            }
            
            subject = f'Order Confirmation - #{order.order_number}'
            html_content = render_to_string('emails/order_confirmation.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Order confirmation sent for order {order.order_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send order confirmation: {e}")
            return False
    
    @staticmethod
    def send_order_status_update(order, new_status, user_email=None):
        """Send order status update email"""
        try:
            email = user_email or order.user.email if order.user else order.guest_email
            if not email:
                return False
            
            status_messages = {
                'confirmed': 'Your order has been confirmed and is being prepared.',
                'in_production': 'Your order is now in production.',
                'quality_check': 'Your order is undergoing quality check.',
                'ready': 'Your order is ready for pickup/shipping.',
                'shipped': 'Your order has been shipped.',
                'delivered': 'Your order has been delivered.',
                'cancelled': 'Your order has been cancelled.'
            }
            
            context = {
                'order': order,
                'status_message': status_messages.get(new_status, 'Your order status has been updated.'),
                'new_status': new_status,
                'site_name': 'Drishthi Printing',
                'support_email': settings.DEFAULT_FROM_EMAIL,
                'site_url': getattr(settings, 'SITE_URL', 'https://drishthi.com')
            }
            
            subject = f'Order Update - #{order.order_number}'
            html_content = render_to_string('emails/order_status_update.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Status update sent for order {order.order_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")
            return False
    
    @staticmethod
    def send_contact_notification(contact_submission):
        """Send notification to admin about new contact submission"""
        try:
            admin_emails = [settings.DEFAULT_FROM_EMAIL]
            if hasattr(settings, 'ADMIN_NOTIFICATION_EMAILS'):
                admin_emails = settings.ADMIN_NOTIFICATION_EMAILS
            
            context = {
                'submission': contact_submission,
                'site_name': 'Drishthi Printing',
                'admin_url': getattr(settings, 'SITE_URL', 'https://drishthi.com') + '/admin/'
            }
            
            subject = f'New Contact Inquiry - {contact_submission.subject}'
            html_content = render_to_string('emails/contact_notification.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=admin_emails
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Contact notification sent for submission {contact_submission.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send contact notification: {e}")
            return False
    
    @staticmethod
    def send_contact_confirmation(contact_submission):
        """Send confirmation email to customer"""
        try:
            context = {
                'submission': contact_submission,
                'site_name': 'Drishthi Printing',
                'support_email': settings.DEFAULT_FROM_EMAIL,
                'site_url': getattr(settings, 'SITE_URL', 'https://drishthi.com')
            }
            
            subject = 'Thank you for contacting Drishthi Printing'
            html_content = render_to_string('emails/contact_confirmation.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[contact_submission.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Contact confirmation sent to {contact_submission.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send contact confirmation: {e}")
            return False
    
    @staticmethod
    def send_quote_notification(quote_request):
        """Send quote request notification to admin"""
        try:
            admin_emails = [settings.DEFAULT_FROM_EMAIL]
            if hasattr(settings, 'ADMIN_NOTIFICATION_EMAILS'):
                admin_emails = settings.ADMIN_NOTIFICATION_EMAILS
            
            context = {
                'quote': quote_request,
                'site_name': 'Drishthi Printing',
                'admin_url': getattr(settings, 'SITE_URL', 'https://drishthi.com') + '/admin/'
            }
            
            subject = f'New Quote Request - {quote_request.request_number}'
            html_content = render_to_string('emails/quote_notification.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=admin_emails
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Quote notification sent for {quote_request.request_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send quote notification: {e}")
            return False