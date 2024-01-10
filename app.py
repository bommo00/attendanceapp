import datetime
import os
from flask import Flask, render_template, request, redirect, url_for
import boto3
from boto3 import resource
from boto3.dynamodb.conditions import Attr
from apscheduler.schedulers.background import BackgroundScheduler
import time

# Initiate the connection with database
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_default_region = os.getenv('AWS_DEFAULT_REGION')
dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          region_name=aws_default_region
                          )
table = resource('dynamodb').Table('for_task')

app = Flask(__name__)

# Check for the overtime working
def overtime():
    current_time = datetime.datetime.now()
    # Get all the employee still work
    if current_time.hour >= 18 and current_time.weekday() < 5:
        response = table.scan(
            FilterExpression=Attr('type').eq('status') & Attr('status').eq('出勤中')
        )
        items = response['Items']
        # Change the status
        if items:
            for item in items:
                table.update_item(
                    Key={
                        'name': item['name'],
                        'type': 'status',
                    },
                    UpdateExpression='set #st = :s',
                    ExpressionAttributeNames={
                        '#st': 'status'
                    },
                    ExpressionAttributeValues={
                        ':s': '残業中'
                    }
                )
        time.sleep(3600)
    else:
        # Check after 1 minute
        time.sleep(60)

# Control the overtime progress
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(overtime, 'cron', hour=18, day_of_week='mon-fri')
scheduler.start()
@app.route('/')
def home():
    # For filtering employees by status
    status = request.args.get('status', 'all')
    if status == 'all':
        response = table.scan(
            FilterExpression=Attr('type').eq('status')
        )
        items = response['Items']
    else:
        response = table.scan(
            FilterExpression=Attr('type').eq('status') & Attr('status').eq(status)
        )
        items = response['Items']
    return render_template("index.html", employees=items)


@app.route("/punch")
def punch():
    # Punch in or out for a certain employee
    employee_id = request.args.get('id')
    response = table.scan(
        FilterExpression=Attr('type').eq('status') & Attr('id').eq(employee_id)
    )
    item = response['Items']
    if item:
        item = item[0]
        item['status'] = '未出勤' if item['status'] == "出勤中" or item['status'] == "残業中" else "出勤中"
        # Overtime check
        if datetime.datetime.now().weekday() > 5 and item['status'] == "出勤中":
            item['status'] = "残業中"
        if datetime.datetime.now().weekday() < 5 and datetime.datetime.now().hour > 18 and item['status'] == "出勤中":
            item['status'] = "残業中"
        # Change the status in the database
        table.update_item(
            Key={
                'name': item['name'],
                'type': 'status',
            },
            UpdateExpression='set #st = :s',
            ExpressionAttributeNames={
                '#st': 'status'
            },
            ExpressionAttributeValues={
                ':s': item['status']}
        )
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run()
