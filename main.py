from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
import sys
import os
import datetime
from PyQt5.QtGui import QIcon
import sqlite3
import matplotlib.pyplot as plt

class ExpenseTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Expense Tracker")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 18px;
                margin: 10px 2px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 10px;
                margin: 10px 0;
                font-size: 18px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTableWidget {
                font-size: 18px;
                selection-background-color: #d0d0d0;
            }
        """)

        self.main_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.total = 0.0

        self.initUI()
        self.initDB()

    def initUI(self):
        # Title
        title = QLabel("Expense Tracker")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        self.main_layout.addWidget(title)

        # Add expense button
        add_expense_button = QPushButton("Add Expense")
        add_expense_button.clicked.connect(self.show_add_expense_window)
        self.main_layout.addWidget(add_expense_button)

        # Filter/Search
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search by Category or Date (YYYY-MM-DD)")
        self.filter_input.textChanged.connect(self.filter_expenses)
        filter_layout.addWidget(self.filter_input)

        clear_filter_button = QPushButton("Clear Filter")
        clear_filter_button.clicked.connect(self.clear_filter)
        filter_layout.addWidget(clear_filter_button)
        self.main_layout.addLayout(filter_layout)

        # Expense table
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(5)
        self.expense_table.setHorizontalHeaderLabels(["Date", "Item", "Amount", "Category", "Actions"])
        self.expense_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.expense_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.expense_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.main_layout.addWidget(self.expense_table)

        # Total expense
        self.total_expense = QLabel("Total Expense: $0.00")
        self.total_expense.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        self.main_layout.addWidget(self.total_expense)

        # Graph button
        graph_button = QPushButton("Show Expense Graph")
        graph_button.clicked.connect(self.show_graph)
        self.main_layout.addWidget(graph_button)

        # Add expense window
        self.add_expense_window = QMainWindow()
        self.add_expense_window.setWindowTitle("Add Expense")
        self.add_expense_window.setGeometry(200, 200, 400, 300)

        add_expense_layout = QVBoxLayout()
        add_expense_window_widget = QWidget()
        add_expense_window_widget.setLayout(add_expense_layout)
        self.add_expense_window.setCentralWidget(add_expense_window_widget)

        # Date
        date_label = QLabel("Date")
        date_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        add_expense_layout.addWidget(date_label)

        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        self.date_input.setStyleSheet("font-size: 18px; padding: 10px; margin: 10px;")
        add_expense_layout.addWidget(self.date_input)

        # Item
        item_label = QLabel("Item")
        item_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        add_expense_layout.addWidget(item_label)

        self.item_input = QLineEdit()
        self.item_input.setStyleSheet("font-size: 18px; padding: 10px; margin: 10px;")
        add_expense_layout.addWidget(self.item_input)

        # Amount
        amount_label = QLabel("Amount")
        amount_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        add_expense_layout.addWidget(amount_label)

        self.amount_input = QLineEdit()
        self.amount_input.setStyleSheet("font-size: 18px; padding: 10px; margin: 10px;")
        add_expense_layout.addWidget(self.amount_input)

        # Category
        category_label = QLabel("Category")
        category_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        add_expense_layout.addWidget(category_label)

        self.category_input = QLineEdit()
        self.category_input.setStyleSheet("font-size: 18px; padding: 10px; margin: 10px;")
        add_expense_layout.addWidget(self.category_input)

        # Add expense button
        add_expense_btn = QPushButton("Add Expense")
        add_expense_btn.clicked.connect(self.add_expense_function)
        add_expense_layout.addWidget(add_expense_btn)

    def initDB(self):
        self.conn = sqlite3.connect('expenses.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                date TEXT,
                item TEXT,
                amount REAL,
                category TEXT
            )
        """)
        self.conn.commit()
        self.load_expenses()

    def load_expenses(self):
        self.expense_table.setRowCount(0)
        self.total = 0.0
        self.cursor.execute("SELECT * FROM expenses")
        for row_data in self.cursor.fetchall():
            row_position = self.expense_table.rowCount()
            self.expense_table.insertRow(row_position)
            for column, data in enumerate(row_data[1:]):  # Skip the ID
                self.expense_table.setItem(row_position, column, QTableWidgetItem(str(data)))
                if column == 2:  # Amount column
                    self.total += float(data)
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("background-color: #f44336; color: white; border: none; padding: 5px 10px; font-size: 16px;")
            delete_button.clicked.connect(lambda ch, id=row_data[0], row=row_position: self.delete_expense(id, row))
            self.expense_table.setCellWidget(row_position, 4, delete_button)
        self.total_expense.setText(f"Total Expense: ${self.total:.2f}")

    def show_add_expense_window(self):
        self.add_expense_window.show()

    def add_expense_function(self):
        date = self.date_input.text()
        item = self.item_input.text()
        amount = self.amount_input.text()
        category = self.category_input.text()

        if not date or not item or not amount or not category:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount must be a number.")
            return

        self.cursor.execute("INSERT INTO expenses (date, item, amount, category) VALUES (?, ?, ?, ?)", (date, item, amount, category))
        self.conn.commit()
        self.load_expenses()
        self.add_expense_window.hide()
        self.date_input.clear()
        self.item_input.clear()
        self.amount_input.clear()
        self.category_input.clear()

    def delete_expense(self, id, row):
        self.cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
        self.conn.commit()
        self.expense_table.removeRow(row)
        self.load_expenses()

    def filter_expenses(self):
        filter_text = self.filter_input.text()
        query = "SELECT * FROM expenses WHERE date LIKE ? OR category LIKE ?"
        self.cursor.execute(query, ('%' + filter_text + '%', '%' + filter_text + '%'))
        self.expense_table.setRowCount(0)
        self.total = 0.0
        for row_data in self.cursor.fetchall():
            row_position = self.expense_table.rowCount()
            self.expense_table.insertRow(row_position)
            for column, data in enumerate(row_data[1:]):
                self.expense_table.setItem(row_position, column, QTableWidgetItem(str(data)))
                if column == 2:
                    self.total += float(data)
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("background-color: #f44336; color: white; border: none; padding: 5px 10px; font-size: 16px;")
            delete_button.clicked.connect(lambda ch, id=row_data[0], row=row_position: self.delete_expense(id, row))
            self.expense_table.setCellWidget(row_position, 4, delete_button)
        self.total_expense.setText(f"Total Expense: ${self.total:.2f}")

    def clear_filter(self):
        self.filter_input.clear()
        self.load_expenses()

    def show_graph(self):
        self.cursor.execute("SELECT date, amount FROM expenses")
        data = self.cursor.fetchall()

        if not data:
            QMessageBox.warning(self, "No Data", "There are no expenses to show.")
            return

        dates = [datetime.datetime.strptime(record[0], "%Y-%m-%d") for record in data]
        amounts = [record[1] for record in data]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, amounts, marker='o', linestyle='-', color='b')
        plt.xlabel('Date')
        plt.ylabel('Amount')
        plt.title('Expenses Over Time')
        plt.grid(True)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseTrackerApp()
    window.show()
    sys.exit(app.exec_())

