from user.models import *
from user.user import user
from flask import *
from flask_session import Session
from bson import ObjectId
from datetime import date,timedelta
# date and time
def dates():
    t=date.today()
    s=t
    t=t+timedelta(days=7)
    t=t.strftime("%d, %b %Y")
    s=s.strftime("%d, %b %Y")
    return s,t
# total cart
def tot():
    res = mongo[db]['users'].find({"_id":ObjectId(session["id"])}, {"_id": 0, "cart": 1})
    result = fetch(res)
    total=0
    for i in result[0]['cart']:
       total+= int(i['qnt'])*i['price']
    return total
@user.route('/')
def index():
    if not session.get("name"):
        return render_template('index.html',t=0)
    else:
        a=tot()
        return render_template('index.html',t=a)
@user.route('/shop')
def shop():
    if not session.get("name"):
        res = mongo[db]['products'].find({}, {"__id": 1, "product_name": 1, "discount_price": 1, "img": 1})
        result = fetch(res)
        return render_template('shop.html', l=result,t=0)
    else:
        res=mongo[db]['users'].find({"_id":ObjectId(session['id'])},{"_id":0,"fav":1})
        r=fetch(res)
        res = mongo[db]['products'].find({},{"__id":1,"product_name":1,"discount_price":1,"img":1})
        result=fetch(res)
        return render_template('shop.html',l=result,fav=r[0],t=tot())
@user.route('/about')
def about():
    if not session.get("name"):
        return render_template('about.html',t=0)
    else:
        return render_template('about.html',t=tot())
@user.route('/checkout/<string:id>')
def checkout(id):
    oid = ObjectId(session["id"])
    res = mongo[db]['users'].find({'_id': oid}, {'_id': 0, 'cart': 1})
    result = fetch(res)
    return render_template('checkout.html', cart=result[0]['cart'],total=id,t=tot())
@user.route('/contact')
def contact():
    if not session.get("name"):
        return render_template('contact.html',t=0)
    else:
        return render_template('contact.html',t=tot())
@user.route('/fav')
def fav():
    if not session.get("id"):
        return render_template('shopping-cart.html',t=0)
    else:
        l=[]
        res = mongo[db]['users'].find({"_id": ObjectId(session['id'])}, {"_id": 0, "fav": 1})
        r = fetch(res)
        r=r[0]
        for i in r['fav']:
            res = mongo[db]['products'].find({},{"__id":1,"product_name":1,"discount_price":1,"img":1})
            r = fetch(res)
            l.append(r[0])
        res = mongo[db]['users'].find({"_id": ObjectId(session['id'])}, {"_id": 0, "fav": 1})
        r = fetch(res)
        return render_template('fav.html',l=l,fav=r[0],t=tot())
@user.route('/order')
def order():
    if not session.get("name"):
        return render_template('order.html',t=0)
    else:
        session.pop('_flashes',None)
        res = mongo[db]['orders'].find({"userid": session['id']})
        r = fetch(res)
        return render_template('order.html',t=tot(),order=r)
@user.route('/shop-details/<string:id>')
def shop_details(id):
    if not session.get("name"):
        oid = ObjectId(id)
        res = mongo[db]['products'].find({'_id': oid})
        result = fetch(res)
        img = zip(result[0]['img'])
        return render_template('shop-details.html', result=result[0],t=0)
    else:
        oid=ObjectId(id)
        res = mongo[db]['products'].find({'_id': oid})
        result = fetch(res)
        img=zip(result[0]['img'])
        return render_template('shop-details.html',result=result[0],t=tot())
@user.route('/shopping-cart')
def shopping_cart():
    if not session.get("id"):
        return render_template('shopping-cart.html',t=0)
    else:
        oid=ObjectId(session["id"])
        res = mongo[db]['users'].find({'_id': oid},{'_id':0,'cart':1})
        result = fetch(res)
        return render_template('shopping-cart.html',cart=result[0]['cart'],t=tot())
@user.route('/signin')
def signin():
    return render_template('signin.html')
@user.route('/signup')
def signup():
    return render_template('signup.html')
@user.route('/logout')
def logout():
    session['name']=None
    session["id"] = None
    session.clear()
    return redirect(url_for('user.index'))

# signup function
@user.route('/signup/user',methods=['GET','POST'])
def user_signup():
    if request.method=="POST":
        username=request.form['username']
        email = request.form['email']
        mobnum = request.form['mobnum']
        password = request.form['pass']
        cpassword=request.form['cpass']
        if password==cpassword:
            s = userdetails(username,email,mobnum,password,role)
            mongo[db]['users'].insert_one(s.user)
            del s
            return redirect(url_for('user.signin'))
        else:
            return render_template('signup.html')
    return render_template('signup.html')

# signin function
@user.route('/signin/user',methods=['GET','POST'])
def user_signin():
    if request.method=="POST":
        password=request.form['pass']
        email = request.form['email']
        res=mongo[db]['users'].find({'email':email,'password':password})
        result=fetch(res)
        if len(result)==1:
            session["id"]=str(result[0]['_id'])
            session["name"]=result[0]['username'].upper()
            return redirect(url_for('user.index'))
        else:
            return redirect(url_for('user.signin'))
    else:
        return render_template('signin.html')

# addcart function
@user.route('/addcart/<string:id>',methods=['POST','GET'])
def addcart(id):
    if not session.get("name"):
        return redirect(request.referrer)
    else:
        size=request.form['size']
        qnt=request.form['qnt']
        res = mongo[db]['users'].find({"_id": ObjectId(session['id'])}, {"_id": 0, "cart": 1})
        r = fetch(res)
        r = r[0]
        if ObjectId(id) in r['cart']:
            return redirect(request.referrer)
        else:
            res = mongo[db]['products'].find({"_id": ObjectId(id)}, {"_id": 0,"product_name":1,"img":1,"discount_price": 1})
            r = fetch(res)
            r = r[0]
            one={"product_id":ObjectId(id),"product_name":r['product_name'],"size":size,"qnt":qnt,"price":r['discount_price'],"img":r['img'][0] }
            mongo[db]['users'].update_one({"_id": ObjectId(session.get("id"))}, {"$push": {"cart": one}})
            return redirect(request.referrer)

# removecart function
@user.route('/removecart/<string:id>')
def removecart(id):
    if not session.get("name"):
        return redirect(request.referrer)
    else:
        res = mongo[db]['users'].find({"_id": ObjectId(session['id'])}, {"_id": 0, "cart": 1})
        r = fetch(res)
        r = r[0]
        r=r['cart']
        mongo[db]['users'].update_one({"_id": ObjectId(session.get("id"))}, {"$pull": {"cart": {"product_id": ObjectId(id)}}})
        return redirect(request.referrer)

# addfav function

@user.route('/addfav/<string:id>')
def addfav(id):
    if not session.get("name"):
        return redirect(request.referrer)
    else:
        res = mongo[db]['users'].find({"_id": ObjectId(session['id'])}, {"_id": 0, "fav": 1})
        r = fetch(res)
        r=r[0]
        if ObjectId(id) in r['fav']:
            mongo[db]['users'].update_one({"_id": ObjectId(session.get("id"))}, {"$pull": {"fav": ObjectId(id)}})
        else:
            mongo[db]['users'].update_one({"_id": ObjectId(session.get("id"))}, {"$push": {"fav": ObjectId(id)}})
        return redirect(request.referrer)
@user.route('/addfav/shop-details/<string:id>')
def add_fav(id):
    if not session.get("name"):
        return redirect(request.referrer)
    else:
        res = mongo[db]['users'].find({"_id": ObjectId(session['id'])}, {"_id": 0, "fav": 1})
        r = fetch(res)
        r = r[0]
        if ObjectId(id) in r['fav']:
            return redirect(request.referrer)
        else:
            mongo[db]['users'].update_one({"_id": ObjectId(session.get("id"))}, {"$push": {"fav": ObjectId(id)}})
            return redirect(request.referrer)

# Checkout function
@user.route('/checkout',methods=['GET','POST'])
def checkoutf():
    if request.method=="POST":
        fname=request.form['fname']
        lname=request.form['lname']
        email = request.form['email']
        phno = request.form['phno']
        city = request.form['city']
        pincode = request.form['pincode']
        state = request.form['state']
        street = request.form['street']
        apartment=request.form['apartment']
        msg = request.form['notes']
        details={"fname":fname,"lname":lname,"email":email,"phno":phno,"city":city,"pincode":pincode,"state":state,"street":street,"apartment":apartment,"msg":msg}
        oid = ObjectId(session["id"])
        res = mongo[db]['users'].find({'_id': oid}, {'_id': 0, 'cart': 1})
        result = fetch(res)
        result=result[0]['cart']
        s,e=dates()
        o=Orders(session["id"],session["name"],details,result,s,e,"Processing",tot())
        mongo[db]['orders'].insert_one(o.order)
        del o
        for i in result:
            print(i)
            a=i["product_id"]
            mongo[db]['users'].update_one({"_id": ObjectId(session.get("id"))},{"$pull": {"cart": {"product_id": a}}})
        flash("success",'success')
        return redirect(request.referrer)

# cancel order
@user.route('/cancel/<string:id>')
def cancel(id):
    mongo[db]['orders'].update_one({"_id": ObjectId(id)}, {"$set": {"status": "Cancelled"}})
    return redirect(request.referrer)
