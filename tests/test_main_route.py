import unittest
from unittest.mock import patch
from app import app, db, City
import tempfile
import os

class WeatherAppMainRouteTest(unittest.TestCase):
    def setUp(self):
        # Create a temporary database
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    @patch('app.get_weather_data')
    def test_main_route_get_request_with_cities(self, mock_weather_data):
        """Test the main route ("/") returns a 200 status code and renders the correct template with cities"""
        # Mock weather data for any existing cities
        mock_weather_data.return_value = {
            "cod": 200,
            "main": {"temp": 75.2},
            "weather": [{"description": "partly cloudy", "icon": "02d"}]
        }
        
        # Add test cities to the database
        with app.app_context():
            test_city1 = City(name='New York')
            test_city2 = City(name='Paris')
            db.session.add(test_city1)
            db.session.add(test_city2)
            db.session.commit()
        
        response = self.app.get('/')
        
        # Check status code
        self.assertEqual(response.status_code, 200)
        
        # Check that the response contains HTML content (indicating template was rendered)
        self.assertIn(b'<html', response.data.lower())
        
        # Check for weather-related content that should be in the template
        self.assertIn(b'New York', response.data)
        self.assertIn(b'Paris', response.data)
        
        # Verify the mock was called for each city
        self.assertEqual(mock_weather_data.call_count, 2)

    def test_main_route_get_request_empty_database(self):
        """Test the main route with no cities in database"""
        response = self.app.get('/')
        
        # Should still return 200 and render template
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<html', response.data.lower())

    @patch('app.get_weather_data')
    def test_main_route_renders_weather_template(self, mock_weather_data):
        """Test that the main route renders the weather.html template"""
        # Mock weather data
        mock_weather_data.return_value = {
            "cod": 200,
            "main": {"temp": 68.0},
            "weather": [{"description": "sunny", "icon": "01d"}]
        }
        
        # Add a test city
        with app.app_context():
            test_city = City(name='London')
            db.session.add(test_city)
            db.session.commit()
        
        response = self.app.get('/')
        
        # Check that temperature and weather description appear in response
        self.assertIn(b'68.0', response.data)
        self.assertIn(b'sunny', response.data)
        self.assertIn(b'London', response.data)

    @patch('app.get_weather_data')
    def test_main_route_handles_weather_api_error(self, mock_weather_data):
        """Test main route behavior when weather API returns an error"""
        # Mock API error response
        mock_weather_data.side_effect = KeyError("API error")
        
        # Add a test city
        with app.app_context():
            test_city = City(name='TestCity')
            db.session.add(test_city)
            db.session.commit()
        
        # This should raise an exception in the current implementation
        # In a production app, you'd want to handle this gracefully
        with self.assertRaises(KeyError):
            response = self.app.get('/')

    def test_main_route_content_type(self):
        """Test that the main route returns HTML content type"""
        response = self.app.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)

if __name__ == '__main__':
    unittest.main()