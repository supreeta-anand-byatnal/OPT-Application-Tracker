import boto3
import json
import requests

def lambda_handler(event, context):
    # Initialize SNS client
    sns_client = boto3.client('sns', region_name='us-east-1')
    topic_arn = "arn:aws:sns:us-east-1:905418461469:OPT_Application_Tracker"
    
    # Get the case number
    case_number = "IOE9824747221"
    
    # Get authorization token
    auth_url = "https://egov.uscis.gov/csol-api/ui-auth"
    auth_headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,fr;q=0.8",
        "content-type": "application/json"
    }
    auth_response = requests.get(auth_url, headers=auth_headers)
    auth_token = auth_response.json()['JwtResponse']['accessToken']
    
    # Get case status
    status_url = f"https://egov.uscis.gov/csol-api/case-statuses/{case_number}"
    status_headers = {
        "accept": "*/*",
        "authorization": f"Bearer {auth_token}",
        "content-type": "application/json"
    }
    status_response = requests.get(status_url, headers=status_headers)
    case_status = status_response.json()
    
    # Extract status information
    status_text = case_status['CaseStatusResponse']['detailsEng']['actionCodeText']
    status_desc = case_status['CaseStatusResponse']['detailsEng']['actionCodeDesc']
    
    # Send email via SNS
    message = f"Status: {status_text}\nDescription: {status_desc}"
    sns_client.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject="USCIS Case Status Update"
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Status fetched and email sent successfully')
    }
