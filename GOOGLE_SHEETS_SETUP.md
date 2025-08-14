# Google Sheets API Setup Guide

## Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it (e.g., "Web Scraper")
4. Click "Create"

## Step 2: Enable Google Sheets API
1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"

## Step 3: Create Service Account Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in:
   - Service account name: `web-scraper-bot`
   - Service account ID: (auto-fills)
   - Description: "Bot for web scraper to write to sheets"
4. Click "Create and Continue"
5. For role, select "Editor" or "Owner"
6. Click "Continue" then "Done"

## Step 4: Get the JSON Key File
1. Click on your new service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON" format
5. Click "Create" - it will download a JSON file
6. **SAVE THIS FILE** as `google_sheets_credentials.json` in your web-scraper folder

## Step 5: Create a Google Sheet
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new sheet
3. Name it "Web Scraper Data"
4. Note the sheet ID from the URL:
   - URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
   - Copy the `SHEET_ID_HERE` part

## Step 6: Share Sheet with Service Account
1. In your Google Sheet, click "Share" button
2. Find the service account email in your JSON file (looks like: `web-scraper-bot@project-name.iam.gserviceaccount.com`)
3. Add this email with "Editor" permissions
4. Click "Send"

## What to Send Me:
1. Confirm you've completed these steps
2. Provide the Google Sheet ID
3. Confirm the credentials file is saved as `google_sheets_credentials.json`

That's it! The service account can now write to your sheet programmatically.