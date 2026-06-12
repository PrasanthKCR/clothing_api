from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    # Changed from product.name to product.model
    product_name = serializers.ReadOnlyField(source='product.model')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    cart_items = serializers.JSONField(write_only=True)

    # CRITICAL: Make sure write_only=True is here!
    payment_mode = serializers.CharField(write_only=True, required=False, default='immediate')

    class Meta:
        model = Order
        # Make sure payment_mode is listed in fields
        fields = ['id', 'created_at', 'status', 'total_amount', 'payment_intent_id', 'items', 'cart_items',
                  'payment_mode']

    def validate_cart_items(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("Cannot place an order. Your checkout basket is empty or items are unavailable.")
        return value