from django.test import TestCase
from .models import Car, CarModel


class CarTestCase(TestCase):
    def setUp(self):
        car_model = CarModel.objects.create(name='new car model')
        car = Car.objects.create(carNumber='01W000WW', model=car_model)
        car_model.name = 'test new car model'
        car_model.save()
        car.model = car_model
        car.save()

    def test_car_trades(self):
        car = Car.objects.get(carNumber='01W000WW')
        self.assertEqual('test', 'test', 'Message if not equal')
