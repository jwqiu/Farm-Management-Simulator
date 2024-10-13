from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from datetime import date, datetime, timedelta
import mysql.connector
import connect

app = Flask(__name__)
app.secret_key = 'COMP636 S2'

start_date = datetime(2024,10,29)
pasture_growth_rate = 65    #kg DM/ha/day
stock_consumption_rate = 14 #kg DM/animal/day

db_connection = None
 
def getCursor():
    """Gets a new dictionary cursor for the database.
    If necessary, a new database connection is created here and used for all
    subsequent to getCursor()."""
    global db_connection
 
    if db_connection is None or not db_connection.is_connected():
        db_connection = mysql.connector.connect(user=connect.dbuser, \
            password=connect.dbpass, host=connect.dbhost,
            database=connect.dbname, autocommit=True)
       
    cursor = db_connection.cursor(buffered=False)   # returns a list
    # cursor = db_connection.cursor(dictionary=True, buffered=False)
   
    return cursor

def get_date():
    Connection=getCursor()
    qstr0="SELECT * FROM curr_date;"
    Connection.execute(qstr0)
    curr_date=Connection.fetchone()[0]
    return curr_date

@app.route("/")
def home():

    curr_date=get_date()

    Connection=getCursor()  
    qstr1="SELECT count(*) FROM stock;"
    qstr2="SELECT round(avg(weight),0) FROM stock;"
    Connection.execute(qstr1)
    totalcows = Connection.fetchone()  

    Connection.execute(qstr2)        
    avgweight = Connection.fetchone() 

    qstr3 ="SELECT * FROM stock;"
    Connection.execute(qstr3)        
    stocks = Connection.fetchall()
    
    updated_stocks=[]
    ages=[]
    current_date=start_date.date()
    for stock in stocks:
        date_of_birth=stock[2]
        age=current_date.year-date_of_birth.year
        if (current_date.month,current_date.day)<(date_of_birth.month,date_of_birth.day):
            age=age-1
        ages.append(age)
        new_stock=list(stock)
        new_stock.append(age)
        updated_stocks.append(new_stock)

    avg_age=sum(ages)/len(ages)

    underweight=0
    for stock in updated_stocks:
        if stock[3]<=300 and stock[4]>=1:
            underweight=underweight+1


    qstr4 = """
    SELECT paddocks.id,paddocks.name,paddocks.area,paddocks.dm_per_ha,paddocks.total_dm,mobs.name AS mobname,mobs.id AS mobid,COUNT(stock.id) AS numofstock FROM paddocks
    LEFT JOIN mobs on mobs.paddock_id=paddocks.id
    LEFT JOIN stock on mobs.id=stock.mob_id
    GROUP BY paddocks.id;
    """
    Connection.execute(qstr4)        
    Paddocks = Connection.fetchall()

    pgr=pasture_growth_rate
    scr=stock_consumption_rate

    updated_Paddocks=[]

    for paddock in Paddocks:
        changerate=round(paddock[2]*pgr-paddock[7]*scr,0)
        new_paddock=list(paddock)
        new_paddock.append(changerate)
        if changerate<=0:
            days=0
            pasturelevel=(paddock[4]+(changerate*days))/paddock[2] 
            while pasturelevel>1500:
                days=days+1
                pasturelevel=(paddock[4]+(changerate*days))/paddock[2] 
        else:
            days=""
        new_paddock.append(days)
        updated_Paddocks.append(new_paddock)

    return render_template("home.html",curr_date=curr_date,totalcows=totalcows,avgweight=avgweight,avg_age=avg_age,underweight=underweight,updated_Paddocks=updated_Paddocks)

@app.route("/clear-date")
def clear_date():
    """Clear session['curr_date']. Removes 'curr_date' from session dictionary."""
    session.pop('curr_date')
    return redirect(url_for('paddocks'))  

@app.route("/reset-date")
def reset_date():
    # session.update({'curr_date': start_date.strftime('%Y-%m-%d')})
    Connection=getCursor()  
    with open('fms-local.sql','r') as file:
        sql_content=file.read()
        for statement in sql_content.split(';'):
            Connection.execute(statement)        

    return redirect(url_for('paddocks'))  

@app.route("/nextday")
def nextday():
    curr_date=get_date()

    curr_date=curr_date+timedelta(days=1)
    # session.update({'curr_date': curr_date.strftime('%Y-%m-%d')})

    Connection=getCursor()
    qstr="""
    SELECT paddocks.id,paddocks.name,paddocks.area,paddocks.dm_per_ha,paddocks.total_dm,mobs.name AS mobname,mobs.id AS mobid,COUNT(stock.id) AS numofstock FROM paddocks
    LEFT JOIN mobs on mobs.paddock_id=paddocks.id
    LEFT JOIN stock on mobs.id=stock.mob_id
    GROUP BY paddocks.id
    ORDER BY mobs.name;
    """
    Connection.execute(qstr)        
    paddocks = Connection.fetchall() 

    for paddock in paddocks:
        area=paddock[2]
        growth = area * pasture_growth_rate
        numofstock=paddock[7]
        consumption = numofstock * stock_consumption_rate
        total_dm=paddock[4]
        total_dm=total_dm+growth-consumption
        dm_per_ha=paddock[3]
        dm_per_ha=round(total_dm / area,2)
        qstr="""
        UPDATE paddocks
        SET dm_per_ha=%s,total_dm=%s
        WHERE id=%s;
        """
        values=(dm_per_ha,total_dm,paddock[0])
        Connection.execute(qstr,values)
        db_connection.commit()

        qstr="""
        UPDATE curr_date
        SET curr_date=%s;
        """
        values=(curr_date,)
        Connection.execute(qstr,values)
        db_connection.commit()

    return redirect(url_for('paddocks'))  


@app.route("/mobs")
def mobs():
    """List the mob details (excludes the stock in each mob)."""
    connection = getCursor()        
    qstr = """
    SELECT paddocks.id,paddocks.name,paddocks.area,paddocks.dm_per_ha,paddocks.total_dm,mobs.name AS mobname,mobs.id AS mobid,COUNT(stock.id) AS numofstock FROM paddocks
    LEFT JOIN mobs on mobs.paddock_id=paddocks.id
    LEFT JOIN stock on mobs.id=stock.mob_id
    GROUP BY paddocks.id
    ORDER BY mobs.name;
    """
    connection.execute(qstr)        
    mobs = connection.fetchall()   
    curr_date=get_date()
     
    return render_template("Mobs.html", mobs=mobs,curr_date=curr_date)  


@app.route("/paddocks")
def paddocks():
    connection = getCursor()        
    qstr = """
    SELECT paddocks.id,paddocks.name,paddocks.area,paddocks.dm_per_ha,paddocks.total_dm,mobs.name AS mobname,mobs.id AS mobid,COUNT(stock.id) AS numofstock FROM paddocks
    LEFT JOIN mobs on mobs.paddock_id=paddocks.id
    LEFT JOIN stock on mobs.id=stock.mob_id
    GROUP BY paddocks.id
    ORDER BY paddocks.name;
    """
    connection.execute(qstr)        
    Paddocks = connection.fetchall()

    pgr=pasture_growth_rate
    scr=stock_consumption_rate

    updated_Paddocks=[]

    for paddock in Paddocks:
        changerate=round(paddock[2]*pgr-paddock[7]*scr,0)
        new_paddock=list(paddock)
        new_paddock.append(changerate)
        if changerate<=0:
            days=0
            pasturelevel=(paddock[4]+(changerate*days))/paddock[2] 
            while pasturelevel>1500:
                days=days+1
                pasturelevel=(paddock[4]+(changerate*days))/paddock[2] 
        else:
            days=""
        new_paddock.append(days)
        updated_Paddocks.append(new_paddock)

    curr_date=get_date()


    return render_template("Paddocks.html",updated_Paddocks=updated_Paddocks,curr_date=curr_date)  

@app.route("/stock")
def stock():
    connection = getCursor()        
    qstr ="""    
    SELECT stock.id,stock.weight,stock.dob,mobs.id AS mobid,mobs.name AS mobname,mobs.paddock_id,paddocks.name AS paddockname FROM stock
    INNER JOIN mobs on mobs.id=stock.mob_id
    INNER JOIN paddocks on mobs.paddock_id=paddocks.id
    GROUP BY stock.id
    ORDER BY stock.id;"""
    connection.execute(qstr)        
    stocks = connection.fetchall()
    updated_stocks=[]
    start_date = datetime(2024,10,29)
    current_date=start_date.date()
    for stock in stocks:
        date_of_birth=stock[2]
        age_days=(current_date-date_of_birth).days
        age_years=age_days//365
        if (current_date.month,current_date.day)<(date_of_birth.month,date_of_birth.day):
            age_years=max(age_years-1,0)
        new_stock=list(stock)
        new_stock.append(age_years)
        updated_stocks.append(new_stock)

    connection = getCursor()        
    qstr ="""
    SELECT mobid,mobname,numofstock,paddocks.name AS paddockname,round(avgweight) FROM
    (SELECT mobs.id AS mobid,mobs.name AS mobname,count(stock.id) AS numofstock,mobs.paddock_id AS paddockid,avg(stock.weight) AS avgweight FROM stock
    INNER JOIN mobs ON mobs.id=stock.mob_id
    GROUP BY mobs.id) AS z
    LEFT JOIN paddocks ON paddockid=paddocks.id
    GROUP BY mobid
    order by z.mobname;
    """
    connection.execute(qstr)        
    mobs = connection.fetchall()
    curr_date=get_date()

    return render_template("Stock.html",updated_stocks=updated_stocks,mobs=mobs,curr_date=curr_date)  

@app.route("/move_mob")
def move_mob():
    connection = getCursor()        
    qstr="""
    SELECT paddocks.id,paddocks.name,paddocks.area,paddocks.dm_per_ha,paddocks.total_dm,mobs.name AS mobname,mobs.id AS mobid,COUNT(stock.id) AS numofstock FROM paddocks
    LEFT JOIN mobs on mobs.paddock_id=paddocks.id
    LEFT JOIN stock on mobs.id=stock.mob_id
    GROUP BY paddocks.id
    ORDER BY mobs.name;
    """
    connection.execute(qstr)        
    mobnpaddock = connection.fetchall()
    
    from_page=request.args.get('from')
    curr_date=get_date()

    return render_template("Move_Mob.html",from_page=from_page,mobnpaddock=mobnpaddock,curr_date=curr_date)  

@app.route("/move_mob_submit",methods=['POST'])
def move_mob_submit():
    
    mobid=request.form.get('mobid')
    paddock_id=request.form.get('paddock_id')
    connection = getCursor()        
    qstr="""UPDATE mobs
    SET paddock_id=%s
    WHERE id=%s;
    """
    values=(paddock_id,mobid)
    connection.execute(qstr,values)
    db_connection.commit()        
    
    curr_date=get_date()

    from_page = request.form.get('from_page')
    if from_page:
        return redirect(from_page)
    else:
        return redirect(url_for('mobs'))
    
@app.route("/add_paddock")
def add_paddock():
    curr_date=get_date()

    return render_template("Add_Paddock.html",curr_date=curr_date)  

@app.route("/add_paddock_submit",methods=['POST'])
def add_paddock_submit ():
    paddock_name=request.form.get('paddock_name')
    area=request.form.get('area')
    dm_ha=request.form.get('dm_ha')
    connection = getCursor()
    total_dm=float(dm_ha)*float(area)
    qstr="""INSERT INTO paddocks(name,dm_per_ha,area,total_dm)
    VALUES(%s,%s,%s,%s);
    """
    values=(paddock_name,dm_ha,area,total_dm)
    connection.execute(qstr,values)
    db_connection.commit()        
    return redirect(url_for('paddocks'))  

@app.route("/delete_paddock",methods=['POST'])
def delete_paddock ():
    connection = getCursor()
    paddock_id=request.form.get('paddock_id')
    qstr="DELETE FROM paddocks WHERE id=%s"
    values=(paddock_id,)
    connection.execute(qstr,values)
    db_connection.commit()        
    return redirect(url_for('paddocks'))  

@app.route("/edit_paddockk",methods=['GET'])
def edit_paddock():
    curr_date=get_date()
    id=request.args.get('id')    
    connection = getCursor()
    qstr="SELECT * FROM paddocks WHERE id=%s;"
    values=(id,)
    connection.execute(qstr,values)
    paddock_detail=connection.fetchone()
    return render_template("Edit_Paddock.html",paddock_detail=paddock_detail,curr_date=curr_date)  

@app.route("/edit_paddockk_submit",methods=['POST'])
def edit_paddock_submit():
    paddock_name=request.form.get('paddock_name')
    area=request.form.get('area')
    dm_ha=request.form.get('dm_ha')
    paddock_id=request.form.get('paddock_id')
    connection = getCursor()
    total_dm=float(area)*float(dm_ha)
    qstr="""
    UPDATE paddocks
    SET name=%s,area=%s,dm_per_ha=%s,total_dm=%s
    WHERE id=%s
"""
    values=(paddock_name,area,dm_ha,total_dm,paddock_id)
    connection.execute(qstr,values)
    db_connection.commit()        

    return redirect(url_for('paddocks'))  

if __name__ == '__main__':
    app.run(debug=True)
