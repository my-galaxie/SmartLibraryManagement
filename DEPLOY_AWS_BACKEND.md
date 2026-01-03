# AWS Backend Deployment Guide

This guide will help you deploy your FastAPI backend to AWS Lambda using the AWS SAM CLI.

## Prerequisites
1.  **AWS Account**: You need an active AWS account.
2.  **AWS CLI**: Installed and configured (`aws configure`).
3.  **AWS SAM CLI**: Installed.
4.  **Docker** (Optional but recommended for testing locally).

## Step 1: Prepare Environment
Ensure you are in the `backend` directory:
```bash
cd backend
```

## Step 2: Build the Application
Run the following command to bundle your dependencies:
```bash
sam build
```
*If this fails due to missing dependencies, ensure `requirements.txt` is up to date.*

## Step 3: Deploy
Run the guided deployment command:
```bash
sam deploy --guided
```

Fill in the prompts:
-   **Stack Name**: `smart-library` (Preserve default)
-   **AWS Region**: `ap-south-1` (Preserve default)
-   **Parameter SupabaseUrl**: [Your Supabase Project URL]
-   **Parameter SupabaseKey**: [Your Supabase Anon Key]
-   **Parameter SupabaseServiceKey**: [Your Supabase Service Role Key]
-   **Parameter FrontendUrl**: `https://your-vercel-app.vercel.app` (Or `*` for now)
-   **Confirm changes before deploy**: `y`
-   **Allow SAM CLI IAM role creation**: `y`
-   **Save arguments to configuration file**: `y`

## Step 4: Get API URL
Once deployment is complete, SAM will output an `ApiUrl`.
Example: `https://xyz123.execute-api.us-east-1.amazonaws.com/`

**Copy this URL** — you will need to add it to your Frontend environment variables.

## Troubleshooting
-   **500 Internal Server Error**: Check CloudWatch Logs in AWS Console.
-   **Timeout**: Increase timeout in `template.yaml` (currently 30s).
