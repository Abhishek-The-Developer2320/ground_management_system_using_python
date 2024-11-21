from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
DATA_FILE = 'data.json'

# Utility functions for reading and writing to a JSON file
# app = Flask(__name__)
# app.secret_key = 'your_secret_key'

# DATA_FILE = 'data.json'

def read_json_file(file_path):
    """Read the JSON file and return the data."""
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json_file(file_path, data):
    """Write the data to the JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Home route


@app.route('/')
def home():
    return render_template('home.html')
@app.route('/about')
def about():
    return render_template('about.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        data = read_json_file(DATA_FILE)
        user = next((u for u in data["users"] if u["email"] == email and u["password"] == password), None)
        if user:
            session['user_id'] = user['user_id']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
            else:
                return redirect(url_for('user_dashboard'))  # Redirect to user dashboard
        else:
            flash("Invalid credentials. Please try again.")
    return render_template('login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        data = read_json_file(DATA_FILE)
        user = next((u for u in data["users"] if u["email"] == email and u["password"] == password), None)
        
        if user and user['role'] == 'admin':
            session['user_id'] = user['user_id']
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid admin credentials, try again.")
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin-signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        data = read_json_file(DATA_FILE)
        # Check if user already exists
        existing_user = next((u for u in data["users"] if u["email"] == email), None)
        if existing_user:
            flash("User already exists. Please log in.")
            return redirect(url_for('login'))
        
        # Add new user to the data with 'admin' role
        new_user_id = len(data["users"]) + 1  # Simple auto-increment logic
        new_user = {
            "user_id": new_user_id,
            "name": name,
            "email": email,
            "password": password,
            "role": 'admin'
        }
        data["users"].append(new_user)
        write_json_file(DATA_FILE, data)
        flash("Admin signup successful. You can now log in.")
        return redirect(url_for('admin_login'))  # Redirect to the login page
    
    return render_template('admin_signup.html')

# User signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = 'user'  # All new users will be assigned the 'user' role
        
        data = read_json_file(DATA_FILE)
        # Check if user already exists
        existing_user = next((u for u in data["users"] if u["email"] == email), None)
        if existing_user:
            flash("User already exists. Please log in.")
            return redirect(url_for('login'))
        
        # Add new user to the data
        new_user_id = len(data["users"]) + 1  # Simple auto-increment logic
        new_user = {
            "user_id": new_user_id,
            "name": name,
            "email": email,
            "password": password,
            "role": role
        }
        data["users"].append(new_user)
        write_json_file(DATA_FILE, data)
        flash("Signup successful. Please log in.")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# Admin dashboard route
# Admin dashboard route
def read_json_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        # Initialize the JSON structure if the file doesn't exist
        return {"users": [], "bookings": [], "events": []}

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Load data from the JSON file
    data = read_json_file(DATA_FILE)
    events = data.get("events", [])
    users = data.get("users", [])
    bookings = data.get("bookings", [])
    
    return render_template('admin_dashboard/index.html', events=events, users=users, bookings=bookings)

# Manage Events route
# @app.route('/manage-events', methods=['GET'])
# def manage_events():
#     data = read_json_file(DATA_FILE)
#     events = data.get('events', [])  # Fetch the events from the JSON data
#     return render_template('admin_dashboard/manage_events.html', events=events)



# User dashboard route
# @app.route('/user-dashboard')
# def user_dashboard():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     # Fetch user-specific data (e.g., bookings)
#     data = read_json_file(DATA_FILE)
#     bookings = [booking for booking in data.get('bookings', []) if booking['user_id'] == session['user_id']]
#     return render_template('user_dashboard/index.html', bookings=bookings)
@app.route('/user-dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    data = read_json_file(DATA_FILE)
    bookings = data.get('bookings', [])
    events = data.get('events', [])
    users = data.get('users', [])
    
    return render_template('user_dashboard/index.html', bookings=bookings, events=events, users=users, user_logged_in='user_id' in session)


# Event scheduling route (Admin only)
@app.route('/schedule-event', methods=['GET', 'POST'])
def schedule_event():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        ground = request.form['ground']
        
        data = read_json_file(DATA_FILE)
        new_event_id = len(data["events"]) + 1
        new_event = {
            "event_id": new_event_id,
            "event_name": event_name,
            "event_date": event_date,
            "ground": ground
        }
        data["events"].append(new_event)
        write_json_file(DATA_FILE, data)
        flash("Event scheduled successfully.")
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_dashboard/schedule_event.html')

# Ground booking route (User only)
# from datetime import datetime, timedelta
# from flask import flash, redirect, url_for, render_template, request, session

@app.route('/book-ground', methods=['GET', 'POST'])
def book_ground():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    data = read_json_file(DATA_FILE)
    bookings = data.get('bookings', [])
    events = data.get('events', [])
    grounds = ["Cricket", "Football", "Tennis", "Badminton Complex"]  # List of available grounds

    if request.method == 'POST':
        # Get booking details from the form
        ground = request.form['ground']
        date = request.form['date']
        time = request.form['time']
        duration = int(request.form['duration'])  # Convert duration to an integer

        # Convert the input date and time to a datetime object
        selected_start_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        selected_end_time = selected_start_time + timedelta(hours=duration)

        # Check for time overlap with existing bookings
        for booking in bookings:
            if booking['ground'] == ground and booking['date'] == date:
                existing_start_time = datetime.strptime(f"{booking['date']} {booking['time']}", "%Y-%m-%d %H:%M")
                existing_end_time = existing_start_time + timedelta(hours=int(booking['duration']))

                # If the selected time overlaps with any existing booking, return an error
                if is_time_overlap(selected_start_time, selected_end_time, existing_start_time, existing_end_time):
                    flash("Ground is already booked for this time.", "error")
                    return redirect(url_for('book_ground'))

        # Check if the ground is already reserved for an event at the given date
        for event in events:
            if event['ground'] == ground and event['event_date'] == date:
                flash("Ground is unavailable due to an event on this date.", "error")
                return redirect(url_for('book_ground'))

        # If the ground is available, proceed to book it
        new_booking = {
            "booking_id": len(bookings) + 1,
            "user_id": session['user_id'],
            "ground": ground,
            "date": date,
            "time": time,
            "duration": duration
        }
        bookings.append(new_booking)

        # Save the new booking to the JSON file
        data['bookings'] = bookings
        write_json_file(DATA_FILE, data)

        flash("Ground booked successfully!", "success")
        return redirect(url_for('user_dashboard'))  # Redirect to user dashboard or booking confirmation page

    return render_template('user_dashboard/book_ground.html', grounds=grounds)


def is_time_overlap(start1, end1, start2, end2):
    """
    Check if two time ranges overlap.
    """
    return start1 < end2 and end1 > start2  # If the start of on

@app.route('/manage-bookings', methods=['GET'])
def manage_bookings():
    # Read the data from the JSON file
    data = read_json_file(DATA_FILE)
    bookings = data.get('bookings', [])  # Fetch the bookings from the JSON data
    return render_template('admin_dashboard/manage_bookings.html', bookings=bookings)

EVENTS_FILE = 'events.json'

def load_events():
    """Load events from the JSON file."""
    try:
        with open(EVENTS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Return an empty structure if the file doesn't exist
        return {"events": []}

def save_events(data):
    """Save events to the JSON file."""
    with open(EVENTS_FILE, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/manage-events', methods=['GET', 'POST'])
def manage_events():
    # Load events from data.json file
    data = read_json_file(DATA_FILE)
    events = data.get("events", [])

    if request.method == 'POST':
        # Get form data
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        ground = request.form['ground']

        # Generate a unique event ID (simple approach)
        new_event_id = len(events) + 1

        # Add new event
        new_event = {
            "event_id": new_event_id,
            "event_name": event_name,
            "event_date": event_date,
            "ground": ground
        }
        data["events"].append(new_event)

        # Save the updated events to data.json
        write_json_file(DATA_FILE, data)

        flash("Event added successfully!", "success")
        return redirect(url_for('manage_events'))

    # Render the manage events page with current events
    return render_template('admin_dashboard/manage_events.html', events=events)




@app.route('/cancel-booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    # Read the data from the JSON file
    data = read_json_file(DATA_FILE)
    bookings = data.get('bookings', [])

    # Find and remove the booking with the given booking_id
    updated_bookings = [booking for booking in bookings if booking['booking_id'] != booking_id]

    if len(updated_bookings) < len(bookings):
        # Save the updated bookings back to the JSON file
        data['bookings'] = updated_bookings
        write_json_file(DATA_FILE, data)
        flash("Booking has been successfully cancelled.", "success")
    else:
        flash("Booking not found.", "error")

    return redirect(url_for('admin_dashboard'))
# @app.route('/add-event', methods=['POST'])
# def add_event():
#     # Read the data from the JSON file
#     data = read_json_file(DATA_FILE)
#     events = data.get('events', [])

#     # Get event details from the form
#     event_name = request.form['event_name']
#     event_date = request.form['event_date']
#     ground = request.form['ground']

#     # Generate a new event ID (simple approach, may need improvement for production)
#     event_id = len(events) + 1

#     # Create the new event
#     new_event = {
#         'event_id': event_id,
#         'event_name': event_name,
#         'event_date': event_date,
#         'ground': ground
#     }

#     # Add the new event to the list of events
#     events.append(new_event)

#     # Save the updated data back to the JSON file
#     data['events'] = events
#     write_json_file(DATA_FILE, data)

#     # Flash a success message and redirect to the manage events page
#     flash("Event added successfully!", "success")
#     return redirect(url_for('admin_dashboard/manage_bookings'))  # Redirect 

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('home'))  # Redirect to the home page or a specific page after logout


if __name__ == "__main__":
    app.run(debug=True)
