import unittest
from data import (
    categorise_temperature,
    categorise_humidity
)

from data import categorise_wind


class TestWeatherFunctions(unittest.TestCase):

    #Temperature Tests
    def test_temperature_categories(self):
        self.assertEqual(categorise_temperature(-5), "Freezing")
        self.assertEqual(categorise_temperature(5), "Cold")
        self.assertEqual(categorise_temperature(10), "Cool")
        self.assertEqual(categorise_temperature(16), "Mild")
        self.assertEqual(categorise_temperature(25), "Warm")

    #Wind Tests
    def test_wind_categories(self):
        self.assertEqual(categorise_wind(2), "Calm")
        self.assertEqual(categorise_wind(5), "Breezy")
        self.assertEqual(categorise_wind(10), "Windy")
        self.assertEqual(categorise_wind(20), "Storm")

    #Humidity Tests
    def test_humidity_categories(self):
        self.assertEqual(categorise_humidity(30), "Dry")
        self.assertEqual(categorise_humidity(50), "Comfortable")
        self.assertEqual(categorise_humidity(80), "Humid")


if __name__ == "__main__":
    unittest.main()