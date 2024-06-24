from pymongo import MongoClient
mongo = MongoClient('mongodb://localhost:27017')
role="user"
db="trap"
class userdetails:
    user={}
    def __init__(self,name,email,mobnum,password,role):
        self.user['username']=name
        self.user['email'] = email
        self.user['mobilenumber'] = mobnum
        self.user['password'] = password
        self.user['role'] = role
        self.user['fav'] = []
        self.user['cart'] = []

class Orders:
    order={}
    def __init__(self,id,name,details,cart,order_date,delivery_date,status,total,adelivery_date=None):
        self.order['userid']=id
        self.order['username']=name
        self.order['details'] = details
        self.order['cart'] = cart
        self.order['order_date'] = order_date
        self.order['delivery_date'] = delivery_date
        self.order['adelivery_date'] = adelivery_date
        self.order['status'] = status
        self.order['total']=total

class product:
    product = {}
    def __init__(self, product_name, discount_price, original_price, size,quantity, product_info,material_used,images):
        self.user['username'] = name
        self.user['email'] = email
        self.user['mobilenumber'] = mobnum
        self.user['password'] = password
        self.user['role'] = role
        self.user['fav'] = []
        self.user['cart'] = []

def fetch(r):
    l=[]
    for i in r:
        l.append(i)
    return l