import unittest
from unittest.mock import patch, MagicMock
from app import app, db, City
import tempfile
import os


class WeatherAppFormSubmissionTest(unittest.TestCase):
    def setUp(self):
        # Create a temporary database
        self.db_fd, app.config["DATABASE"] = tempfile.mkstemp()
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["WTF_CSRF_ENABLED"] = False

        self.app = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config["DATABASE"])

    @patch("app.get_weather_data")
    def test_valid_city_name_success(self, mock_weather_data):
        """Test form submission with a valid city name"""
        # Mock successful API response
        mock_weather_data.return_value = {
            "cod": 200,
            "main": {"temp": 72.5},
            "weather": [{"description": "clear sky", "icon": "01d"}],
        }

        response = self.app.post("/", data={"city": "London"}, follow_redirects=True)

        # Should redirect back to index with success message
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"City added successfully!", response.data)

        # Check that city was added to database
        with app.app_context():
            city = City.query.filter_by(name="London").first()
            self.assertIsNotNone(city)

    @patch("app.get_weather_data")
    def test_invalid_city_name_error(self, mock_weather_data):
        """Test form submission with an invalid city name"""
        # Mock API response for invalid city
        mock_weather_data.return_value = {"cod": 404, "message": "city not found"}

        response = self.app.post(
            "/", data={"city": "InvalidCityName123"}, follow_redirects=True
        )

        # Should redirect back to index with error message
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"That is not a valid city!", response.data)

        # Check that city was NOT added to database
        with app.app_context():
            city = City.query.filter_by(name="InvalidCityName123").first()
            self.assertIsNone(city)

    @patch("app.get_weather_data")
    def test_duplicate_city_error(self, mock_weather_data):
        """Test form submission with a city that already exists"""
        # Mock successful API response
        mock_weather_data.return_value = {
            "cod": 200,
            "main": {"temp": 72.5},
            "weather": [{"description": "clear sky", "icon": "01d"}],
        }

        # Add city first time using same normalization as app
        import string

        with app.app_context():
            normalized_name = string.capwords("london")
            city = City(name=normalized_name)
            db.session.add(city)
            db.session.commit()

        # Try to add same city again
        response = self.app.post("/", data={"city": "london"}, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"City already exists in the database!", response.data)

    def test_empty_city_name(self):
        """Test form submission with empty city name"""
        response = self.app.post("/", data={"city": ""}, follow_redirects=True)

        # Should redirect without error (empty city is ignored)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
