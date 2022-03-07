from ast import For
from atexit import register
from audioop import add
from cgitb import text
from distutils.util import execute
from multiprocessing.sharedctypes import Value
from re import search
from turtle import st
from fractions import Fraction
from typing_extensions import Required
from urllib import request
from fastapi import FastAPI, Query, Request, Cookie
from fastapi.params import Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import starlette.status as status 
import sqlite3
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from Email import Email

#creating a FastAPI object
travel = FastAPI()  
security = HTTPBasic()
#----------------------------------EMAIL INEGRATION------------------------------------------#
emailsender = Email("fourseasons.travel04@gmail.com", "fourseasons04")
ADMIN_MAIL = "fourseasons.travel04@gmail.com"

#configuring the static, which serve static
travel.mount("/static", StaticFiles(directory="static"), name="static")

#configuring the HTML pages
templates = Jinja2Templates(directory="templates")

travel.add_middleware(SessionMiddleware, secret_key='4seasons')

DATABASE_NAME = "4seasons.db"
#------------------------------------EXPLORE PAGE -------------------------------------------#
#explore page 
@travel.get("/", response_class=HTMLResponse)
def explore(request : Request):
    return templates.TemplateResponse("explore.html", { "request" : request })

#------------------------------------HOME PAGE -------------------------------------------#
#home page 
@travel.get("/home", response_class=HTMLResponse)
def home(request : Request):
    return templates.TemplateResponse("home.html", {"request" : request})

#home page - login section
@travel.get("/login-section", response_class=HTMLResponse)
def login_section(request : Request):
    return templates.TemplateResponse("login-section.html", {"request" : request})

#home page - sign up
@travel.get("/reg-section", response_class=HTMLResponse)
def reg_section(request : Request):
    return templates.TemplateResponse("reg-section.html", {"request" : request})

#home page -join us 
@travel.get("/joinus", response_class=HTMLResponse)
def joinus(request : Request):
    return templates.TemplateResponse("joinus.html", {"request" : request})

#home page - bus 
@travel.get("/bus", response_class=HTMLResponse)
def bus(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Bus limit 6;" )
    bus = cur.fetchall()
    con.close
    return templates.TemplateResponse("bus.html", {"request" : request, "bus" : bus})



#home page - hotel
@travel.get("/hotel", response_class=HTMLResponse)
def hotel(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Hotel limit 7;" )
    hotel = cur.fetchall()
    con.close
    return templates.TemplateResponse("hotel.html", {"request" : request , "hotel": hotel})

#home page -flight
@travel.get("/flydeskblore", response_class=HTMLResponse)
def flydeskblore(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(" SELECT * FROM Flight  LIMIT 6 ;" )
    flight1 = cur.fetchall()
    con.close
    return templates.TemplateResponse("flydeskblore.html", {"request" : request, "flight1":flight1})

#------------------------------------LOGIN SECTION -------------------------------------------#
#home page -login admin
@travel.get("/lgn-admin", response_class=HTMLResponse)
def lgn_admin(request : Request):
    return templates.TemplateResponse("lgn-admin.html", {"request" : request})

@travel.post("/lgn-admin",response_class=HTMLResponse)
def post_lgnadmin(request :Request,adminname : str = Form(...),email : str = Form(...), password : str = Form(...)):
    con = sqlite3.connect(DATABASE_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Admin where admin_name=? and  admin_email=? and admin_pwd=?", [adminname,email, password])
    admin = cur.fetchone()
    if not admin:
        return templates.TemplateResponse("lgn-admin.html", {"request": request, "msg": "Invalid Admin Credential"})
    else:
        request.session.setdefault("isLogin", True)
        request.session.setdefault('username', admin['admin_name'])
        request.session.setdefault('adminid', admin['admin_id'])
    #database -> inserting or updating, can be done POST request
    return RedirectResponse("/admin",status_code=status.HTTP_302_FOUND)
    

#home page -login user
@travel.get("/lgn-usr", response_class=HTMLResponse)
def lgn_usr(request : Request):
    return templates.TemplateResponse("lgn-usr.html", {"request" : request})

@travel.post("/lgn-usr",response_class=HTMLResponse)
def post_lgnusr(request :Request, username : str = Form(...),email: str = Form(...), password : str = Form(...)):
    con = sqlite3.connect(DATABASE_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from User where user_name=? and  user_email=? and user_pwd=?", [username,email, password])
    user = cur.fetchone()
    if not user:
        return templates.TemplateResponse("lgn-usr.html", {"request": request, "msg": "Invalid Username , User Id or Password"})
    else:
        request.session.setdefault("isLogin", True)
        request.session.setdefault('username', user['user_name'])
        request.session.setdefault('user_id', user['user_id'])
        return RedirectResponse("/user",status_code=status.HTTP_302_FOUND)

@travel.get("/logout", response_class=HTMLResponse)
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/lgn-usr", status_code=status.HTTP_302_FOUND)

#------------------------------------SIGN UP SECTION  -------------------------------------------#

#home page -signup user
@travel.get("/reg-usr", response_class=HTMLResponse)
def reg_usr(request : Request):
    return templates.TemplateResponse("reg-usr.html", {"request" : request})

@travel.post("/reg-usr",response_class=HTMLResponse)
def post_regusr(request :Request,username : str = Form(...),address: str = Form(...),pincode : str = Form(...),email : str = Form(...), password : str = Form(...)):
    #database -> inserting or updating, can be done POST request
    with sqlite3.connect(DATABASE_NAME) as con:
        cur = con.cursor()
        cur.execute("INSERT into User(user_name,user_add,user_pincode, user_email,user_pwd) values(?,?,?,?,?)",
                    (username, address,pincode,email,password ))
        con.commit()
    return RedirectResponse("/lgn-usr",status_code=status.HTTP_302_FOUND)


#------------------------------------BUS PAGE -------------------------------------------#
#bus page -bus1
@travel.get("/bus1", response_class=HTMLResponse)
def bus1(request : Request):
    user_id = request.session.get('user_id')
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Bus limit 6 OFFSET 6" )
    bus = cur.fetchall()
    con.close
    return templates.TemplateResponse("bus1.html", {"request" : request, "bus" : bus})
    

#bus page -bus2
@travel.get("/bus2", response_class=HTMLResponse)
def bus2(request : Request):
    user_id = request.session.get('user_id')
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Bus limit 6 OFFSET 12 " )
    bus = cur.fetchall()
    con.close
    return templates.TemplateResponse("bus2.html", {"request" : request, "bus" : bus})
    

#bus page - bus info 
@travel.get("/bus-info/{bid}", response_class=HTMLResponse)
def bus_info(request : Request, bid:int):
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    con = sqlite3.connect(DATABASE_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM Bus WHERE bus_id=?",[bid])
    binfo= cur.fetchall()
    con.close
    return templates.TemplateResponse("bus-info.html", {"request": request, "bid": bid, "binfo": binfo[0]})


#bus page - bus cart
@travel.get("/bcart", response_class=HTMLResponse)
def bcart(request : Request, bid:str ,depdate:str ,seatnumber:str):
    user_id = request.session.get('user_id')
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    con = sqlite3.connect(DATABASE_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM Bus  WHERE bus_id=?", [bid])
    Bus = cur.fetchall()
    con.close
    return templates.TemplateResponse("bcart.html", {"request" : request, "bid": bid,"depdate":depdate,"seatnumber":seatnumber, "Bus":Bus[0] ,})

@travel.post("/bcart",response_class=HTMLResponse)
def post_hcart(request :Request,bid:str =Form(...), username : str = Form(...),email: str = Form(...),mobilenumber : str = Form(...),busnumber:str =Form(...),buscomp:str =Form(...),b_from:str =Form(...),b_to:str =Form(...),dept:str =Form(...),arr:str =Form(...),deptime:str =Form(...),arrtime:str =Form(...),depdate:str =Form(...),terminal:str =Form(...),bustype:str=Form(...),seatnumber:str=Form(...),totalprice:str=Form(...)):
    #database -> inserting or updating, can be done POST request
    user_id = request.session.get('user_id')
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    with sqlite3.connect(DATABASE_NAME) as con:
        cur = con.cursor()
        con.row_factory = sqlite3.Row
        cur.execute("SELECT * from Bus b where b.bus_id=?", [bid])
        Bus = cur.fetchall()
        actual_seats = Bus[0][7]
        remaining_seats = int(actual_seats) - int(seatnumber)
        cur.execute("UPDATE Bus SET total_seats = ? where bus_id=?",[str(remaining_seats) ,bid])
        cur.execute("INSERT into Busorders(user_id,username,email,phone,busnumber,buscomp,b_from,b_to,dept,arr,deptime,arrtime,depdate,terminal,bustype,seatnumber,totalprice) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (user_id,username, email,mobilenumber,busnumber,buscomp,b_from,b_to,dept,arr,deptime,arrtime,depdate,terminal,bustype,seatnumber,totalprice))
        con.commit()
        emailsender.sendMail([email],"BOOKING SUCCESSFULL! \n" ,"DEAR  " +username + ", \n" + "You have succesfully booked your Bus! \n " 
        +"Please find the Details below \n" + "*******************************\n"+ "Bus company:    " +buscomp +"\n" "Bus Number:    " +busnumber +"\n" 
        +"Bus Type:    " +bustype +"\n" "From   " +b_from +"\n" "To:   " +b_to +"\n" "Departure Station:    " 
        +dept +"Arrival Station:   "+arr +"Departure Date:   "+depdate +"Departure Time:   "+deptime +"Arrival Time:   " +arrtime +"Terminal:    "+terminal+ "No. of Seats:  "+seatnumber +"\n" +"*******************************\n" + "THANKYOU \n" +"Regards, \n" +"Fourseasons")
        emailsender.sendMail([ADMIN_MAIL],"NEW BUS BOOKING! \n" ,"Username:  " +username +" \n"+"Email:  "+email+"\n"+"Contact no. :    "+mobilenumber +"\n" + "Bus company:    " +buscomp +"\n" "Bus Number:    " +busnumber +"\n" 
        +"Bus Type:    " +bustype +"\n" "From   " +b_from +"\n"+ "To:   " +b_to +"\n" "Departure Station:    " 
        +dept +"\n" +"Arrival Station:   "+arr +"\n" +"Departure Date:   "+depdate +"\n"+"Departure Time:   "+deptime +"\n"+"Arrival Time:   " +arrtime +"\n"+"Terminal:    "+terminal+"\n" +"No. of Seats:  "+seatnumber +"\n" )
    return RedirectResponse("/confirm",status_code=status.HTTP_302_FOUND)

#------------------------------------HOTEL PAGE -------------------------------------------#
#hotel page -hotel2
@travel.get("/hotel2", response_class=HTMLResponse)
def hotel2(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Hotel limit 7 OFFSET 7;" )
    hotel = cur.fetchall()
    con.close
    return templates.TemplateResponse("hotel2.html", {"request" : request , "hotel": hotel})
  

#hotel page -hotel3
@travel.get("/hotel3", response_class=HTMLResponse)
def hotel3(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Hotel limit 7 OFFSET 14;" )
    hotel = cur.fetchall()
    con.close
    return templates.TemplateResponse("hotel3.html", {"request" : request , "hotel": hotel})

#hotel page -hotel4
@travel.get("/hotel4", response_class=HTMLResponse)
def hotel4(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Hotel limit 8 OFFSET 21;" )
    hotel = cur.fetchall()
    con.close
    return templates.TemplateResponse("hotel4.html", {"request" : request , "hotel": hotel})


#hotel page - hotel info
@travel.get("/hotel-info/{hid}", response_class=HTMLResponse)
def hotel_info(request : Request , hid: int):
    user_id = request.session.get('user_id')
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    con = sqlite3.connect(DATABASE_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Hotel where hotel_id =?", [hid])
    hinfo = cur.fetchall()
    con.close
    return templates.TemplateResponse("hotel-info.html", {"request": request, "hid": hid, "hinfo": hinfo[0]})


#hotel page - hotel cart
@travel.get("/hcart", response_class=HTMLResponse)
def hcart_hotels(request: Request,hid:str,room:str,bed:str,cin:str,cout:str,guests:str):
    user_id = request.session.get('user_id')
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    con = sqlite3.connect(DATABASE_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * from Hotel h where h.hotel_id=?", [hid])
    hotels = cur.fetchall()
    cur.execute("SELECT * FROM Room r WHERE r.room_id=?" ,[room])
    rooms = cur.fetchall()
    cur.execute("SELECT * from Extrabed e WHERE e.bed_id=?" ,[bed])
    beds = cur.fetchall()
    con.close
    return templates.TemplateResponse("hcart.html", {"request": request,"hid":hid,"cin":cin, "cout":cout,"guests":guests, "room":room, "bed":bed,"hotels": hotels[0],"rooms":rooms[0],"beds":beds[0]})

@travel.post("/hcart",response_class=HTMLResponse)
def post_hcart(request :Request,hid:str =Form(...),room:str =Form(...),bed:str =Form(...), 
username : str = Form(...),email: str = Form(...),mobilenumber : str = Form(...),hotelname:str =Form(...),
hotellocation:str =Form(...),roomtype:str =Form(...),extrabed:str =Form(...),checkin:str =Form(...),checkout:str =Form(...),
servicefee:str =Form(...),totalprice:str =Form(...), totalrooms:int = Form(...),guests:str =Form(...)):

    #database -> inserting or updating, can be done POST request
    with sqlite3.connect(DATABASE_NAME) as con:
        user_id = request.session.get('user_id')
        cur = con.cursor()
        con.row_factory = sqlite3.Row
        cur.execute("SELECT * from Hotel h where h.hotel_id=?", [hid])
        hotels = cur.fetchall()
        actual_rooms = hotels[0][4]
        remaining_hotels = int(actual_rooms) - totalrooms
        cur.execute("INSERT into Horders(user_id,username,email,phone,hotelname,hotellocation,roomtype,extrabed,checkin,checkout,servicefee,totalprice,guests) values(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (user_id,username, email,mobilenumber,hotelname,hotellocation,roomtype,extrabed,checkin,checkout,servicefee,totalprice,guests))     
        cur.execute("UPDATE Hotel SET total_rooms = ? where hotel_id=?",[str(remaining_hotels) ,hid])
        con.commit()
        emailsender.sendMail([email],"BOOKING SUCCESSFULL! \n" ,"DEAR  " +username + ", \n" + "You have succesfully booked your staycation! \n " +"Please find the Details below \n" + "*******************************\n"+ "Hotel Name:    " +hotelname +"\n" "Hotel Location:    " +hotellocation +"\n" +"Room Type:    " +roomtype +"\n" "Extra bed Type:    " +extrabed +"\n" "CHECK-IN DATE:    " +checkin +"\n" "CHECK-OUT DATE:    " +checkout +"\n" +"*******************************\n" + "THANKYOU \n" +"Regards, \n" +"Fourseasons")
        emailsender.sendMail([ADMIN_MAIL],"NEW HOTEL BOOKING! \n" ,"Username:  " +username  +"\n"+"Email:    "+email+"\n" +"Contact no. :   "+mobilenumber +"\n" + "Hotel Name:    " +hotelname +"\n" "Hotel Location:    " +hotellocation +"\n" +"Room Type:    " +roomtype +"\n" "Extra bed Type:    " +extrabed +"\n" "CHECK-IN DATE:    " +checkin +"\n" "CHECK-OUT DATE:    " +checkout +"\n")
    return RedirectResponse("/confirm",status_code=status.HTTP_302_FOUND)



#------------------------------------FLIGHT PAGE -------------------------------------------#
#flight page -f2 chennai
@travel.get("/chennai", response_class=HTMLResponse)
def chennai(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(" SELECT * FROM Flight  LIMIT 6  OFFSET 6" )
    chennai = cur.fetchall()
    con.close
    return templates.TemplateResponse("chennai.html", {"request" : request ,"chennai":chennai})

#flight page -f3 kerala
@travel.get("/kerala", response_class=HTMLResponse)
def kerala(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(" SELECT * FROM Flight  LIMIT 6 OFFSET 12" )
    ker = cur.fetchall()
    con.close
    return templates.TemplateResponse("kerala.html", {"request" : request,"ker":ker })

#flight page -f4 goa
@travel.get("/goa", response_class=HTMLResponse)
def goa(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(" SELECT * FROM Flight  LIMIT 6  OFFSET 18" )
    goa = cur.fetchall()
    con.close
    return templates.TemplateResponse("goa.html", {"request" : request,"goa":goa})

#flight page -f5 hyd
@travel.get("/hyd", response_class=HTMLResponse)
def hyd(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(" SELECT * FROM Flight LIMIT 6 OFFSET 24" )
    hyd = cur.fetchall()
    con.close
    return templates.TemplateResponse("hyd.html", {"request" : request,"hyd":hyd})

#flight page -f6 mumbai
@travel.get("/mumbai", response_class=HTMLResponse)
def mumbai(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(" SELECT * FROM Flight LIMIT 6 OFFSET 30" )
    mumbai = cur.fetchall()
    con.close
    return templates.TemplateResponse("mumbai.html", {"request" : request,"mumbai":mumbai})

#flight page -f7 delhi
@travel.get("/delhi", response_class=HTMLResponse)
def delhi(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(" SELECT * FROM Flight  LIMIT 6 OFFSET 36" )
    delhi = cur.fetchall()
    con.close
    return templates.TemplateResponse("delhi.html", {"request" : request,"delhi":delhi})

#flight page -f8 kolkata
@travel.get("/kolkata", response_class=HTMLResponse)
def kolkata(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(" SELECT * FROM Flight  LIMIT 6 OFFSET 42" )
    kolkata = cur.fetchall()
    con.close
    return templates.TemplateResponse("kolkata.html", {"request" : request,"kolkata":kolkata})

#flight page -f9 round trip
@travel.get("/Rt", response_class=HTMLResponse)
def Rt(request : Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(" SELECT * FROM Flight  LIMIT 6 OFFSET 48 " )
    rt = cur.fetchall()
    con.close
    return templates.TemplateResponse("Rt.html", {"request" : request,"rt":rt})

#flight page -flight info
@travel.get("/flight-info/{fid}", response_class=HTMLResponse)
def flight_info(request : Request,fid:int):
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    con = sqlite3.connect(DATABASE_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM Flight WHERE flight_id=?",[fid])
    finfo= cur.fetchall()
    con.close
    return templates.TemplateResponse("flight-info.html", {"request" : request,"fid":fid,"finfo":finfo[0]})

#flight page - flight cart
@travel.get("/fcart", response_class=HTMLResponse)
def fcart(request : Request,fid:str,fclass:str,depdate:str,seatnumber:str):
    user_id = request.session.get('user_id')
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    con = sqlite3.connect(DATABASE_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM Flight  WHERE flight_id=?", [fid])
    flight = cur.fetchall()
    cur.execute("SELECT * FROM Flight_class  WHERE class_id=?", [fclass])
    fclass = cur.fetchall()
    con.close 
    return templates.TemplateResponse("fcart.html", {"request" : request,"fid":fid,"depdate":depdate,"seatnumber":seatnumber,"fclass":fclass[0],"flight":flight[0]})


@travel.post("/fcart",response_class=HTMLResponse)
def post_fcart(request :Request,fid:str =Form(...),username : str = Form(...),email: str = Form(...),phone : str = Form(...),fno:str =Form(...),fname:str =Form(...),ffrom:str =Form(...),fto:str =Form(...),via:str =Form(...),route:str =Form(...),depdate:str =Form(...),deptime:str =Form(...),arrtime:str =Form(...),terminal:str =Form(...),fclass:str =Form(...),seatnumber:str =Form(...),totalprice:str =Form(...)):
    #database -> inserting or updating, can be done POST request
    with sqlite3.connect(DATABASE_NAME) as con:
        user_id = request.session.get('user_id')
        cur = con.cursor()
        con.row_factory = sqlite3.Row
        cur.execute("SELECT * from Flight f where f.flight_id=?", [fid])
        Flight = cur.fetchall()
        actual_seats = Flight[0][4]
        remaining_seats = int(actual_seats) - int(seatnumber)
        cur.execute("UPDATE Flight SET totalseats = ? where flight_id=?",[str(remaining_seats) ,fid])
        cur.execute("INSERT into Flightorders(user_id,username,email,phone,fno,fname,ffrom,fto,via,route,depdate,deptime,arrtime,terminal,fclass,seatno,totalprice) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (user_id,username, email,phone,fno,fname,ffrom,fto,via,route,depdate,deptime,arrtime,terminal,fclass,seatnumber,totalprice))
        emailsender.sendMail([email],"BOOKING SUCCESSFULL! \n" ,"DEAR  " +username + ", \n" + "You have succesfully booked your Flight! \n " 
        +"Please find the Details below \n" + "*******************************\n"+ "Flight Company:    " +fname +"\n" "Flight Number:    " +fno +"\n" 
        +"Flight Class:    " +fclass +"\n" "From:   " +ffrom +"\n" "To:   " +fto +"\n" "Via:    " 
        +via+"\n" +"Route:   "+route +"\n" +"Departure Date:   "+depdate +"\n"+"Departure Time:   "+deptime+"\n" +"Arrival Time:   " +arrtime+"\n" +"Terminal:    "+terminal+"\n" + "No. of Seats:  "+seatnumber +"\n" +"*******************************\n" + "THANKYOU \n" +"Regards, \n" +"Fourseasons")
        emailsender.sendMail([ADMIN_MAIL],"New Flight booking!" , "\n"+"Username:    " +username +"\n"+"Email:    "+email+"\n" +"Contact no. :   "+phone +"\n" +"Flight Company:    " +fname +"\n" "Flight Number:    " +fno +"\n" 
        +"Flight Class:    " +fclass +"\n" "From:   " +ffrom +"\n" "To:   " +fto +"\n" "Via:    " 
        +via+"\n" +"Route:   "+route +"\n" +"Departure Date:   "+depdate +"\n"+"Departure Time:   "+deptime+"\n" +"Arrival Time:   " +arrtime+"\n" +"Terminal:    "+terminal+"\n" + "No. of Seats:  "+seatnumber +"\n")
        con.commit()
    return RedirectResponse("/confirm",status_code=status.HTTP_302_FOUND)

#------------------------------------ADMIN HOME PAGE -------------------------------------------#

#admin page 
@travel.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Horders ")
    Hbookings = cur.fetchall()
    cur.execute("select * from Busorders ")
    Busbookings = cur.fetchall()
    cur.execute("select * from Flightorders ")
    Fbookings = cur.fetchall()
    con.close
    return templates.TemplateResponse("admin.html",{"request": request ,"Hbookings":Hbookings[0],"Busbookings":Busbookings[0],"Fbookings":Fbookings[0]})

@travel.get("/admin-logout", response_class=HTMLResponse)
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/lgn-admin", status_code=status.HTTP_302_FOUND)

#admin page - manage hotel bookings 
@travel.get("/mnageHb", response_class=HTMLResponse)
def mnageHb(request: Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Horders ")
    Hbookings = cur.fetchall()
    con.close
    return templates.TemplateResponse("mnageHb.html",{"request": request, "Hbookings":Hbookings})

#admin page - manage bus bookings 
@travel.get("/mngeBb", response_class=HTMLResponse)
def mngeBb(request: Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Busorders ")
    Busbookings = cur.fetchall()
    con.close
    return templates.TemplateResponse("mngeBb.html",{"request": request ,"Busbookings":Busbookings})

#admin page  -manage flight bookings
@travel.get("/mngeFb", response_class=HTMLResponse)
def mngeFb(request: Request):
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Flightorders ")
    Fbookings = cur.fetchall()
    con.close
    return templates.TemplateResponse("mngeFb.html",{"request": request,"Fbookings":Fbookings})

#admin page  -manage hotel staff 
@travel.get("/mnageHs", response_class=HTMLResponse)
def mnageHs(request: Request):
    con = sqlite3.connect(DATABASE_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Hotelstaff ")
    hstaff = cur.fetchall()
    con.close
    return templates.TemplateResponse("mnageHs.html",{"request": request ,"hstaff": hstaff})

#admin page  -manage Tour Guide 
@travel.get("/mnageTgd", response_class=HTMLResponse)
def mnageTgd(request: Request):
    con = sqlite3.connect(DATABASE_NAME)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Tourguide ")
    tguide = cur.fetchall()
    con.close
    return templates.TemplateResponse("mnageTgd.html",{"request": request ,"tguide":tguide})

#------------------------------------BOOKING CONFIRMATION--------------------------------------#

@travel.get("/confirm" ,response_class=HTMLResponse)
def confirm(request: Request):
    return templates.TemplateResponse("confirm.html", {"request":request})

#------------------------------------USER HOME PAGE -------------------------------------------#
#user home 
@travel.get("/user", response_class=HTMLResponse)
def user(request: Request):
    return templates.TemplateResponse("user.html",{"request": request})

#user page -  user bus bookings
@travel.get("/userbusbookings", response_class=HTMLResponse)
def userbusbookings(request: Request):
    user_id = request.session.get('user_id')
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Busorders where user_id=?", [user_id])
    Bbookings = cur.fetchall()
    con.close
    return templates.TemplateResponse("ubbk.html",{"request": request,"Bbookings":Bbookings})

#user page -  user flight bookings
@travel.get("/userflightbookings", response_class=HTMLResponse)
def userflightbookings(request: Request):
    user_id= request.session.get('user_id')
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Flightorders where user_id=?", [user_id])
    Fbookings = cur.fetchall()
    con.close
    return templates.TemplateResponse("ufbk.html",{"request": request,"Fbookings":Fbookings})

#user page -  user hotel bookings
@travel.get("/userhotelbookings", response_class=HTMLResponse)
def userhotelbookings2(request: Request):
    user_id = request.session.get('user_id')
    if not request.session.get('isLogin'):
        return RedirectResponse('/lgn-usr', status_code=status.HTTP_302_FOUND)
    con = sqlite3.connect("4seasons.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Horders  where user_id =?",[user_id])
    hbookings = cur.fetchall()
    con.close
    return templates.TemplateResponse("uhbk.html",{"request": request ,"hbookings":hbookings})

#------------------------------------JOIN US PAGE -------------------------------------------#

#joinus page -   hotel staff
@travel.get("/hotelmng", response_class=HTMLResponse)
def hotelmng(request: Request):
    return templates.TemplateResponse("hotelmng.html",{"request": request})

@travel.post("/hotelmng",response_class=HTMLResponse)
def post_hotelmng(request :Request,firstname : str = Form(...),lastname : str = Form(...),gender: str = Form(...), age : str = Form(...),state : str = Form(...),email: str = Form(...) ,availablepositions: str = Form(...),qualification : str = Form(...),experience : str = Form(...)):
    #database -> inserting or updating, can be done POST request
    with sqlite3.connect("4seasons.db") as con:
        cur = con.cursor()
        cur.execute("INSERT into Hotelstaff(hs_name,hs_gender,hs_age,hs_email,hs_state,hs_post,hs_qual,hs_exp) values(?,?,?,?,?,?,?,?)",
                    (firstname, gender,age,email,state,availablepositions,qualification, experience))
        con.commit()
        emailsender.sendMail([email, 'fourseasons.travel04@gmail.com'],"SUCCESSFULLY REGISTERED", "Dear," +firstname +"\n"+"You have Successfully registered for " +availablepositions +"post. We will further revert back to you." )
    return templates.TemplateResponse("hotelmng.html",{"request": request , "msg" : "You have successfully Registered. We will further contact you!"})

#joinus page -   tour guide
@travel.get("/tguide", response_class=HTMLResponse)
def tguide(request: Request):
    return templates.TemplateResponse("tguide.html",{"request": request})

@travel.post("/tguide",response_class=HTMLResponse)
def post_tguide(request :Request, firstname : str = Form(...),lastname : str = Form(...), gender : str = Form(...),age : str = Form(...),state : str = Form(...),email:  str = Form(...),qualification: str = Form(...),areaofexpertise  : str = Form(...), experience : str = Form(...)):
    #database -> inserting or updating, can be done POST request
    with sqlite3.connect("4seasons.db") as con:
        cur = con.cursor()
        cur.execute("INSERT into Tourguide(tg_name,tg_gender,tg_age,tg_state,tg_email,tg_qual,tg_arex,tg_exp) values(?,?,?,?,?,?,?,?)",
                    (firstname ,gender,age,state,email,qualification,areaofexpertise,experience))
        con.commit()
        emailsender.sendMail([email, 'fourseasons.travel04@gmail.com'],"SUCCESSFULLY REGISTERED", "Dear," +firstname +"\n" +"You have Successfully registered for TOUR GUIDE post. We will further revert back to you." )
    return templates.TemplateResponse("tguide.html",{"request": request , "msg" : "You have successfully Registered. We will further contact you!"})



