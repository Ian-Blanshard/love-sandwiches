import gspread
from google.oauth2.service_account import Credentials
from pprint import pprint

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('love_sandwiches')

def get_sales_data():
    """
    Get sales data from the user
    """
    while True:
        print('Please enter sales data from the last market.')
        print('Data should be six numbers, seperated by commas')
        print('Example: 10,20,30,40,50,60\n')

        data_str = input('Enter you data here: ')
        
        sales_data = data_str.split(',')
        if validate_data(sales_data):
            print('Data is valid')
            break
    return sales_data

def validate_data(values):
    """
    Inside the try, converts all string values into integers.
    Raises ValueError if string cannot be converted into int,
    or if there aren't exactly 6 values.
    """
    try:
        [int(value) for value in values]
        if len(values) != 6:
            raise ValueError(
                f'Exactly 6 values required, you provided {len(values)}'
            )
    except ValueError as e:
        print(f'Invalid data: {e}, please try again \n')
        return False
    return True

def update_worksheet(data, worksheet):
    """
    Update worksheet, add new row with the list data provided
    """
    print(f'Updating {worksheet} worksheet...\n')
    surplus_worksheet = SHEET.worksheet(f'{worksheet}')
    surplus_worksheet.append_row(data)
    print(f'{worksheet} worksheet updated successfully.\n')

def calculate_surplus(sales_row):
    """
    Compare sales with stock and calculate the surplus for each item type

    The surplus is defined as the sales figure subtracted from the stock
    - Positive surplus indicates waste
    - Negative surplus indicates extra made when the stock was sold out.
    """
    print('Calculating surplus data....\n')
    stock = SHEET.worksheet('stock').get_all_values()
    stock_row = stock[-1]
   
    surplus_data =[]
    for stock,sales in zip(stock_row, sales_row):
        surplus = int(stock) - sales
        surplus_data.append(surplus)
    
    return surplus_data


def get_last_5_entries_sales():
    """
    Collects columns of data from each sales worksheet, collecting
    the last 5 entries for each sandwich and returns the data as 
    a list of lists.
    """
    sales = SHEET.worksheet('sales')
    columns = []
    for ind in range(1, 7):
        column = sales.col_values(ind)
        columns.append(column[-5:])
    return columns


def calculate_stock_data(data):
    """
    Calculate the average stock for each item type, adding 10%
    """
    print('Calculating stock data....\n')
    new_stock_data = []
    for column in data:
        int_column = [int(num) for num in column]
        average = sum(int_column) / len(int_column)
        stock_num = average * 1.1
        new_stock_data.append(round(stock_num))
    
    return new_stock_data

def get_stock_values(data):
    """
    A function which takes the new stock data and heading of
    sandwich type and returns this as a dictionary, this dictionary
    is a guide for the next days stock
    """
    headings = SHEET.worksheet('sales').row_values(1)
    stock_vals_dict = {}
    for heading, value in zip(headings, data):
        stock_vals_dict[heading] = value
    return stock_vals_dict

def next_days_prep_guide(data):
    """
    A function which takes the dictionary of the next days stock and
    prints instructions to the terminal of what to create
    """
    for heading, stock in data.items():
        print(f'Please make {stock} {heading} sandwiches today')


def main():
    """
    Run all program functions
    """
    data = get_sales_data()
    sales_data = [int(num) for num in data]
    update_worksheet(sales_data, 'sales')
    new_surplus_data = calculate_surplus(sales_data)
    update_worksheet(new_surplus_data, 'surplus')
    sales_columns = get_last_5_entries_sales()
    stock_data = calculate_stock_data(sales_columns)
    update_worksheet(stock_data, 'stock')
    stock_values = get_stock_values(stock_data)
    next_days_prep_guide(stock_values)
    

print('Welcome to Love Sandwiches Data Automation')
main()
