import smtplib
from email.message import EmailMessage
import time

# Configuration
SMTP_HOST = '108.181.38.69'
SMTP_PORT = 25
FROM_EMAIL = 'no-reply@vietcgi.nguoivietcali.com'
RECIPIENTS = ['vietcgi@gmail.com', 'vietcgi@yahoo.com', 'vietcgi@outlook.com']

print(f"Connecting to {SMTP_HOST}:{SMTP_PORT}...")

for recipient in RECIPIENTS:
    msg = EmailMessage()
    msg['From'] = FROM_EMAIL
    msg['To'] = recipient
    msg['Subject'] = f'working or not 100% {int(time.time())}'
    msg.set_content(f'Testing delivery to {recipient} via KumoMTA.')
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, local_hostname='vietcgi.nguoivietcali.com', timeout=10) as s:
            s.set_debuglevel(1)  # Enable debug output
            s.ehlo()
            result = s.send_message(msg)
            print(f'✓ Sent to {recipient} - Server response: {result}')
    except Exception as e:
        print(f'✗ Failed to send to {recipient}: {e}')
    
    # Small delay between sends
    time.sleep(1)

print("\nDone.")
