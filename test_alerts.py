# test_alerts.py
# Save this in: C:\Users\HP\Desktop\crowd_safety_system\crowd_safety\test_alerts.py

import requests
import json
import sys

# Configuration
BASE_URL = 'http://127.0.0.1:8000/api/'

# You need to get a token first. Run this to create one:
# python manage.py drf_create_token admin
# Or use the session authentication by logging in first
AUTH_TOKEN = None  # Replace with actual token if using token auth
USERNAME = 'admin'  # Your superuser username
PASSWORD = 'admin123'  # Your superuser password

class AlertAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.token = None
        
    def login(self, username, password):
        """Login to get session cookie"""
        login_url = 'http://127.0.0.1:8000/accounts/login/'
        
        # Get CSRF token first
        self.session.get(login_url)
        
        # Login
        login_data = {
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': self.session.cookies.get('csrftoken', '')
        }
        
        response = self.session.post(login_url, data=login_data)
        
        if response.status_code == 200:
            print(f"✓ Logged in as {username}")
            return True
        else:
            print(f"✗ Login failed: {response.status_code}")
            return False
    
    def get_alerts(self):
        """Test GET /api/alerts/"""
        print("\n" + "="*50)
        print("Testing GET /api/alerts/")
        print("="*50)
        
        try:
            response = self.session.get(f'{self.base_url}alerts/')
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Found {data.get('count', 0)} alerts")
                print("\nRecent Alerts:")
                for alert in data.get('alerts', [])[:5]:
                    print(f"  - [{alert['priority'].upper()}] {alert['title']}")
                    print(f"    {alert['message'][:100]}...")
                return data
            else:
                print(f"Error: {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None
    
    def send_alert(self):
        """Test POST /api/alerts/"""
        print("\n" + "="*50)
        print("Testing POST /api/alerts/")
        print("="*50)
        
        alert_data = {
            'title': 'Test Alert from Python Script',
            'message': 'This is a test alert sent via the REST API at ' + 
                       __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'alert_type': 'security',
            'priority': 'high',
            'location': 'Times Square, New York',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'send_to_all': True
        }
        
        print(f"Sending alert: {alert_data['title']}")
        
        try:
            response = self.session.post(
                f'{self.base_url}alerts/',
                json=alert_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Alert sent successfully!")
                print(f"  Alert ID: {data.get('alert_id')}")
                print(f"  Message: {data.get('message')}")
                return data
            else:
                print(f"✗ Failed to send alert: {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None
    
    def trigger_panic(self):
        """Test POST /api/panic/"""
        print("\n" + "="*50)
        print("Testing POST /api/panic/")
        print("="*50)
        
        panic_data = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'message': 'Emergency test panic from Python script!',
            'location': 'Times Square, Main Entrance'
        }
        
        print("Triggering panic button...")
        
        try:
            response = self.session.post(
                f'{self.base_url}panic/',
                json=panic_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Panic alert sent!")
                print(f"  Panic ID: {data.get('panic_id')}")
                print(f"  Alert ID: {data.get('alert_id')}")
                print(f"  Message: {data.get('message')}")
                return data
            else:
                print(f"✗ Failed to send panic: {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None
    
    def get_crowd_data(self):
        """Test GET /api/crowd/"""
        print("\n" + "="*50)
        print("Testing GET /api/crowd/")
        print("="*50)
        
        try:
            response = self.session.get(f'{self.base_url}crowd/')
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Found {data.get('count', 0)} crowd data points")
                print("\nCrowd Data:")
                for item in data.get('data', [])[:5]:
                    print(f"  - {item['location']}: {item['density'].upper()} ({item['count']} people)")
                return data
            else:
                print(f"Error: {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None
    
    def acknowledge_alert(self, alert_id):
        """Test POST /api/alerts/<id>/acknowledge/"""
        print("\n" + "="*50)
        print(f"Testing POST /api/alerts/{alert_id}/acknowledge/")
        print("="*50)
        
        try:
            response = self.session.post(f'{self.base_url}alerts/{alert_id}/acknowledge/')
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Alert {alert_id} acknowledged!")
                print(f"  {data.get('message')}")
                return data
            else:
                print(f"✗ Failed to acknowledge: {response.text}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None

def main():
    """Main test function"""
    print("\n" + "="*60)
    print(" CROWD SAFETY SYSTEM - ALERT API TESTER")
    print("="*60)
    
    tester = AlertAPITester()
    
    # Login
    print("\nPlease enter your credentials:")
    username = input("Username (default: admin): ").strip() or 'admin'
    password = input("Password: ").strip()
    
    if not password:
        print("Password required!")
        return
    
    if not tester.login(username, password):
        print("Login failed. Please check your credentials and make sure the server is running.")
        return
    
    # Test menu
    while True:
        print("\n" + "-"*40)
        print("Select test to run:")
        print("1. Get Alerts")
        print("2. Send New Alert")
        print("3. Trigger Panic Button")
        print("4. Get Crowd Data")
        print("5. Acknowledge Alert (enter ID)")
        print("6. Run All Tests")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-6): ").strip()
        
        if choice == '1':
            tester.get_alerts()
        elif choice == '2':
            tester.send_alert()
        elif choice == '3':
            tester.trigger_panic()
        elif choice == '4':
            tester.get_crowd_data()
        elif choice == '5':
            alert_id = input("Enter alert ID to acknowledge: ").strip()
            if alert_id.isdigit():
                tester.acknowledge_alert(int(alert_id))
            else:
                print("Invalid alert ID")
        elif choice == '6':
            print("\n" + "="*60)
            print(" RUNNING ALL TESTS")
            print("="*60)
            tester.get_alerts()
            tester.send_alert()
            tester.trigger_panic()
            tester.get_crowd_data()
        elif choice == '0':
            print("\nExiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)