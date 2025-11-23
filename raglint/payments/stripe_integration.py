"""
Stripe payment integration for RAGLint Pro/Enterprise
"""

import stripe
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRICING = {
    "pro_monthly": {
        "price_id": "price_XXXXX",  # Replace with actual Stripe Price ID
        "amount": 4900,  # $49.00 in cents
        "interval": "month",
        "name": "RAGLint Pro (Monthly)"
    },
    "pro_yearly": {
        "price_id": "price_YYYYY",  # Replace with actual Stripe Price ID
        "amount": 47040,  # $490.40/year (20% discount)
        "interval": "year",
        "name": "RAGLint Pro (Annual)"
    },
    "enterprise": {
        "price_id": "price_ZZZZZ",  # Custom pricing
        "amount": 100000,  # $1,000/month minimum
        "interval": "month",
        "name": "RAGLint Enterprise"
    }
}

class StripePaymentManager:
    """Handle Stripe payments for RAGLint subscriptions"""
    
    def __init__(self):
        self.api_key = stripe.api_key
    
    def create_checkout_session(
        self,
        user_email: str,
        plan: str = "pro_monthly",
        quantity: int = 1,
        trial_days: int = 14
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session for subscription
        
        Args:
            user_email: Customer email
            plan: pro_monthly, pro_yearly, or enterprise
            quantity: Number of users/seats
            trial_days: Free trial period (default: 14 days)
        
        Returns:
            Checkout session with URL to redirect user
        """
        
        price_info = PRICING.get(plan)
        if not price_info:
            raise ValueError(f"Invalid plan: {plan}")
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                customer_email=user_email,
                line_items=[{
                    'price': price_info['price_id'],
                    'quantity': quantity,
                }],
                mode='subscription',
                subscription_data={
                    'trial_period_days': trial_days,
                    'metadata': {
                        'plan': plan,
                        'users': quantity
                    }
                },
                success_url='https://raglint.dev/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://raglint.dev/pricing',
                metadata={
                    'plan': plan,
                    'product': 'raglint'
                }
            )
            
            return {
                'session_id': session.id,
                'checkout_url': session.url,
                'trial_end': (datetime.now() + timedelta(days=trial_days)).isoformat()
            }
        
        except stripe.error.StripeError as e:
            return {'error': str(e)}
    
    def create_customer_portal_session(self, customer_id: str) -> Dict[str, str]:
        """
        Create a session for customer to manage their subscription
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url='https://raglint.dev/dashboard',
            )
            return {'portal_url': session.url}
        except stripe.error.StripeError as e:
            return {'error': str(e)}
    
    def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Handle Stripe webhook events
        
        Events to handle:
        - customer.subscription.created
        - customer.subscription.updated
        - customer.subscription.deleted
        - invoice.payment_succeeded
        - invoice.payment_failed
        """
        
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            return {'error': 'Invalid payload'}
        except stripe.error.SignatureVerificationError:
            return {'error': 'Invalid signature'}
        
        # Handle the event
        event_type = event['type']
        data = event['data']['object']
        
        if event_type == 'customer.subscription.created':
            return self._handle_subscription_created(data)
        
        elif event_type == 'customer.subscription.updated':
            return self._handle_subscription_updated(data)
        
        elif event_type == 'customer.subscription.deleted':
            return self._handle_subscription_deleted(data)
        
        elif event_type == 'invoice.payment_succeeded':
            return self._handle_payment_succeeded(data)
        
        elif event_type == 'invoice.payment_failed':
            return self._handle_payment_failed(data)
        
        return {'status': 'unhandled_event', 'type': event_type}
    
    def _handle_subscription_created(self, subscription):
        """
        New subscription created - activate Pro features
        """
        customer_id = subscription['customer']
        plan = subscription['metadata'].get('plan', 'pro_monthly')
        
        # TODO: Update user in database to Pro status
        # db.update_user_plan(customer_id, plan='pro', status='active')
        
        return {'status': 'subscription_activated', 'customer': customer_id}
    
    def _handle_subscription_updated(self, subscription):
        """
        Subscription updated - handle plan changes
        """
        customer_id = subscription['customer']
        status = subscription['status']
        
        # TODO: Update user plan status
        # db.update_user_status(customer_id, status=status)
        
        return {'status': 'subscription_updated', 'customer': customer_id}
    
    def _handle_subscription_deleted(self, subscription):
        """
        Subscription cancelled - downgrade to Community
        """
        customer_id = subscription['customer']
        
        # TODO: Downgrade user to community edition
        # db.update_user_plan(customer_id, plan='community', status='inactive')
        
        return {'status': 'subscription_cancelled', 'customer': customer_id}
    
    def _handle_payment_succeeded(self, invoice):
        """
        Payment succeeded - send receipt email
        """
        customer_id = invoice['customer']
        amount = invoice['amount_paid'] / 100  # Convert from cents
        
        # TODO: Send receipt email
        # email.send_receipt(customer_id, amount=amount)
        
        return {'status': 'payment_processed', 'amount': amount}
    
    def _handle_payment_failed(self, invoice):
        """
        Payment failed - notify customer
        """
        customer_id = invoice['customer']
        
        # TODO: Send payment failure email
        # email.send_payment_failure(customer_id)
        
        return {'status': 'payment_failed', 'customer': customer_id}

# Example usage
if __name__ == "__main__":
    manager = StripePaymentManager()
    
    # Create checkout for Pro monthly
    session = manager.create_checkout_session(
        user_email="customer@example.com",
        plan="pro_monthly",
        quantity=5  # 5 users
    )
    
    print(f"Checkout URL: {session['checkout_url']}")
    print(f"Trial ends: {session['trial_end']}")
