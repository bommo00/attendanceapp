import flet as ft
import datetime


def main(page):
    employees = []
    class Employee:
        def __init__(self, name, department):
            self.name = name
            self.department = department
            self.status = '未出勤'
            self.record = []

        def punch_in(self, time):
            self.status = '出勤中'

        def punch_out(self, time):
            self.status = '未出勤'


    def handle_change(e):
        print(f"handle_change e.data: {e.data}")

    def handle_submit(e):
        print(f"handle_submit e.data: {e.data}")

    def handle_tap(e):
        print(f"handle_tap")


    new_employee = Employee('田中','営業')

    employees.append(new_employee)
    employee_list = []

    for employee in employees:
        employee_list.append(ft.Row([
            ft.Text(employee.name, size=30),
            ft.Text(employee.department, size=30),
            ft.Text(employee.status, size=25),
            ft.ElevatedButton('出退勤'),
        ],
            alignment=ft.MainAxisAlignment.CENTER
        ))

    page.title = "出退勤管理システム"
    page.vertical_alignment = ft.MainAxisAlignment.START
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
                    height=40,
                    options=[
                        ft.dropdown.Option("Red"),
                        ft.dropdown.Option("Green"),
                        ft.dropdown.Option("Blue"),
                    ],
                ),
                ft.ElevatedButton('すべて', bgcolor='BLUE_200', height=40),
                ft.ElevatedButton('未出勤', bgcolor='BLUE_200', height=40),
                ft.ElevatedButton('出勤中', bgcolor='BLUE_200', height=40),
                ft.ElevatedButton('残業中', bgcolor='BLUE_200', height=40),
                ft.SearchBar(
                    width=200,
                    height=40,
                    view_elevation=4,
                    divider_color=ft.colors.AMBER,
                    bar_hint_text="名前",
                    on_change=handle_change,
                    on_submit=handle_submit,
                    on_tap=handle_tap,
                ),
                ft.IconButton(icon=ft.icons.ADD)
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
