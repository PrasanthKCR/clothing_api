# from django.db import models
#
# class ClothingItem(models.Model):
#     model = models.CharField(max_length=255)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=6, decimal_places=2)
#     sizes = models.JSONField(default=list)
#     colors = models.JSONField(default=list)
#
#     def __str__(self):
#         return self.model

from django.db import models

class ClothingItem(models.Model):
    # Added for Menu tracking
    GENDER_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('kids', 'Kids'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='men')
    category = models.CharField(max_length=50, default='Shirts')  # e.g., Jackets, Dresses, Pants

    # Existing fields
    model = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sizes = models.JSONField(default=list)
    colors = models.JSONField(default=list)

    def __str__(self):
        return f"[{self.gender.upper()}] {self.model}"