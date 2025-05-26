# Flask_Contact_API
# Contact Identification Flask App

This is a simple Flask web application that manages contacts by linking related email addresses and phone numbers. It identifies primary and secondary contacts based on the input and stores them in a SQLite database.

## Features

- Add new contacts with email and/or phone number.
- Identify existing contacts linked by email or phone number.
- Maintain link precedence (primary and secondary contacts).
- REST API endpoint `/identify` for contact identification (accepts JSON).
- Simple HTML form to test contact submission via web browser.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Flask and dependencies (listed in requirements.txt)

### Installation

1. Clone the repository or download the code files.
2. (Optional) Create and activate a Python virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Run the app with `python app.py`.
5. Open a browser at `http://127.0.0.1:5000` to access the form.

### API Usage

Send a POST request to `/identify` with JSON data containing email and/or phoneNumber fields:

Example:
{
  "email": "user@example.com",
  "phoneNumber": "1234567890"
}

Response will include the primary contact id, linked emails and phone numbers, and secondary contact ids.

## Project Structure

- app.py          # Main Flask app code
- templates/      # HTML templates (form.html)
- contacts.db     # SQLite database file (auto-created)
- requirements.txt # Python dependencies
- README.md       # Project documentation

## License

This project is licensed under the MIT License.

