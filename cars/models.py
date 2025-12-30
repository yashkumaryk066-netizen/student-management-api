from django.db import models

class Manufacturer(models.Model):
    name = models.CharField(max_length=5000)
    location = models.CharField(max_length=5000)
    phone_number = models.IntegerField()
    is_ready = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Car(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, related_name="cars", on_delete=models.CASCADE)
    model_name = models.CharField(max_length=2000)
    year = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.model_name

class ServicingCenter(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, related_name="service_centers", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    



