from django.db import models
from django.contrib.auth.models import User

class StockPrediction(models.Model):
    ticker = models.CharField(max_length=10)
    prediction_date = models.DateTimeField(auto_now_add=True)
    days_predicted = models.IntegerField()

    def __str__(self):
        return f"{self.ticker} - {self.prediction_date}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pan_card_number = models.CharField(max_length=10, unique=True)
    pan_card_verified = models.BooleanField(default=False)
    pan_card_image = models.ImageField(upload_to='pan_cards/', blank=True, null=True)
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    address = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.pan_card_number}"
