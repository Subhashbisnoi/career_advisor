# GitHub OAuth Setup Guide

This guide will walk you through setting up GitHub OAuth authentication for your interviewer application.

## Prerequisites

- A GitHub account
- Access to your application's repository
- Admin access to your deployed application (if applicable)

## Step 1: Create a GitHub OAuth App

1. **Navigate to GitHub Settings**
   - Go to [GitHub](https://github.com)
   - Click on your profile picture in the top right corner
   - Select "Settings" from the dropdown menu

2. **Access Developer Settings**
   - In the left sidebar, scroll down and click "Developer settings"
   - Click "OAuth Apps" in the left sidebar
   - Click "New OAuth App" button

3. **Configure OAuth App**
   Fill out the form with the following information:
   
   - **Application name**: `Interviewer App` (or your preferred name)
   - **Homepage URL**: 
     - For development: `http://localhost:3000`
     - For production: `https://yourdomain.com`
   - **Application description**: `AI-powered interviewer application with GitHub OAuth authentication`
   - **Authorization callback URL**: 
     - For development: `http://localhost:3000` (same as homepage)
     - For production: `https://yourdomain.com` (same as homepage)

4. **Register Application**
   - Click "Register application"
   - You'll be redirected to your app's settings page

5. **Get Client Credentials**
   - Copy the **Client ID** - you'll need this for both frontend and backend
   - Click "Generate a new client secret"
   - Copy the **Client Secret** - you'll need this for the backend only
   - ⚠️ **Important**: Store the client secret securely. You won't be able to see it again!

## Step 2: Configure Backend Environment

1. **Update Backend Environment File**
   - Navigate to your backend directory: `cd backend`
   - Copy the example environment file: `cp .env.example .env`
   - Edit the `.env` file and add your GitHub credentials:

   ```bash
   # GitHub OAuth Configuration
   GITHUB_CLIENT_ID=your_github_client_id_here
   GITHUB_CLIENT_SECRET=your_github_client_secret_here
   ```

   Replace `your_github_client_id_here` and `your_github_client_secret_here` with the values you copied from GitHub.

## Step 3: Configure Frontend Environment

1. **Update Frontend Environment File**
   - Navigate to your frontend directory: `cd frontend`
   - Copy the example environment file: `cp .env.example .env`
   - Edit the `.env` file and add your GitHub client ID:

   ```bash
   # GitHub OAuth Configuration
   REACT_APP_GITHUB_CLIENT_ID=your_github_client_id_here
   ```

   Replace `your_github_client_id_here` with the Client ID you copied from GitHub.

## Step 4: Test the Integration

1. **Start the Backend Server**
   ```bash
   cd backend
   python3 main.py
   ```

2. **Start the Frontend Server**
   ```bash
   cd frontend
   npm start
   ```

3. **Test GitHub OAuth**
   - Open your browser and navigate to `http://localhost:3000`
   - Click on "Sign In" or "Sign Up"
   - You should see a "Continue with GitHub" button
   - Click the button to test the GitHub OAuth flow

## Step 5: Production Deployment

When deploying to production:

1. **Update OAuth App Settings**
   - Go back to your GitHub OAuth App settings
   - Update the **Homepage URL** and **Authorization callback URL** to your production domain
   - Example: `https://yourapp.com`

2. **Update Environment Variables**
   - Make sure your production environment has the correct `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`
   - Update `REACT_APP_GITHUB_CLIENT_ID` in your frontend build environment

3. **Security Considerations**
   - Never commit your `.env` files to version control
   - Use environment variable management in your deployment platform
   - Regularly rotate your client secret if needed

## Troubleshooting

### Common Issues

1. **"GitHub OAuth not configured" message**
   - Check that `REACT_APP_GITHUB_CLIENT_ID` is set in your frontend `.env` file
   - Restart your frontend development server after adding environment variables

2. **"GitHub authentication failed" error**
   - Verify that your `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are correct
   - Check that your OAuth app's callback URL matches your application URL
   - Ensure your backend server is running and accessible

3. **"Application suspended" error**
   - Check your GitHub OAuth app status in GitHub Developer Settings
   - Ensure you haven't exceeded GitHub's rate limits

4. **Email not found error**
   - Make sure your GitHub account has a public email address
   - Or add the `user:email` scope to access private email addresses (already included in our implementation)

### Debug Steps

1. **Check Backend Logs**
   - Look for any error messages in your backend console
   - Verify that the GitHub API requests are successful

2. **Check Frontend Console**
   - Open browser developer tools and check for JavaScript errors
   - Verify that the OAuth flow is redirecting correctly

3. **Verify Environment Variables**
   - Backend: `echo $GITHUB_CLIENT_ID` and `echo $GITHUB_CLIENT_SECRET`
   - Frontend: Check browser developer tools > Application > Local Storage for environment variables

## Security Best Practices

1. **Environment Variables**
   - Never hardcode credentials in your source code
   - Use different OAuth apps for development and production
   - Store production secrets securely using your deployment platform's secret management

2. **Scope Permissions**
   - Our implementation only requests `user:email` scope
   - Only request the minimum permissions needed for your application

3. **Error Handling**
   - Don't expose sensitive error details to end users
   - Log security-related errors for monitoring

## Need Help?

If you encounter issues during setup:

1. Check the GitHub OAuth App settings match your application URLs
2. Verify all environment variables are set correctly
3. Ensure both backend and frontend servers are running
4. Check the browser developer console and backend logs for error messages

The implementation supports both Google and GitHub OAuth, so users can choose their preferred authentication method.
