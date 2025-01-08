from flask import Flask, render_template, request
import mysql.connector
from pymongo import MongoClient

app = Flask(__name__)

# MySQL: Fetch customer and order details based on CustomerID
def get_customer_order_details(customer_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="taruntarun",
        database="ecommerce",
        port=3306
    )
    cursor = conn.cursor()

    # Fetch customer details
    query_customer = "SELECT * FROM Customers WHERE CustomerID = %s"
    cursor.execute(query_customer, (customer_id,))
    customer = cursor.fetchone()

    # Fetch orders related to the customer
    query_orders = "SELECT * FROM Orders WHERE CustomerID = %s"
    cursor.execute(query_orders, (customer_id,))
    orders = cursor.fetchall()

    cursor.close()
    conn.close()
    return customer, orders

# MongoDB: Configuration and fetch product details
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]

def get_product_details(product_id):
    # Match product_id with MongoDB collection
    product = db["products"].find_one({"productID": product_id})
    return product

# Home route: Rendering the home page with a form
@app.route('/')
def home():
    return render_template('home.html')

# Fetch route: Handling form submission to fetch customer, orders, and product details
@app.route('/fetch', methods=['POST'])
def fetch():
    customer_id = request.form.get('customer_id')
    
    if customer_id:
        customer_id = int(customer_id)

        # Fetch data from MySQL
        customer_data, order_data = get_customer_order_details(customer_id)

        # Fetch product data from MongoDB based on the first order
        if order_data:
            product_id = order_data[0][2]  # Assuming the second column is ProductID
            product_data = get_product_details(product_id)
        else:
            product_data = None
        # print (customer_data)

        return render_template('index.html', 
                               customer=customer_data, 
                               orders=order_data, 
                               product=product_data)
    else:
        return "Please provide a valid Customer ID."

if __name__ == '__main__':
    app.run(debug=True)
