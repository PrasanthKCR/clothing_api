# # from rest_framework import viewsets, status
# # from rest_framework.response import Response
# # from .models import ClothingItem
# # from .serializers import ClothingItemSerializer
# #
# # class ClothingItemViewSet(viewsets.ModelViewSet):
# #     queryset = ClothingItem.objects.all()
# #     serializer_class = ClothingItemSerializer
# #
# #     # This magic function allows you to POST a massive list array all at once!
# #     def create(self, request, *args, **kwargs):
# #         serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
# #         serializer.is_valid(raise_exception=True)
# #         self.perform_create(serializer)
# #         headers = self.get_success_headers(serializer.data)
# #         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#
#
# import django_filters
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from .models import ClothingItem
# from .serializers import ClothingItemSerializer
#
#
# # 1. Define custom filtering rules for our database fields
# class ClothingItemFilter(django_filters.FilterSet):
#     # This magic 'icontains' look-up searches inside our PostgreSQL JSON fields safely
#     color = django_filters.CharFilter(field_name='colors', lookup_expr='icontains')
#     size = django_filters.CharFilter(field_name='sizes', lookup_expr='icontains')
#
#     # Simple price range evaluation controls ($100 - $150 parameters)
#     min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
#     max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
#
#     class Meta:
#         model = ClothingItem
#         fields = ['color', 'size', 'min_price', 'max_price']
#
#
# # 2. Main ViewSet controlling API logic execution
# class ClothingItemViewSet(viewsets.ModelViewSet):
#     queryset = ClothingItem.objects.all()
#     serializer_class = ClothingItemSerializer
#     filterset_class = ClothingItemFilter
#
#     # Defines which fields our users are allowed to sort/order by
#     ordering_fields = ['price', 'model']
#     ordering = ['id']  # Default baseline database sorting rule
#
#     # Custom handling to intercept list queries and throw meaningful errors if empty
#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#
#         # If filtering/sorting leaves absolutely no records found:
#         if not queryset.exists():
#             return Response(
#                 {"error": "No clothing items are available matching your selection criteria."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         # Standard framework pagination rendering rules apply if records exist
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
#
#     # (Keep your existing 'create' method down here if you still need seeding capacity)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Count
from .models import ClothingItem
from .serializers import ClothingItemSerializer


# ==========================================
# 1. CATEGORY GRID VIEW (ALL PRODUCTS / FILTER / SORT / PAGINATION)
# ==========================================
class ProductGridListView(generics.ListCreateAPIView):
    serializer_class = ClothingItemSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = ClothingItem.objects.all()

        # Reading query strings dynamically from parameters
        gender = self.request.query_params.get('gender')
        category = self.request.query_params.get('category')
        color = self.request.query_params.get('color')
        size = self.request.query_params.get('size')
        sort_by = self.request.query_params.get('sort_by')

        # Precise Filtering checks
        if gender:
            queryset = queryset.filter(gender__iexact=gender)
        if category:
            queryset = queryset.filter(category__iexact=category)
        if color:
            queryset = queryset.filter(colors__icontains=color)
        if size:
            queryset = queryset.filter(sizes__icontains=size)

        # Precise Sorting check
        if sort_by:
            # Handles values like 'price' or '-price' (descending)
            queryset = queryset.order_by(sort_by)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"error": "No clothing items are available matching your selection criteria."},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().list(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data'), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


# ==========================================
# 2. PRODUCT DETAIL VIEW (GET BY ID)
# ==========================================
class ProductDetailView(APIView):
    def get(self, request, product_id):
        try:
            item = ClothingItem.objects.get(id=product_id)
            serializer = ClothingItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ClothingItem.DoesNotExist:
            return Response(
                {"error": f"Product with ID {product_id} is not available."},
                status=status.HTTP_404_NOT_FOUND
            )


# ==========================================
# 3. BASE MENU VIEW (GET ALL CATEGORIES BY GENDER)
# ==========================================
class BaseMenuView(APIView):
    def get(self, request, gender=None):
        queryset = ClothingItem.objects.all()

        if gender:
            if gender.lower() not in ['men', 'women', 'kids']:
                return Response({"error": "Invalid gender category specified."}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(gender__iexact=gender)

        if not queryset.exists():
            return Response({"error": "No menu items available."}, status=status.HTTP_404_NOT_FOUND)

        # Build a unique dictionary of categories and how many items they contain
        menu_summary = queryset.values('gender', 'category').annotate(total_items=Count('id'))

        return Response({"menu": menu_summary}, status=status.HTTP_200_OK)


# ==========================================
# 4. EXPANDED MENU ITEMS VIEW
# ==========================================
class MenuExpandView(APIView):
    def get(self, request, gender):
        if gender.lower() not in ['men', 'women', 'kids']:
            return Response({"error": "Gender category not found."}, status=status.HTTP_404_NOT_FOUND)

        items = ClothingItem.objects.filter(gender__iexact=gender)
        if not items.exists():
            return Response({"error": f"No menu items available for {gender}."}, status=status.HTTP_404_NOT_FOUND)

        # Groups all items organized directly under their assigned category headers
        expanded_menu = {}
        for item in items:
            if item.category not in expanded_menu:
                expanded_menu[item.category] = []
            expanded_menu[item.category].append({
                "id": item.id,
                "model": item.model,
                "price": item.price
            })

        return Response({"gender": gender, "categories": expanded_menu}, status=status.HTTP_200_OK)