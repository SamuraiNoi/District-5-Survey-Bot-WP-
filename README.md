# District 5 Survey Bot

This informative survey increases voter engagement and authenticity for District 5 voters in Hyde Park, Mattapan, Readville especially!

## Features

- 📱 **SMS Bot**: Automatically send survey links to voters via SMS/text messages
- 📋 **Survey Form**: Beautiful, responsive HTML survey form with categorical data collection
- 💾 **Data Storage**: Store responses in SQLite database with JSON backup
- 📊 **Analytics**: View statistics and export data to CSV
- 🔒 **Validation**: Client-side and server-side validation for data integrity

## Project Structure

```
District-5-Survey-Bot-WP-/
├── survey.html              # Survey form (HTML/CSS/JavaScript)
├── app.py                   # Flask backend server
├── sms_bot.py              # SMS bot for sending survey links
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── recipients_example.json  # Example recipients file for bulk SMS
└── data/                   # Directory for database and exports (auto-created)
    ├── survey_responses.db # SQLite database
    ├── responses.json      # JSON backup of responses
    └── responses_export_*.csv # CSV exports
```

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- A Twilio account (for SMS functionality)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SamuraiNoi/District-5-Survey-Bot-WP-.git
   cd District-5-Survey-Bot-WP-
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Twilio credentials:
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
   - `TWILIO_PHONE_NUMBER`: Your Twilio phone number (in E.164 format, e.g., +11234567890)
   - `SURVEY_URL`: Your survey URL (update after deployment)

4. **Get Twilio credentials**
   - Sign up at [https://www.twilio.com/](https://www.twilio.com/)
   - Get a phone number from the Twilio Console
   - Find your Account SID and Auth Token in the Console

## Usage

### Running the Survey Server

Start the Flask backend server:

```bash
python app.py
```

The server will start on `http://localhost:5000`

Access the survey at: `http://localhost:5000/survey.html`

### Sending SMS Invitations

#### Send Single SMS

```bash
python sms_bot.py <phone_number> [name]
```

Example:
```bash
python sms_bot.py 1234567890 "John Doe"
```

#### Send Bulk SMS

1. Create a recipients file (JSON format):
   ```json
   [
     {"phone": "1234567890", "name": "John Doe"},
     {"phone": "0987654321", "name": "Jane Smith"}
   ]
   ```

2. Run the bulk SMS command:
   ```bash
   python sms_bot.py --bulk recipients.json
   ```

The bot will send personalized SMS messages to all recipients with the survey link.

### API Endpoints

The backend provides several API endpoints:

- `POST /api/submit-survey` - Submit a survey response
- `GET /api/responses` - Get all survey responses
- `GET /api/stats` - Get survey statistics
- `GET /api/export-csv` - Export responses to CSV

### Viewing Survey Data

#### Get Statistics

```bash
curl http://localhost:5000/api/stats
```

#### Get All Responses

```bash
curl http://localhost:5000/api/responses
```

#### Export to CSV

```bash
curl http://localhost:5000/api/export-csv
```

## Survey Questions

The survey collects the following categorical data:

1. **Contact Information**
   - Phone Number (required)
   - Full Name (required)
   - Email Address (optional)

2. **Demographics**
   - Neighborhood: Hyde Park, Mattapan, Readville, Other
   - Age Group: 18-24, 25-34, 35-44, 45-54, 55-64, 65+

3. **Voting Information**
   - Voting Frequency: Every Election, Most Elections, Some Elections, Rarely, Never
   - Important Issues: Education, Healthcare, Housing, Transportation, Public Safety, Economic Development, Environment
   - Engagement Level: Very Engaged, Somewhat Engaged, Neutral, Not Very Engaged, Not Engaged At All

4. **Additional Comments** (optional text field)

## Data Storage

Survey responses are stored in two formats:

1. **SQLite Database** (`data/survey_responses.db`): Primary storage with structured data
2. **JSON Backup** (`data/responses.json`): Backup copy in JSON format

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- The `.env` file is included in `.gitignore` by default
- Use environment variables for all sensitive credentials
- Consider implementing authentication for the API endpoints in production
- Use HTTPS in production to protect data in transit

## Deployment

### Deploy to Heroku

1. Install Heroku CLI
2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```

3. Set environment variables:
   ```bash
   heroku config:set TWILIO_ACCOUNT_SID=your_sid
   heroku config:set TWILIO_AUTH_TOKEN=your_token
   heroku config:set TWILIO_PHONE_NUMBER=+11234567890
   heroku config:set SURVEY_URL=https://your-app-name.herokuapp.com/survey.html
   ```

4. Deploy:
   ```bash
   git push heroku main
   ```

### Deploy to Other Platforms

The application is a standard Flask app and can be deployed to:
- AWS (Elastic Beanstalk, EC2)
- Google Cloud Platform (App Engine, Cloud Run)
- DigitalOcean
- Any VPS with Python support

## Development

### Running in Development Mode

The Flask server runs in debug mode by default when started with `python app.py`.

### Testing the SMS Bot (Without Sending)

You can test the SMS bot logic by modifying the code to use a test mode or by using Twilio's test credentials.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available for use by District 5 voter engagement initiatives.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

Created to increase voter engagement and authenticity for District 5 voters in Hyde Park, Mattapan, and Readville.
