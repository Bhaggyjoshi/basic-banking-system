from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'My$ql#Pa3sw@rd'
app.config['MYSQL_DB'] = 'bank'

mysql = MySQL(app)  



# Import the API routes
@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/customers', methods=['GET'])
def customers():
    #pull from transaction table
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM customers')
        data = cur.fetchall()

    return render_template("customers.html", data = data)

@app.route('/customer/<accountNo>', methods=['GET'])
def customer(accountNo):
    #pull from transaction table
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute(f'SELECT * FROM customers WHERE accountNo = {accountNo}')
        data = cur.fetchall()

    return render_template("customer.html", data = data)    


@app.route('/transactions', methods=['GET'])
def trasaction_history():
    #pull from transaction table
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM transactions')
        data = cur.fetchall()
    
    return render_template("transactions.html", data = data)


@app.route('/transfer', methods=["GET", "POST"])
def transfer_form():
    return render_template("transfer.html")


@app.route('/transfer_money', methods=["POST"])
def transfer_money():
    from_ac = int( request.form.get("from_ac"))
    to_ac = int(request.form.get("to_ac"))
    amount = int(request.form.get("amount"))
    
    #check if the from_ac and to_ac exist
    if  accounts_present(from_ac, to_ac) :
        #then check for amount
        if amount >0 :
            #check the transfer amount valid i.e. sufficient amout is present in senders account or not
            if isTransferable(from_ac, amount):
                # transfer amount
                make_transfer(from_ac, to_ac, amount)
                return render_template("successfull_trans.html")
            else:
                return  render_template("failed_temp.html", data="Insufficient amount")
        else:
            return render_template("failed_temp.html", data="Amount must be Greater than 0.")

    else:
        return render_template("failed_temp.html", data="Invalid Account !")
        #return acount not present
    # print(f"transefer amount of Rs. {amount} from {from_ac} -> to {to_ac}")
    # return "test successful"


'''
Make transfer from senders account ot receievers account and update transaction table also
'''
def make_transfer(from_ac, to_ac, amount):
    cur = mysql.connection.cursor()
    #debit amount from senders a/c
    sender_current_balance = get_balance(from_ac)
    sender_update_balance = sender_current_balance - amount

    cur.execute("UPDATE customers SET balance=%s where accountNo= %s",(sender_update_balance, from_ac))
    mysql.connection.commit()


    #credit same amount in recievers a/c
    receiver_current_balance = get_balance(to_ac)
    receiver_update_balance = receiver_current_balance + amount

    cur.execute("UPDATE customers SET balance=%s where accountNo= %s",(receiver_update_balance, to_ac))
    mysql.connection.commit()

    #make entry to trasactions table
    cur.execute("INSERT INTO transactions (from_cust, to_cust, amount, datetime) VALUES (%s, %s, %s, %s)", (from_ac, to_ac, amount, datetime.now()))
    mysql.connection.commit()

    cur.close()

def get_balance(ac):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT balance FROM customers where accountNo = {ac}")
    data = cur.fetchone()
    cur.close()
    return data[0]

'''
Check if amount is tranferable 
i.e. sender should have sufficient amount in account

'''
def isTransferable(from_ac, amount):
    #fetch details for account from customers
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT balance FROM customers where accountNo = {from_ac}")
    data = cur.fetchone()
    print(data)
    if data[0] - amount > 0:
        return True
    return False

'''
Check if both accounts are present of not 
'''
def accounts_present(from_ac, to_ac ):
    # check in data base accounts present or not:
    
    #get accont no from customers;
    cur = mysql.connection.cursor()
    cur.execute('SELECT accountNo FROM customers')
    data = cur.fetchall()
    # print(type(data))
    # print(data)
    # res = from_ac in data and to_ac in data
    # for item in data
    res_from= False
    res_to = False
    for item in data:
        if item[0] == from_ac:
            res_from =True
        if item[0] == to_ac:
            res_to = True

    # print(f"res_From {res_from}\n res_to {res_to}")

    return res_from and res_to
    
@app.route("/failed", methods=["GET"])
def failed():
    return render_template("failed_temp.html", data="testing message")


# Required because app is imported in other modules
if __name__== '__main__':
    print("Stating server...")
    app.run(debug=True)
