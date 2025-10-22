#!/usr/bin/env python3
"""
District 5 Survey Bot - SMS Notification Service
Sends survey links to voters via SMS using Twilio
"""

import os
import sys
from datetime import datetime
from twilio.rest import Client
from typing import List, Dict
import json


class SurveyBot:
    """SMS bot for sending survey links to voters"""
    
    def __init__(self):
        """Initialize the Twilio client with credentials from environment variables"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.survey_url = os.getenv('SURVEY_URL', 'http://localhost:5000/survey.html')
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError(
                "Missing required environment variables: "
                "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER"
            )
        
        self.client = Client(self.account_sid, self.auth_token)
        self.sent_messages = []
    
    def format_phone_number(self, phone: str) -> str:
        """
        Format phone number to E.164 format
        
        Args:
            phone: Phone number in various formats
            
        Returns:
            Formatted phone number in E.164 format (+1XXXXXXXXXX)
        """
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        
        # Add country code if not present
        if len(digits) == 10:
            digits = '1' + digits
        
        return '+' + digits
    
    def create_message(self, name: str = None) -> str:
        """
        Create personalized survey invitation message
        
        Args:
            name: Optional voter name for personalization
            
        Returns:
            Formatted message string
        """
        greeting = f"Hello {name}!" if name else "Hello!"
        
        message = (
            f"{greeting}\n\n"
            f"You're invited to participate in the District 5 Voter Survey for "
            f"Hyde Park, Mattapan, and Readville.\n\n"
            f"Your voice matters! Share your thoughts on important community issues.\n\n"
            f"Complete the survey here: {self.survey_url}\n\n"
            f"Thank you for your participation!"
        )
        
        return message
    
    def send_sms(self, to_number: str, name: str = None) -> Dict:
        """
        Send SMS to a single phone number
        
        Args:
            to_number: Recipient phone number
            name: Optional recipient name for personalization
            
        Returns:
            Dictionary with send status and details
        """
        try:
            formatted_number = self.format_phone_number(to_number)
            message_body = self.create_message(name)
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=formatted_number
            )
            
            result = {
                'success': True,
                'to': formatted_number,
                'sid': message.sid,
                'status': message.status,
                'timestamp': datetime.now().isoformat(),
                'name': name
            }
            
            self.sent_messages.append(result)
            print(f"✓ SMS sent to {formatted_number} (SID: {message.sid})")
            
            return result
            
        except Exception as e:
            result = {
                'success': False,
                'to': to_number,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'name': name
            }
            
            self.sent_messages.append(result)
            print(f"✗ Failed to send SMS to {to_number}: {str(e)}")
            
            return result
    
    def send_bulk_sms(self, recipients: List[Dict]) -> Dict:
        """
        Send SMS to multiple recipients
        
        Args:
            recipients: List of dictionaries with 'phone' and optional 'name' keys
            
        Returns:
            Dictionary with summary of sent messages
        """
        print(f"\nSending survey invitations to {len(recipients)} recipients...\n")
        
        results = {
            'total': len(recipients),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for recipient in recipients:
            phone = recipient.get('phone')
            name = recipient.get('name')
            
            if not phone:
                print(f"✗ Skipping recipient: missing phone number")
                results['failed'] += 1
                continue
            
            result = self.send_sms(phone, name)
            results['details'].append(result)
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
        
        print(f"\n{'='*50}")
        print(f"Bulk SMS Send Summary:")
        print(f"Total: {results['total']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"{'='*50}\n")
        
        return results
    
    def save_log(self, filename: str = 'sms_log.json'):
        """
        Save sent messages log to a JSON file
        
        Args:
            filename: Output filename for the log
        """
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'messages': self.sent_messages
            }, f, indent=2)
        
        print(f"Log saved to {filename}")


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single SMS: python sms_bot.py <phone_number> [name]")
        print("  Bulk SMS:   python sms_bot.py --bulk <recipients_file.json>")
        print("\nRecipients file format:")
        print('  [{"phone": "1234567890", "name": "John Doe"}, ...]')
        sys.exit(1)
    
    try:
        bot = SurveyBot()
        
        if sys.argv[1] == '--bulk':
            if len(sys.argv) < 3:
                print("Error: Please provide recipients file")
                sys.exit(1)
            
            with open(sys.argv[2], 'r') as f:
                recipients = json.load(f)
            
            results = bot.send_bulk_sms(recipients)
            bot.save_log()
            
        else:
            phone = sys.argv[1]
            name = sys.argv[2] if len(sys.argv) > 2 else None
            
            result = bot.send_sms(phone, name)
            
            if result['success']:
                print("\nSMS sent successfully!")
            else:
                print("\nFailed to send SMS")
                sys.exit(1)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
