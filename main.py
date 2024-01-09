import datetime
from flask import Flask, render_template, request, redirect, url_for
import boto3
from boto3 import resource
from boto3.dynamodb.conditions import Attr
from apscheduler.schedulers.background import BackgroundScheduler
import time

dynamodb = boto3.resource('dynamodb')
table = resource('dynamodb').Table('for_task')

app = Flask(__name__)

def overtime():
    current_time = datetime.datetime.now()
    if current_time.hour >= 18 and current_time.weekday() < 5:
        response = table.scan(
            FilterExpression=Attr('type').eq('status') & Attr('status').eq('出勤中')
        )
        items = response['Items']
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
        time.sleep(60)

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(overtime, 'cron', hour=18, day_of_week='mon-fri')
scheduler.start()
@app.route('/')
def home():
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
    employee_id = request.args.get('id')
    response = table.scan(
        FilterExpression=Attr('type').eq('status') & Attr('id').eq(employee_id)
    )
    item = response['Items']
    if item:
        item = item[0]
        item['status'] = '未出勤' if item['status'] == "出勤中" or item['status'] == "残業中" else "出勤中"
        if datetime.datetime.now().weekday() > 5 and item['status'] == "出勤中":
            item['status'] = "残業中"
        if datetime.datetime.now().weekday() < 5 and datetime.datetime.now().hour > 18 and item['status'] == "出勤中":
            item['status'] = "残業中"
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
    app.run(debug=True)
