# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import AllowAny
# from .models import Order, OrderItem
# from .serializers import OrderSerializer
# from products.models import ClothingItem
#
#
# class PlaceOrderView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request):
#         serializer = OrderSerializer(data=request.data)
#         if serializer.is_valid():
#             cart_items = serializer.validated_data['cart_items']
#
#             # Initialize a new order entity
#             order = Order.objects.create(user=request.user, total_amount=0.00)
#             total = 0
#
#             for item in cart_items:
#                 try:
#                     product = ClothingItem.objects.get(id=item['product_id'])
#                     qty = item.get('quantity', 1)
#                     price = product.price * qty
#
#                     OrderItem.objects.create(
#                         order=order,
#                         product=product,
#                         quantity=qty,
#                         price=price
#                     )
#                     total += price
#                 except ClothingItem.DoesNotExist:
#                     order.delete()
#                     return Response(
#                         {"error": f"Product with ID {item['product_id']} is no longer available."},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#
#             order.total_amount = total
#             order.save()
#
#             return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class OrderHistoryView(APIView):
#     permission_classes = [AllowAny]
#
#     def get(self, request):
#         orders = Order.objects.filter(user=request.user).order_by('-created_at')
#         serializer = OrderSerializer(orders, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class OrderDetailsView(APIView):
#     permission_classes = [AllowAny]
#     def get(self, request, order_id):
#         try:
#             order = Order.objects.get(id=order_id, user=request.user)
#             serializer = OrderSerializer(order)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Order.DoesNotExist:
#             return Response(
#                 {"error": "The requested order tracking details could not be found or has no associated items."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#
# class PaymentStatusView(APIView):
#     permission_classes = [AllowAny]
#
#     def get(self, request):
#         order_id = request.query_params.get('order_id')
#         if not order_id:
#             return Response({"error": "Please provide an order_id parameter."}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             order = Order.objects.get(id=order_id, user=request.user)
#             return Response({
#                 "order_id": order.id,
#                 "payment_status": order.status,
#                 "amount_processed": order.total_amount,
#                 "gateway_reference": order.payment_intent_id or "MOCK_PAY_INTENT_99X"
#             }, status=status.HTTP_200_OK)
#         except Order.DoesNotExist:
#             return Response({"error": "No transaction records found for this order allocation."},
#                             status=status.HTTP_404_NOT_FOUND)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Order, OrderItem
from .serializers import OrderSerializer
from products.models import ClothingItem


# class PlaceOrderView(APIView):
#     permission_classes = [AllowAny]  # No login credentials required!
#
#     def post(self, request):
#         serializer = OrderSerializer(data=request.data)
#         if serializer.is_valid():
#             cart_items = serializer.validated_data['cart_items']
#
#             # We create the order without attaching a user relationship
#             order = Order.objects.create(total_amount=0.00)
#             total = 0
#
#             for item in cart_items:
#                 try:
#                     product = ClothingItem.objects.get(id=item['product_id'])
#                     qty = item.get('quantity', 1)
#                     price = product.price * qty
#
#                     OrderItem.objects.create(
#                         order=order,
#                         product=product,
#                         quantity=qty,
#                         price=price
#                     )
#                     total += price
#                 except ClothingItem.DoesNotExist:
#                     order.delete()
#                     return Response(
#                         {"error": f"Product with ID {item['product_id']} is no longer available."},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#
#             order.total_amount = total
#             order.save()
#
#             return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class PlaceOrderView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            cart_items = serializer.validated_data['cart_items']
            payment_mode = serializer.validated_data.get('payment_mode', 'immediate')

            # Decide the status based on the incoming checkout choice
            initial_status = "Success" if payment_mode == "immediate" else "Pending"

            # Create the order with your dynamic status
            order = Order.objects.create(total_amount="0.00", status=initial_status)
            total = 0

            for item in cart_items:
                try:
                    product = ClothingItem.objects.get(id=item['product_id'])
                    qty = item.get('quantity', 1)
                    price = product.price * qty

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        price=price
                    )
                    total += price
                except ClothingItem.DoesNotExist:
                    order.delete()
                    return Response(
                        {"error": f"Product with ID {item['product_id']} is no longer available."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            order.total_amount = total
            order.save()

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderHistoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Returns all orders in the system since we aren't filtering by user
        orders = Order.objects.all().order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetailsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, order_id):
        try:
            # Look up purely by the order's primary key ID
            order = Order.objects.get(id=order_id)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                {"error": "The requested order tracking details could not be found or has no associated items."},
                status=status.HTTP_404_NOT_FOUND
            )


class PaymentStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response({"error": "Please provide an order_id parameter."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id)
            return Response({
                "order_id": order.id,
                "payment_status": order.status,
                "amount_processed": order.total_amount,
                "gateway_reference": order.payment_intent_id or "MOCK_PAY_INTENT_99X"
            }, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "No transaction records found for this order allocation."},
                            status=status.HTTP_404_NOT_FOUND)