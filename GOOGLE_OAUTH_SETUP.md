# Google OAuth Setup Instructions

This document explains how to set up Google OAuth for the AI Interviewer application.

## Prerequisites

1. A Google Cloud Platform (GCP) account
2. A Google Cloud project

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "Select a project" and then "New Project"
3. Give your project a name (e.g., "AI Interviewer")
4. Click "Create"

## Step 2: Enable the Google+ API

1. In the Google Cloud Console, navigate to "APIs & Services" > "Library"
2. Search for "Google+ API" and click on it
3. Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" for User Type
   - Fill in the required fields:
     - Application name: "AI Interviewer"
     - User support email: Your email
     - Developer contact information: Your email
   - Add scopes: `email`, `profile`, `openid`
   - Add test users if needed
4. For Application type, select "Web application"
5. Give it a name (e.g., "AI Interviewer Web Client")
6. Add Authorized JavaScript origins:
   - `http://localhost:3000` (for development)
   - Your production domain (if applicable)
7. Add Authorized redirect URIs:
   - `http://localhost:3000` (for development)
   - Your production domain (if applicable)
8. Click "Create"

## Step 4: Configure Environment Variables

1. Copy the Client ID from the credentials you just created
2. Update the environment files:

### Backend (.env)
```
GOOGLE_CLIENT_ID=your-google-client-id-here
```

### Frontend (.env)
```
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id-here
```

## Step 5: Test the Integration

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

3. Navigate to the login or signup page
4. You should see a "Continue with Google" button
5. Click it to test the Google OAuth flow

## Security Notes

- Never commit your Google Client ID to version control if it's sensitive
- In production, make sure to add your production domain to the authorized origins
- Consider implementing additional security measures like CSRF protection
- The Google Client ID for web applications is not considered secret, but still follow best practices

## Troubleshooting

### Common Issues

1. **"redirect_uri_mismatch" error**: Make sure your redirect URI in the Google Console matches your application URL
2. **"invalid_client" error**: Check that your Client ID is correct in both environment files
3. **Button not appearing**: Make sure the Google Identity Services script is loaded (check browser console for errors)

### Debug Tips

- Check the browser console for JavaScript errors
- Verify that environment variables are loaded correctly
- Test with different browsers
- Clear browser cache and cookies if needed
