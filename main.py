import datetime
import boto3
import flet as ft
from flet import *
from boto3 import resource
from boto3.dynamodb.conditions import Key, Attr
import threading

dynamodb = boto3.resource('dynamodb')
table = resource('dynamodb').Table('for_task')


def main(page):
    # To create every employee information with GUI for the further interaction
    class Employee_list(UserControl):
        def __init__(self, name, department, status):
            super().__init__()
            self.name = name
            self.department = department
            self.status = status
            # For the GUI interaction
            self.bar = ft.Text(self.status, size=30)
            # For the overtime checking
            self.time_check()
            thread = threading.Thread(target=self.time_check)
            thread.start()

        # Update the data to the database
        def status_change(self):
            response = table.scan(
                FilterExpression=Key('name').eq(self.name) & Attr('type').eq('status')
                                 & Attr('department').eq(self.department)
            )
            item = response['Items']
            if item:
                table.update_item(
                    Key={
                        'name': self.name,
                        'type': 'status',
                    },
                    UpdateExpression='set #st = :s',
                    ExpressionAttributeNames={
                        '#st': 'status'
                    },
                    ExpressionAttributeValues={
                        ':s': self.status}
                )

        def time_check(self):
            if datetime.datetime.now().hour > 18 and datetime.datetime.now().weekday() < 5:
                if self.status == "出勤中":
                    self.status = "残業中"
                    self.status_change()

        # Punch in and out; the interaction of GUI button
        def punch(self, e):
            self.bar.value = '未出勤' if self.bar.value == "出勤中" or self.bar.value == "残業中" else "出勤中"
            if datetime.datetime.now().weekday() > 5 and self.bar.value == "出勤中":
                self.bar.value = "残業中"
            self.status = self.bar.value
            self.status_change()
            self.update()

        # Build the list of employees
        def build(self):
            list = ft.Row([
                ft.Text(self.name, size=30),
                ft.Text(self.department, size=30),
                self.bar,
                ft.ElevatedButton('出退勤', on_click=self.punch),
            ],
                alignment=ft.MainAxisAlignment.CENTER
            )
            return list

    # Rebuild the list of employees
    def make_column(items, e):
        global employee_list
        employee_list = []
        if items:
            for item in items:
                employee_list.append(
                    Employee_list(item['name'], item['department'], item['status'])
                )
        page.controls.pop()
        page.add(ft.Column(employee_list,
                           alignment=ft.MainAxisAlignment.CENTER,
                           height=600,
                           scroll=ft.ScrollMode.ALWAYS,
                           ), )
        page.update()

    # Get data from database
    def get_list(e):
        if e.control.text == "すべて":
            response = table.scan(
                FilterExpression=Attr('type').eq('status')
            )
        else:
            response = table.scan(
                FilterExpression=Attr('type').eq('status') & Attr('status').eq(e.control.text)
            )
        items = response['Items']
        make_column(items, e)

    def classify(e):
        response = table.scan(
            FilterExpression=Attr('type').eq('status') & Attr('department').eq(e.control.value)
        )
        items = response['Items']
        make_column(items, e)

    def display_all(e):
        response = table.scan(
            FilterExpression=Attr('type').eq('status')
        )
        items = response['Items']
        make_column(items, e)

    def find_employee(e):
        response = table.scan(
            FilterExpression=Attr('type').eq('status') & Key('name').eq(e.data)
        )
        items = response['Items']
        make_column(items, e)

    # Initial the employee list
    employee_list = []
    response = table.scan(
        FilterExpression=Attr('type').eq('status')
    )
    items = response['Items']
    for item in items:
        employee_list.append(
            Employee_list(item['name'], item['department'], item['status'])
        )

    # Build the basic framework
    page.title = "出退勤管理システム"
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Get the values of all the departments
    response = table.scan()
    departments = []
    for item in response['Items']:
        if item['department'] not in departments:
            departments.append(item['department'])

    # Build the page with all elements
    page.add(
        ft.Row(
            [
                ft.Text("出退勤管理システム", size=20, weight=ft.FontWeight.W_100),
                ft.IconButton(ft.icons.PUNCH_CLOCK),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        ),
        ft.Row(
            [
                ft.Dropdown(
                    width=100,
                    height=60,
                    options=[ft.dropdown.Option(department) for department in departments],
                    on_change=classify,
                ),
                ft.ElevatedButton('すべて', bgcolor='BLUE_200', height=40, on_click=get_list),
                ft.ElevatedButton('未出勤', bgcolor='BLUE_200', height=40, on_click=get_list),
                ft.ElevatedButton('出勤中', bgcolor='BLUE_200', height=40, on_click=get_list),
                ft.ElevatedButton('残業中', bgcolor='BLUE_200', height=40, on_click=get_list),
                ft.TextField(
                    width=200,
                    height=40,
                    hint_text="名前",
                    on_change=find_employee,
                ),
                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=display_all)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Column(employee_list,
                  alignment=ft.MainAxisAlignment.CENTER,
                  height=600,
                  scroll=ft.ScrollMode.ALWAYS,
                  ),
    )
    page.update()


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
