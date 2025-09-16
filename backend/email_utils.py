import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)

def send_otp_email(recipient_email: str, otp_code: str, recipient_name: Optional[str] = None) -> bool:
    """
    Send OTP email to the recipient
    
    Args:
        recipient_email: Email address to send OTP
        otp_code: 6-digit OTP code
        recipient_name: Optional recipient name
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # For development, if email credentials are not configured, just log the OTP
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print(f"[DEVELOPMENT MODE] OTP for {recipient_email}: {otp_code}")
        print(f"[DEVELOPMENT MODE] Recipient: {recipient_name or 'User'}")
        return True  # Return True to allow testing without email setup
        return False
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Reset OTP - Interviewer App"
        message["From"] = EMAIL_FROM
        message["To"] = recipient_email
        
        # Create the HTML content
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center;">
              <h1 style="color: #2563eb; margin-bottom: 20px;">Password Reset Request</h1>
              
              <p style="font-size: 16px; color: #374151; margin-bottom: 30px;">
                {"Hello " + recipient_name + "," if recipient_name else "Hello,"}
              </p>
              
              <p style="font-size: 16px; color: #374151; margin-bottom: 30px;">
                We received a request to reset your password for your Interviewer App account.
                Use the OTP code below to reset your password:
              </p>
              
              <div style="background-color: #fff; padding: 20px; border-radius: 8px; margin: 30px 0; border: 2px dashed #2563eb;">
                <h2 style="color: #2563eb; font-size: 32px; letter-spacing: 5px; margin: 0;">
                  {otp_code}
                </h2>
              </div>
              
              <p style="font-size: 14px; color: #6b7280; margin-bottom: 20px;">
                This OTP will expire in 10 minutes for security reasons.
              </p>
              
              <p style="font-size: 14px; color: #6b7280; margin-bottom: 20px;">
                If you didn't request this password reset, please ignore this email.
                Your account is still secure.
              </p>
              
              <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                <p style="font-size: 12px; color: #9ca3af;">
                  This is an automated email from Interviewer App. Please do not reply to this email.
                </p>
              </div>
            </div>
          </body>
        </html>
        """
        
        # Create plain text version
        text_content = f"""
        Password Reset Request
        
        {"Hello " + recipient_name + "," if recipient_name else "Hello,"}
        
        We received a request to reset your password for your Interviewer App account.
        Use the OTP code below to reset your password:
        
        OTP Code: {otp_code}
        
        This OTP will expire in 10 minutes for security reasons.
        
        If you didn't request this password reset, please ignore this email.
        Your account is still secure.
        
        ---
        This is an automated email from Interviewer App. Please do not reply to this email.
        """
        
        # Attach parts
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        
        message.attach(text_part)
        message.attach(html_part)
        
        # Create secure connection and send email
        context = ssl.create_default_context()
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            
            # Send email
            text = message.as_string()
            server.sendmail(EMAIL_FROM, recipient_email, text)
            
        print(f"OTP email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send OTP email to {recipient_email}: {str(e)}")
        return False

def send_password_reset_confirmation_email(recipient_email: str, recipient_name: Optional[str] = None) -> bool:
    """
    Send password reset confirmation email
    
    Args:
        recipient_email: Email address
        recipient_name: Optional recipient name
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print(f"[DEVELOPMENT MODE] Password reset confirmation sent to {recipient_email}")
        print(f"[DEVELOPMENT MODE] Recipient: {recipient_name or 'User'}")
        return True  # Return True to allow testing without email setup
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Reset Successful - Interviewer App"
        message["From"] = EMAIL_FROM
        message["To"] = recipient_email
        
        # Create the HTML content
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f0f9ff; padding: 30px; border-radius: 10px; text-align: center;">
              <h1 style="color: #059669; margin-bottom: 20px;">Password Reset Successful</h1>
              
              <p style="font-size: 16px; color: #374151; margin-bottom: 30px;">
                {"Hello " + recipient_name + "," if recipient_name else "Hello,"}
              </p>
              
              <p style="font-size: 16px; color: #374151; margin-bottom: 30px;">
                Your password has been successfully reset for your Interviewer App account.
              </p>
              
              <div style="background-color: #dcfce7; padding: 20px; border-radius: 8px; margin: 30px 0; border-left: 4px solid #059669;">
                <p style="color: #065f46; margin: 0; font-weight: 500;">
                  ✓ Your account is now secure with the new password
                </p>
              </div>
              
              <p style="font-size: 14px; color: #6b7280; margin-bottom: 20px;">
                If you didn't make this change, please contact our support team immediately.
              </p>
              
              <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                <p style="font-size: 12px; color: #9ca3af;">
                  This is an automated email from Interviewer App. Please do not reply to this email.
                </p>
              </div>
            </div>
          </body>
        </html>
        """
        
        # Create plain text version
        text_content = f"""
        Password Reset Successful
        
        {"Hello " + recipient_name + "," if recipient_name else "Hello,"}
        
        Your password has been successfully reset for your Interviewer App account.
        
        Your account is now secure with the new password.
        
        If you didn't make this change, please contact our support team immediately.
        
        ---
        This is an automated email from Interviewer App. Please do not reply to this email.
        """
        
        # Attach parts
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        
        message.attach(text_part)
        message.attach(html_part)
        
        # Create secure connection and send email
        context = ssl.create_default_context()
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            
            # Send email
            text = message.as_string()
            server.sendmail(EMAIL_FROM, recipient_email, text)
            
        print(f"Password reset confirmation email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send confirmation email to {recipient_email}: {str(e)}")
        return False
