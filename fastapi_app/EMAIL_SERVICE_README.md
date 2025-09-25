# Email Service Documentation

## Overview

The email service has been updated to use Gmail SMTP with a simplified single endpoint that accepts HTML content with inline CSS and sends rendered emails to multiple recipients.

## Configuration

The email service uses the following environment variables (add these to your `.env` file):

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_SECURE=false
EMAIL_USER=${EMAIL_USER}
EMAIL_PASS=${EMAIL_PASS}
EMAIL_FROM=${EMAIL_FROM}
```

## API Endpoints

### Send Email

**POST** `/emails/send`

Sends emails to multiple recipients with HTML content that gets rendered in email clients. Supports per-recipient templating and optional attachments. Automatically saves a summary to the database.

#### Request Body

```json
{
  "subject": "Hello {{user[0]}} 🚀 Check out {{product[0]}}",
  "emails": ["user1@example.com", "user2@example.com"],
  "body": "<!DOCTYPE html><html><body><h1>Hello {{user[0]}}</h1><p>About {{product[0]}}</p></body></html>",
  "bcc": ["admin@example.com"],
  "custom": {
    "user": ["Vaibhav", "Pratyush"],
    "product": ["Next.js SaaS", "AI Health Monitor"]
  },
  "attachments": [
    {"filename": "hello.txt", "mime_type": "text/plain", "content_base64": "SGVsbG8sIFdvcmxkIQ=="}
  ]
}
```

#### Request Fields

- `subject` (string, required): Email subject line
- `emails` (array of strings, required): List of recipient email addresses
- `body` (string, required): HTML body content with inline CSS (will be rendered in email clients)
- `bcc` (array of strings, optional): List of BCC email addresses
- `custom` (object, optional): Placeholders like `{{key[index]}}` are replaced per recipient index: `[0]` → first email, `[1]` → second, etc. Missing keys/indices stay unchanged.
- `attachments` (array, optional): Items `{ filename, content_base64, mime_type }`. `content_base64` must be base64 of file bytes.

#### Response

```json
{
  "success": true,
  "sent_count": 2,
  "failed_count": 0,
  "total_recipients": 2,
  "errors": null,
  "message": "Email sent successfully to 2 out of 2 recipients"
}
```

### Get Email Summaries

**GET** `/emails/summaries?limit=50&skip=0`

Retrieves email summaries with pagination. Each summary represents one email send operation with deduplicated recipients.

#### Query Parameters

- `limit` (integer, optional): Maximum number of summaries to return (1-100, default 50)
- `skip` (integer, optional): Number of summaries to skip for pagination (default 0)

#### Response

```json
[
  {
    "id": "summary_id",
    "subject": "Your email subject",
    "recipients": ["recipient1@example.com", "recipient2@example.com"],
    "bcc_recipients": ["admin@example.com"],
    "body_preview": "Your HTML content with inline CSS...",
    "sent_at": "2025-09-07T10:30:00Z",
    "success": true,
    "sent_count": 2,
    "failed_count": 0,
    "errors": null
  }
]
```

### Get Email Statistics

**GET** `/emails/summaries/stats`

Get overall email statistics and performance metrics.

#### Response

```json
{
  "status": "success",
  "data": {
    "total_emails": 150,
    "successful_emails": 145,
    "failed_emails": 5,
    "recent_emails_24h": 12,
    "success_rate": 96.7
  }
}
```

## Email Summary Feature

The email service automatically saves a summary of every email sent to the database. This provides:

### Key Features

1. **Automatic Tracking**: Every email send operation is logged automatically
2. **Duplicate Prevention**: If an email is sent to multiple recipients, only one summary is created with all unique recipients
3. **Body Preview**: HTML content is stripped and truncated to create a readable preview
4. **Statistics**: Track success rates, recent activity, and overall performance
5. **Pagination**: View summaries with pagination support

### Summary Data Structure

Each email summary contains:
- **Subject**: The email subject line
- **Recipients**: Array of unique recipient email addresses
- **BCC Recipients**: Array of unique BCC email addresses (if any)
- **Body Preview**: First 200 characters of email content (HTML stripped)
- **Sent At**: Timestamp when the email was sent
- **Success**: Whether the email was sent successfully
- **Sent Count**: Number of emails successfully delivered
- **Failed Count**: Number of emails that failed
- **Errors**: Array of error messages (if any failures occurred)

### Usage Examples

#### Send Email with Multiple Recipients

```python
# This will create ONE summary with multiple recipients
email_data = {
    "subject": "Team Meeting",
    "emails": ["user1@example.com", "user2@example.com", "user1@example.com"],  # user1 appears twice
    "body": "<h1>Meeting Tomorrow</h1><p>Don't forget our team meeting!</p>",
    "bcc": ["manager@example.com"]
}

# Result: Summary will contain:
# - recipients: ["user1@example.com", "user2@example.com"] (deduplicated)
# - bcc_recipients: ["manager@example.com"]
```

#### View Email Summaries

```python
# Get latest 20 summaries
response = requests.get("http://localhost:8000/emails/summaries?limit=20&skip=0")
ummaries = response.json()

for summary in summaries:
    print(f"Subject: {summary['subject']}")
    print(f"Recipients: {summary['recipients']}")
    print(f"Success: {summary['success']}")
```

#### Get Email Statistics

```python
response = requests.get("http://localhost:8000/emails/summaries/stats")
stats = response.json()['data']

print(f"Success Rate: {stats['success_rate']:.1f}%")
print(f"Total Emails: {stats['total_emails']}")
```

### Basic Email

```bash
curl -X POST "http://localhost:8000/emails/send" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Welcome to ECELL KIET",
    "emails": ["user@example.com"],
    "body": "<h1 style=\"color: #667eea;\">Welcome!</h1><p style=\"font-family: Arial, sans-serif;\">Thank you for joining us.</p>"
  }'
```

### Email with Multiple Recipients and BCC

```bash
curl -X POST "http://localhost:8000/emails/send" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Important Announcement",
    "emails": ["user1@example.com", "user2@example.com"],
    "body": "<div style=\"background: #f8f9fa; padding: 20px;\"><h2>Announcement</h2><p>Your announcement content here.</p></div>",
    "bcc": ["admin@example.com"]
  }'
```

### Python Example

```python
import requests

email_data = {
    "subject": "Test Email",
    "emails": ["recipient@example.com"],
    "body": """
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; 
                    border-radius: 10px; 
                    color: white; 
                    text-align: center;">
            <h1>ECELL KIET</h1>
            <p>Your content here</p>
        </div>
    </body>
    </html>
    """,
    "bcc": ["admin@example.com"]
}

response = requests.post(
    "http://localhost:8000/emails/send",
    json=email_data
)

print(response.json())
```

## HTML Email Best Practices

1. **Use Inline CSS**: Email clients have limited CSS support, so use inline styles
2. **Table-based Layout**: Use tables for complex layouts as email clients don't fully support modern CSS
3. **Test Rendering**: Test your emails in different email clients
4. **Keep it Simple**: Avoid complex CSS features and JavaScript
5. **Responsive Design**: Use media queries for mobile compatibility

### Example HTML Template

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white; text-align: center; margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 28px;">ECELL KIET</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Entrepreneurship Cell</p>
    </div>
    
    <div style="background: #f8f9fa; padding: 30px; border-radius: 10px;">
        <h2 style="color: #2c3e50; margin-top: 0;">Your Title</h2>
        <p>Your content here...</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://example.com" 
               style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                Call to Action
            </a>
        </div>
    </div>
    
    <div style="text-align: center; padding: 20px; border-top: 2px solid #eee; color: #666;">
        <p style="margin: 0; font-size: 14px;">
            Best regards,<br>
            <strong>ECELL KIET Team</strong>
        </p>
    </div>
</body>
</html>
```

## Error Handling

The API provides detailed error information:

- **400 Bad Request**: Missing required fields or invalid email addresses
- **500 Internal Server Error**: SMTP connection issues or server errors

Common error scenarios:
- Invalid email addresses in the `emails` or `bcc` fields
- SMTP authentication failures
- Network connectivity issues
- Gmail security restrictions (use App Passwords for Gmail accounts)

## Security Notes

1. **App Passwords**: For Gmail accounts with 2FA enabled, use App Passwords instead of regular passwords
2. **Environment Variables**: Store email credentials in environment variables, never in code
3. **Rate Limiting**: Gmail has sending limits, implement rate limiting if sending large volumes
4. **Validation**: Always validate email addresses before sending

## Testing

Use the provided `test_email_api.py` script to test the email service:

```bash
python test_email_api.py
```

Make sure to:
1. Update the test email addresses in the script
2. Ensure the FastAPI server is running
3. Configure the correct environment variables


Example Email Payload

{
  "subject": "Welcome {{user[0]}} 🎉",
  "emails": [
    "vaibhavgupta.v890@gmail.com","pratyushmehra2005@gmail.com"
  ],
  "body": "<!DOCTYPE html><html><head><style>body { font-family: Arial, sans-serif; color: #333; } .container { padding: 20px; border: 1px solid #ddd; border-radius: 10px; } h1 { color: #4CAF50; }</style></head><body><div class='container'><h1>Hello {{user[0]}} 👋</h1><p>We’re thrilled to have you, {{user[1]}}, join our {{team[0]}}!</p><p>You’ll be working on <b>{{project[0]}}</b> next.</p><p style='color: #555;'>Stay awesome 🚀</p></div></body></html>",
  "bcc": [
    "pratyushmehra2005@gmail.com"
  ],
  "custom": {
    "user": ["Vaibhav", "Pratyush"],
    "team": ["Developers", "Designers"],
    "project": ["AI Health Monitor", "Next.js SaaS"]
  },
  "attachments": [
    {
      "filename": "welcome-guide.pdf",
      "content": "JVBERi0xLjUKJYGBgYEKMSAwIG9iago8PC9UeXBlIC9DYXRhbG9nPj4KZW5kb2Jq...",
      "encoding": "base64",
      "contentType": "application/pdf"
    },
    {
      "filename": "logo.png",
      "content": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
      "encoding": "base64",
      "contentType": "image/png"
    }
  ]
}
