from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from plyer import notification
from geopy.distance import geodesic
import threading
import time
import geocoder  # For fetching location


class ReminderApp(BoxLayout):
    def __init__(self, **kwargs):
        super(ReminderApp, self).__init__(**kwargs)
        self.orientation = "vertical"

        # Input for the item to buy
        self.item_label = Label(text="Item to Buy:")
        self.item_input = TextInput(hint_text="Enter the item")
        self.add_widget(self.item_label)
        self.add_widget(self.item_input)

        # Input for latitude and longitude
        self.location_label = Label(text="Target Location (Latitude, Longitude):")
        self.location_input = TextInput(hint_text="Enter as lat,lon (e.g., 37.7749,-122.4194)")
        self.add_widget(self.location_label)
        self.add_widget(self.location_input)

        # Button to set the reminder
        self.set_alarm_button = Button(text="Set Reminder")
        self.set_alarm_button.bind(on_press=self.set_alarm)
        self.add_widget(self.set_alarm_button)

        # Placeholder for user location
        self.user_location = None
        self.target_location = None
        self.item_to_buy = ""

        # Start fetching location and check for distance
        self.fetch_location_and_start()

    def set_alarm(self, instance):
        try:
            # Get target location and item
            location = self.location_input.text.split(",")
            self.target_location = (float(location[0]), float(location[1]))
            self.item_to_buy = self.item_input.text

            self.add_widget(Label(text=f"Reminder set for {self.item_to_buy} at {self.target_location}"))
        except ValueError:
            self.add_widget(Label(text="Invalid location. Use format: lat,lon"))

    def fetch_location_and_start(self):
        # Fetch user location using geocoder
        def location_fetching_thread():
            while True:
                location = geocoder.ip("me")
                if location.ok:
                    lat, lon = location.latlng
                    self.user_location = (lat, lon)
                    print(f"Fetched Location: Latitude: {lat}, Longitude: {lon}")
                else:
                    print("Unable to fetch location. Using default coordinates.")
                    self.user_location = (37.7749, -122.4194)  # Fallback to San Francisco

                # Check distance to target location
                self.check_distance()
                time.sleep(5)  # Update every 5 seconds

        # Start the location fetching thread
        threading.Thread(target=location_fetching_thread, daemon=True).start()

    def check_distance(self):
        if self.user_location and self.target_location:
            distance = geodesic(self.user_location, self.target_location).meters
            print(f"Distance to target: {distance} meters")
            if distance < 100:  # Alert if within 100 meters
                notification.notify(
                    title="Reminder Alert",
                    message=f"You're near the location. Don't forget to buy: {self.item_to_buy}!",
                )
                self.target_location = None  # Clear the alarm to prevent repeated alerts
                print("Alert triggered!")


class ReminderAppMain(App):
    def build(self):
        return ReminderApp()


if __name__ == "__main__":
    ReminderAppMain().run()
