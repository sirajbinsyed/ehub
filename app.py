from unicodedata import category
from flask import Flask, render_template,request,session,redirect,flash,url_for
from config import Database

app = Flask(__name__)

app.secret_key = 'your_secret_key'
# Initialize Database
db = Database()

#Guest Block
@app.route("/")
def home():
    return render_template("guest/index.html")

@app.route("/index")
def index():
    return render_template("guest/index.html")

@app.route("/guest-aboutus")
def guestaboutus():
    return render_template("guest/about_us.html")

@app.route("/logout")
def logout():
    # Clear the session data
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    invalid = None
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Fetch user from the database
        query = f"SELECT * FROM tbl_login WHERE username = '{username}' and password='{password}'"
        user = db.fetchone(query)

        if user:
            session['user_id'] = user['id']
            # Verify the password
            if user['type']=='admin':
                flash("Login successful!", "success")
                return redirect(url_for('adminhome'))  
            elif user['type']=='user':
                flash("Login successful!", "success")
                return redirect(url_for('userhome'))
            elif user['type']=='company':
                flash("Login successful!", "success")
                return redirect(url_for('companyhome'))
            else:
                flash("Invalid username or password.", "danger")
            
        else:
            flash("User not found.", "danger")
            invalid = 'true'

    return render_template("guest/login.html", invalid=invalid)

@app.route("/user-registration", methods=["GET", "POST"])
def userreg():
    if request.method == "POST":
        # Get form data
        name = request.form['name']
        age = request.form['age']
        details = request.form['details']
        username = request.form['username']
        password = request.form['password']
        

        try:
            # Insert into tbl_login
            insert_login_query = f"""
            INSERT INTO tbl_login (username, password, type) 
            VALUES ('{username}', '{password}', 'user')
            """
            db.single_insert(insert_login_query)

            # Retrieve the login ID
            get_login_id_query = f"SELECT id FROM tbl_login WHERE username = '{username}'"
            login_record = db.fetchone(get_login_id_query)
            login_id = login_record['id']

            # Insert into registration table
            insert_registration_query = f"""
            INSERT INTO tbl_user (login_id, name, details, age) 
            VALUES ({login_id}, '{name}', '{details}', {age})
            """
            print(insert_registration_query)
            db.single_insert(insert_registration_query)

            flash("Registration successful!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "danger")

    return render_template("guest/user-reg.html")

@app.route("/company-registration", methods=["GET", "POST"])
def companyreg():
    if request.method == "POST":
        # Get form data
        name = request.form['name']
        phone = request.form['phone']
        gmail = request.form['gmail']
        license = request.form['license']
        address = request.form['address']
        details = request.form['details']
        username = request.form['username']
        password = request.form['password']
        location = request.form['location']
        

        try:
            # Insert into tbl_login
            insert_login_query = f"""
            INSERT INTO tbl_login (username, password, type) 
            VALUES ('{username}', '{password}', 'company')
            """
            db.single_insert(insert_login_query)

            # Retrieve the login ID
            get_login_id_query = f"SELECT id FROM tbl_login WHERE username = '{username}'"
            login_record = db.fetchone(get_login_id_query)
            login_id = login_record['id']

            # Insert into registration table
            insert_registration_query = f"""
            INSERT INTO tbl_company (login_id, name, address, phone_no, gmail, license, details, location_id) 
            VALUES ({login_id}, '{name}', '{address}', {phone}, '{gmail}', '{license}', '{details}', {location})
            """
            print(insert_registration_query)
            db.single_insert(insert_registration_query)

            flash("Registration successful!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "danger")

    locations = db.fetchall("SELECT * FROM tbl_location")
    return render_template("guest/company-reg.html",locations=locations)

    


#admin Block

@app.route("/admin-home")
def adminhome():
    counts=None
    try:
        query = """
        SELECT 
            (SELECT COUNT(*) FROM tbl_user) AS user_count,
            (SELECT COUNT(*) FROM tbl_company) AS company_count,
            (SELECT COUNT(*) FROM booking) AS booking_count
        """
        
        # Execute the query
        counts = db.fetchall(query)
    except Exception as e:
                print(f"execption 1234{e}")
                flash(f"Failed to add product: {str(e)}", "danger")
    return render_template("admin/index.html", counts=counts)

@app.route("/admin-category", methods=["GET", "POST"])
def admincategory():
    if request.method == "POST":
        category_id = request.form.get('category_id')
        category_name = request.form['category']
        details = request.form['details']

        if category_id:  # Update operation
            try:
                update_category_query = f"""
                UPDATE tbl_category 
                SET name = '{category_name}', details = '{details}'
                WHERE id = {category_id}
                """
                db.execute(update_category_query)
                flash("Category updated successfully!", "success")
            except Exception as e:
                flash(f"Failed to update category: {str(e)}", "danger")
        else:  # Create operation
            try:
                insert_category_query = f"""
                INSERT INTO tbl_category (name, details) 
                VALUES ('{category_name}', '{details}')
                """
                db.single_insert(insert_category_query)
                flash("Category added successfully!", "success")
            except Exception as e:
                flash(f"Failed to add category: {str(e)}", "danger")
        
        return redirect(url_for('admincategory'))

    # Fetch all categories and the category to edit (if any)
    categories = db.fetchall("SELECT * FROM tbl_category")
    category_to_edit = None
    if 'edit' in request.args:
        category_id = request.args.get('edit')
        category_to_edit = db.fetchone(f"SELECT * FROM tbl_category WHERE id = {category_id}")
    
    return render_template("admin/category.html", categories=categories, category_to_edit=category_to_edit)

@app.route("/delete-category/<int:category_id>", methods=["POST"])
def delete_category(category_id):
    try:
        delete_query = f"DELETE FROM tbl_category WHERE id = {category_id}"
        db.execute(delete_query)
        flash("Category deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete category: {str(e)}", "danger")
    
    return redirect(url_for('admincategory'))

@app.route("/admin-location", methods=["GET", "POST"])
def adminlocation():
    if request.method == "POST":
        location_id = request.form.get('location_id')
        name = request.form['name']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        if location_id:  # Update operation
            try:
                update_location_query = f"""
                UPDATE tbl_location 
                SET name = '{name}', latitude = '{latitude}', longitude = '{longitude}'
                WHERE id = {location_id}
                """
                db.execute(update_location_query)
                flash("Location updated successfully!", "success")
            except Exception as e:
                flash(f"Failed to update location: {str(e)}", "danger")
        else:  # Create operation
            try:
                insert_location_query = f"""
                INSERT INTO tbl_location (name, latitude, longitude) 
                VALUES ('{name}', '{latitude}', '{longitude}')
                """
                db.single_insert(insert_location_query)
                flash("Location added successfully!", "success")
            except Exception as e:
                flash(f"Failed to add location: {str(e)}", "danger")
        
        return redirect(url_for('adminlocation'))

    # Fetch all locations and the location to edit (if any)
    locations = db.fetchall("SELECT * FROM tbl_location")
    location_to_edit = None
    if 'edit' in request.args:
        location_id = request.args.get('edit')
        location_to_edit = db.fetchone(f"SELECT * FROM tbl_location WHERE id = {location_id}")
    
    return render_template("admin/location.html", locations=locations, location_to_edit=location_to_edit)

@app.route("/delete-location/<int:location_id>", methods=["POST"])
def delete_location(location_id):
    try:
        delete_query = f"DELETE FROM tbl_location WHERE id = {location_id}"
        db.execute(delete_query)
        flash("Location deleted successfully!", "success")
    except Exception as e:
        flash(f"Failed to delete location: {str(e)}", "danger")
    
    return redirect(url_for('adminlocation'))

@app.route("/admin-companies", methods=["GET", "POST"])
def admin_companies():
    for_page = None
    search = request.args.get('search')
    print(f"this is search:{search}")
    for_page = request.args.get('page')

    if search:   
         companies = db.fetchall(f"""
                        SELECT tbl_company.*, tbl_location.name AS location_name
                        FROM tbl_company
                        LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
                        WHERE tbl_company.location_id={search}  
                    """)
    else:
        companies = db.fetchall(f"""
                            SELECT tbl_company.*, tbl_location.name AS location_name
                            FROM tbl_company
                            LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
                        """)
    locations =  db.fetchall("""SELECT * FROM tbl_location""")
    print(f"this is bookings :{companies}")
    return render_template("admin/companies.html", companies=companies, locations=locations, for_page=for_page)

@app.route("/admin-company-review", methods=["GET", "POST"])
def admin_company_review():
    company_id = request.args.get('company_id')
    reviews = None
    if company_id:
         company = db.fetchall(f"""
                    SELECT tbl_company.*, tbl_location.name AS location_name
                    FROM tbl_company
                    LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
                    WHERE tbl_company.id= {company_id}
                """)
         reviews = db.fetchall(f"""
                    SELECT rating.*, tbl_user.name AS user_name
                    FROM rating
                    LEFT JOIN tbl_user ON tbl_user.login_id = rating.user_id
                    WHERE rating.company_id= {company_id}
                """)

   
    print(f"this is bookings :{company}")
    print(f"this is reviews:{reviews}")
    return render_template("admin/reviews.html", company=company, reviews=reviews)

@app.route("/admin-company-pickups", methods=["GET", "POST"])
def admin_company_pickups():
    company_id = request.args.get('company_id')
    pickups = None
    if company_id:
        try:
            company = db.fetchall(f"""
                        SELECT tbl_company.*, tbl_location.name AS location_name
                        FROM tbl_company
                        LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
                        WHERE tbl_company.id= {company_id}
                    """)
            pickups = db.fetchall(f"""
                        SELECT pickup.*, tbl_user.name AS user_name
                        FROM pickup
                        LEFT JOIN tbl_user ON tbl_user.login_id = pickup.user_id
                        WHERE pickup.company_id= {company_id}
                    """)
        except Exception as e:
                print(f"execption 1234{e}")
                flash(f"Failed to add product: {str(e)}", "danger")
   
    print(f"this is bookings :{company}")
    print(f"this is pickups:{pickups}")
    return render_template("admin/pickups.html", company=company, pickups=pickups)

@app.route("/admin-company-bookings", methods=["GET", "POST"])
def admin_company_bookings():
    company_id = request.args.get('company_id')
    bookings = None
    if company_id:
        try:
            company = db.fetchall(f"""
                        SELECT tbl_company.*, tbl_location.name AS location_name
                        FROM tbl_company
                        LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
                        WHERE tbl_company.id= {company_id}
                    """)
            bookings = db.fetchall(f"""
                        SELECT booking.*, tbl_user.name AS user_name
                        FROM booking
                        LEFT JOIN tbl_user ON tbl_user.login_id = booking.user_id
                        WHERE booking.company_id= {company_id}
                    """)
        except Exception as e:
                print(f"execption 1234{e}")
                flash(f"Failed to add product: {str(e)}", "danger")
   
    print(f"this is bookings :{company}")
    print(f"this is bookings:{bookings}")
    return render_template("admin/bookings.html", company=company, bookings=bookings)


@app.route("/admin-users", methods=["GET", "POST"])
def admin_users():
    # search = request.args.get('search')
    # if search:   
    #      companies = db.fetchall(f"""
    #                     SELECT tbl_company.*, tbl_location.name AS location_name
    #                     FROM tbl_company
    #                     LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
    #                     WHERE tbl_company.location_id={search}
    #                 """)
    users = db.fetchall(f"""
                        SELECT * FROM tbl_user 
                    """)
    
    print(f"this is users :{users}")
    return render_template("admin/users.html", users=users)


#user section
@app.route("/user-home")
def userhome():
    counts=None
    try:
        query = """
        SELECT 
            (SELECT COUNT(*) FROM tbl_location) AS location_count,
            (SELECT COUNT(*) FROM tbl_company) AS company_count,
            (SELECT COUNT(*) FROM slot) AS slot_count
        """
        
        # Execute the query
        counts = db.fetchall(query)
    except Exception as e:
                print(f"execption 1234{e}")
                flash(f"Failed to add product: {str(e)}", "danger")
    
    print(f"{counts}")
    return render_template("user/index.html", counts = counts)

@app.route("/user-aboutus")
def useraboutus():
    return render_template("user/about_us.html")

@app.route("/select-company", methods=["GET", "POST"])
def select_company():
    search = request.args.get('search')
    if search:   
         companies = db.fetchall(f"""
            SELECT tbl_company.*, tbl_location.name AS location_name
            FROM tbl_company
            LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
            WHERE tbl_company.location_id = {search}
        """)
                            
    else:
        # Fetch all products
        companies = db.fetchall("""
            SELECT tbl_company.*, tbl_location.name AS location_name
            FROM tbl_company
            LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
        """)
    locations =  db.fetchall("""SELECT * FROM tbl_location""")
    print(f"this is companies :{companies}")
    print(f"this is locations :{locations}")
    return render_template("user/select_company.html", companies=companies, locations=locations)

@app.route("/select-slot", methods=["GET", "POST"])
def select_slot():
    company_id= request.args.get('company_id')
    print(f"companyId:{company_id}")
    slots = db.fetchall(f""" SELECT * FROM slot WHERE company_id={company_id}""")   
    print(f"this is slots :{slots}")
    return render_template("user/select_slot.html", slots=slots)

#admin manage products
@app.route("/book-slot", methods=["GET", "POST"])
def book_slot():
    if request.method == "POST":
        user_id = session.get('user_id')
        slot_num = request.form['slot_num']
        company_id = request.form['company_id']
        category_id = request.form['category_id']
        time = request.form['time']
        slot_id = request.form['slot_id'] 
        location =request.form['location']      
        print(f"company ID:{company_id}")
        print(f"slot ID:{slot_id}")
        print(f"slot NUm:{slot_num}")
        print(f"time:{time}")
        print(f"category ID :{category_id}")
        print(f"user_id:{user_id}")
        try:
                update_slot_query = f"""
                UPDATE slot 
                SET status = 'Booked'
                WHERE slot_id = {slot_id}
                """  
                db.execute(update_slot_query)
                insert_booking_query = f"""
                    INSERT INTO booking (slot_no,slot_id,time,location,user_id,category_id,status,date,company_id)
                    VALUES ({slot_num}, '{slot_id}', '{time}', '{location}', {user_id}, {category_id},'booked',NOW(),{company_id})
                """
                db.single_insert(insert_booking_query)
                flash("slot booked successfully!", "success")
        except Exception as e:
                print(f"execption 1234{e}")
                flash(f"Failed to add product: {str(e)}", "danger")
        return redirect(url_for('show_my_bookings'))

    else:  
        slot_id = request.args.get('slot_id')
        slot_details = db.fetchall(f"""
                    SELECT slot.*, tbl_location.name AS location_name
                    FROM slot
                    LEFT JOIN tbl_company ON tbl_company.id = slot.company_id
                    LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
                    WHERE slot.slot_id= {slot_id}
                """)
        catagory =  db.fetchall("""SELECT * FROM tbl_category""")
        print(f"this is slot details :{slot_details}")
        print(f"this is category :{catagory}")
    return render_template("user/book_slot.html",slot_details=slot_details, catagory=catagory)

@app.route("/pickup", methods=["GET", "POST"])
def pickup():
    try:
        company_details=None
        company_id = request.args.get('company_id')
        company = db.fetchone(f"""SELECT * FROM tbl_company WHERE id = {company_id}""")
        categories =  db.fetchall("""SELECT * FROM tbl_category""")
        print(f"this is category :{categories}")
        print(f"this is company :{company}")

    except Exception as e:
                print(f"execption 1234{e}")
                flash(f"Failed to add product: {str(e)}", "danger")
    return render_template("user/create_pickup.html", company=company, categories=categories)

@app.route("/create-pickup", methods=["GET", "POST"])
def create_pickup():
    user_id = session.get('user_id')
    if request.method == "POST":
        user_id = session.get('user_id')
        company_id = request.form['company_id']
        category_id = request.form['category_id']
        location =request.form['location'] 
        land_mark = request.form['land_mark']
        contact = request.form['contact']
        print(f"company ID:{company_id}")
        print(f"land mark:{land_mark}")
        print(f"category ID :{category_id}")
        print(f"user_id:{user_id}")
        try:
                insert_pickup_query = f"""
                    INSERT INTO pickup (user_id,category_id,status,company_id,location,landmark,contact,time)
                    VALUES ({user_id}, {category_id},'booked',{company_id},'{location}','{land_mark}','{contact}',NOW())
                """
                db.single_insert(insert_pickup_query)
                flash("pickup booked successfully!", "success")
        except Exception as e:
                print(f"execption 1234{e}")
                flash(f"Failed to add product: {str(e)}", "danger")
        return redirect(url_for('create_pickup'))

    else:
    
        pickup_details = db.fetchall(f"""
                    SELECT pickup.*, tbl_location.name AS company_location, tbl_company.*, tbl_category.name AS category_name, pickup.status AS pickup_status
                    FROM pickup
                    LEFT JOIN tbl_company ON tbl_company.id = pickup.company_id
                    LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
                    LEFT JOIN tbl_category ON tbl_category.id = pickup.category_id
                    WHERE pickup.user_id= {user_id}
                """)
        
        print(f"this is slot details :{pickup_details}")
      
    return render_template("user/my_pickups.html",pickup_details=pickup_details)

@app.route("/show-my-bookings", methods=["GET", "POST"])
def show_my_bookings():
    user_id = session.get('user_id')
    bookings = db.fetchall(f"""
                SELECT 
                    booking.*, 
                    slot.slot, 
                    tbl_category.name AS category_name,
                    tbl_company.name AS company_name,
                    tbl_company.address AS company_address
                FROM booking
                LEFT JOIN slot ON booking.slot_id = slot.slot_id
                LEFT JOIN tbl_category ON booking.category_id = tbl_category.id
                LEFT JOIN tbl_company ON slot.company_id = tbl_company.id
                WHERE booking.user_id = {user_id}
                ORDER BY booking.booking_id DESC
            """)  
    print(f"this is bookings :{bookings}")
    return render_template("user/my_bookings.html", bookings=bookings)

@app.route("/review-company", methods=["GET", "POST"])
def review_company():
    search = request.args.get('search')
    if search:   
         companies = db.fetchall(f"""
            SELECT tbl_company.*, tbl_location.name AS location_name
            FROM tbl_company
            LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
            WHERE tbl_company.location_id = {search}
        """)
                            
    else:
        # Fetch all products
        companies = db.fetchall("""
            SELECT tbl_company.*, tbl_location.name AS location_name
            FROM tbl_company
            LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
        """)
    locations =  db.fetchall("""SELECT * FROM tbl_location""")
    print(f"this is companies :{companies}")
    print(f"this is locations :{locations}")
    return render_template("user/review_company.html", companies=companies, locations=locations)

@app.route("/send_review", methods=["GET", "POST"])
def send_review():
    if request.method == "POST":
        user_id = session.get('user_id')
        booking_id = request.form['booking_id']
        rating = request.form['rating']
        command = request.form['command']
        company_id =request.form['company_id']
        print(f"rating:{rating}")
        print(f"booking_id:{booking_id}")
        print(f"command:{command}")
        print(f"company ID:{company_id}")
        print(f"user_id:{user_id}")
        try:
                insert_review_query = f"""
                        INSERT INTO rating (user_id, company_id, booking_id, ratings, command, date)
                        VALUES ({user_id}, {company_id}, {booking_id}, {rating}, '{command}', NOW())
                    """
                db.single_insert(insert_review_query)
                flash("reviewed successfully!", "success")
        except Exception as e:
                print(f"execption 1234{e}")
                flash(f"Failed to add product: {str(e)}", "danger")
        return redirect(url_for('show_my_bookings'))

    else:  
        company_id = request.args.get('company_id')
        company_details = db.fetchall(f"""
                    SELECT tbl_company.*, tbl_location.name AS location_name
                    FROM tbl_company
                    LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
                    WHERE tbl_company.id= {company_id}
                """)
        catagory =  db.fetchall("""SELECT * FROM tbl_category""")
        print(f"this is slot details :{company_details}")
        print(f"this is category :{catagory}")
        return render_template("user/send_review.html", company_details=company_details, catagory=catagory)

@app.route("/view-companies", methods=["GET", "POST"])
def view_companies():
    companies = db.fetchall(f"""
                        SELECT tbl_company.*, tbl_location.name AS location_name
                        FROM tbl_company
                        LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
                    """)
    locations =  db.fetchall("""SELECT * FROM tbl_location""")
    print(f"this is bookings :{companies}")
    return render_template("user/view_companies.html", companies=companies, locations=locations)


@app.route("/view-company-review", methods=["GET", "POST"])
def view_company_review():
    company_id = request.args.get('company_id')
    reviews = None
    if company_id:
         company = db.fetchall(f"""
                    SELECT tbl_company.*, tbl_location.name AS location_name
                    FROM tbl_company
                    LEFT JOIN tbl_location ON tbl_company.location_id = tbl_location.id
                    WHERE tbl_company.id= {company_id}
                """)
         reviews = db.fetchall(f"""
                    SELECT rating.*, tbl_user.name AS user_name
                    FROM rating
                    LEFT JOIN tbl_user ON tbl_user.login_id = rating.user_id
                    WHERE rating.company_id= {company_id}
                """)

   
    print(f"this is bookings :{company}")
    print(f"this is reviews:{reviews}")
    return render_template("user/show_reviews.html", company=company, reviews=reviews)

#company section
@app.route("/company-home")
def companyhome():
    user_id = session.get('user_id')
    company = db.fetchone(f""" SELECT * FROM tbl_company WHERE login_id={user_id}""")
    if company:
        company_id = company['id']  
    else:
        company_id = None  
    counts=None
    try:
        query = f"""
        SELECT 
            (SELECT COUNT(*) FROM pickup WHERE company_id={company_id}) AS pickup_count,
            (SELECT COUNT(*) FROM booking WHERE company_id={company_id}) AS booking_count,
            (SELECT COUNT(*) FROM rating WHERE company_id={company_id}) AS rating_count
        """
        
        # Execute the query
        counts = db.fetchall(query)
    except Exception as e:
                print(f"execption 1234{e}")
                flash(f"Failed to add product: {str(e)}", "danger")
    return render_template("company/index.html", counts=counts)

#company manage products
@app.route("/allocate-slot", methods=["GET", "POST"])
def allocateslot():
    if request.method == "POST":
        user_id = session.get('user_id')
        company = db.fetchone(f""" SELECT * FROM tbl_company WHERE login_id={user_id}""")
        if company:
            company_id = company['id']  
        else:
            company_id = None  

        slot_id = request.form.get('slot_id')
        slot_num = request.form['slot_num']
        offers= request.form['offers']
        # category_id = request.form['category_id']
        unit_price = request.form['unit_price']
        
        print(f"company ID:{company_id}")
        print(f"slot ID:{slot_id}")
        print(f"slot NUm:{slot_num}")
        print(f"offers:{offers}")
        
        if slot_id:  # Update operation
            try:
                update_slot_query = f"""
                UPDATE slot 
                SET offers = '{offers}', 
                    slot = {slot_num},
                    unit_price = '{unit_price}'
                WHERE slot_id = {slot_id}
                """
               
                db.execute(update_slot_query)
                flash("slot updated successfully!", "success")
            except Exception as e:
                print(f"exeption:{e}")
                flash(f"Failed to update product: {str(e)}", "danger")
        else:  # Create operation
            try:
                insert_slot_query = f"""
                    INSERT INTO slot (slot, unit_price, status, offers, company_id)
                    VALUES ({slot_num}, '{unit_price}', 'Available', '{offers}', {company_id})
                """
                db.single_insert(insert_slot_query)
                flash("slot added successfully!", "success")
            except Exception as e:
                print(f"execption{e}")
                flash(f"Failed to add product: {str(e)}", "danger")
        
        return redirect(url_for('allocateslot'))
    user_id = session.get('user_id')
    company = db.fetchone(f""" SELECT * FROM tbl_company WHERE login_id={user_id}""")
    if company:
            company_id = company['id']  
    else:
            company_id = None
    # Fetch all products
    slots = db.fetchall(f""" SELECT * FROM slot WHERE company_id={company_id}""")


    slot_to_edit = None
    if 'edit' in request.args:
        slot_id = request.args.get('edit')
        print(f"slot to edit :{slot_id}")
        slot_to_edit = db.fetchone(f"""
        SELECT * FROM slot
        WHERE slot_id = {slot_id}
        """)

    print(f"slot to edit:{slot_to_edit}")
        
    return render_template("company/allocate_slot.html", slots=slots, slot_to_edit=slot_to_edit)

@app.route("/delete-slot", methods=["POST"])
def delete_slot():
    try:
        slot_id = request.args.get('slot_id')
        print(f"Slot ID :{slot_id}")
        delete_query = f"DELETE FROM slot WHERE slot_id = {slot_id}"
        db.execute(delete_query)
        print(f"Slot Deleted")
    except Exception as e:
        flash(f"Failed to delete location: {str(e)}", "danger")
        print(f"Slot Deleted  {e}")
    
    return redirect(url_for('allocateslot'))

@app.route("/available-slots", methods=["GET", "POST"])
def available_slots():
    user_id = session.get('user_id')
    company = db.fetchone(f""" SELECT * FROM tbl_company WHERE login_id={user_id}""")
    if company:
            company_id = company['id']  
    else:
            company_id = None
    # Fetch all products
    slots = db.fetchall(f""" SELECT * FROM slot WHERE company_id={company_id} AND status='Available'""")
    return render_template("company/available_slots.html", slots=slots)

@app.route("/company-bookings", methods=["GET", "POST"])
def company_bookings():
    date = request.args.get('date')
    user_id = session.get('user_id')
    company = db.fetchone(f""" SELECT * FROM tbl_company WHERE login_id={user_id}""")
    if company:
        company_id = company['id']  
    else:
        company_id = None  

    print(f"this is company ID{company_id}")
    
    print(f"this is date :{date}")
        
    if date:
        
        bookings = db.fetchall(f"""
                    SELECT booking.*, tbl_user.name AS user_name
                    FROM booking
                    LEFT JOIN slot ON slot.slot_id = booking.slot_id
                    LEFT JOIN tbl_user ON tbl_user.login_id = booking.user_id
                    WHERE booking.company_id= {company_id} AND booking.date='{date}' AND booking.status = 'booked'
                """)
    else:
        bookings = db.fetchall(f"""
                    SELECT booking.*, tbl_user.name AS user_name ,slot.company_id AS company_id
                    FROM booking
                    LEFT JOIN slot ON slot.slot_id = booking.slot_id
                    LEFT JOIN tbl_user ON tbl_user.login_id = booking.user_id
                    WHERE booking.company_id= {company_id}  AND booking.status = 'booked'
                """)


    print(f"this is reviews:{bookings}")
    return render_template("company/company_bookings.html", bookings=bookings)

@app.route("/close-booking", methods=["GET","POST"])
def close_booking():
    try:
        booking_id = request.args.get('booking_id')
        slot_id = request.args.get('slot_id')
        print(f"booking ID :{booking_id}")
        print(f"slot ID :{slot_id}")
        update_booking_query = f"UPDATE booking SET status='closed' WHERE booking_id = {booking_id}"
        db.execute(update_booking_query)
        update_slot_query =  f"UPDATE slot SET status='Available' WHERE slot_id = {slot_id}"
        db.execute(update_slot_query)
        print(f"updated")
    except Exception as e:
        flash(f"Failed to delete location: {str(e)}", "danger")
        print(f"updated {e}")
    return redirect(url_for('company_bookings'))


@app.route("/closed-company-bookings", methods=["GET", "POST"])
def ongoing_company_bookings():
    date = request.args.get('date')
    user_id = session.get('user_id')
    company = db.fetchone(f""" SELECT * FROM tbl_company WHERE login_id={user_id}""")
    if company:
        company_id = company['id']  
    else:
        company_id = None  

    print(f"this is company ID{company_id}")
    
    print(f"this is date :{date}")
        
    if date:
        
        bookings = db.fetchall(f"""
                    SELECT booking.*, tbl_user.name AS user_name
                    FROM booking
                    LEFT JOIN slot ON slot.slot_id = booking.slot_id
                    LEFT JOIN tbl_user ON tbl_user.login_id = booking.user_id
                    WHERE booking.company_id= {company_id} AND booking.date='{date}' AND booking.status = 'closed'
                """)
    else:
        bookings = db.fetchall(f"""
                    SELECT booking.*, tbl_user.name AS user_name ,slot.company_id AS company_id
                    FROM booking
                    LEFT JOIN slot ON slot.slot_id = booking.slot_id
                    LEFT JOIN tbl_user ON tbl_user.login_id = booking.user_id
                    WHERE booking.company_id= {company_id}  AND booking.status = 'closed'
                """)


    print(f"this is reviews:{bookings}")
    return render_template("company/closed_bookings.html", bookings=bookings)
    

@app.route("/company-reviews", methods=["GET", "POST"])
def company_reviews():
    user_id = session.get('user_id')
    company = db.fetchone(f""" SELECT * FROM tbl_company WHERE login_id={user_id}""")
    if company:
        company_id = company['id']  
    else:
        company_id = None  

    print(f"this is company ID{company_id}")
    reviews = None
    if company_id:
         reviews = db.fetchall(f"""
                    SELECT rating.*, tbl_user.name AS user_name
                    FROM rating
                    LEFT JOIN tbl_user ON tbl_user.login_id = rating.user_id
                    WHERE rating.company_id= {company_id}
                """)

   
    print(f"this is reviews:{reviews}")
    return render_template("company/company_reviews.html", reviews=reviews)


@app.route("/new-pickups", methods=["GET", "POST"])
def new_pickups():
    attend_pickup_id = request.args.get('attend_pickup_id')
    cancel_pickup_id = request.args.get('cancel_pickup_id')
    login_id = session.get('user_id')
    company = db.fetchone(f"""SELECT * FROM tbl_company WHERE login_id={login_id}""")
    if company:
        company_id = company['id']  
    else:
        company_id = None  

    print(f"this is company ID{company_id}")
    
    if attend_pickup_id:
        query= f"""UPDATE pickup SET status='attended' WHERE pickup_id = {attend_pickup_id}"""
        db.execute(query)

    elif cancel_pickup_id:
        query= f"""UPDATE pickup SET status='canceled' WHERE pickup_id = {cancel_pickup_id}"""
        db.execute(query)
    
    try:
        pickups = db.fetchall(f"""
                        SELECT pickup.*, tbl_user.name AS user_name , tbl_category.name AS category_name
                        FROM pickup
                        LEFT JOIN tbl_user ON tbl_user.login_id = pickup.user_id
                        LEFT JOIN tbl_category ON tbl_category.id = pickup.category_id
                        WHERE pickup.company_id= {company_id}  AND pickup.status = 'booked'
                    """)
    except Exception as e:
        flash(f"Failed to delete location: {str(e)}", "danger")
        print(f"updated {e}")

    print(f"this is reviews:{pickups}")
    return render_template("company/new_pickups.html", pickups=pickups)

@app.route("/confirmed-pickups", methods=["GET", "POST"])
def confirmed_pickups():
    pickup_id = request.args.get('pickup_id')
    login_id = session.get('user_id')
    company = db.fetchone(f"""SELECT * FROM tbl_company WHERE login_id={login_id}""")
    if company:
        company_id = company['id']  
    else:
        company_id = None  

    print(f"this is company ID{company_id}")
    
    if pickup_id:
        query= f"""UPDATE pickup SET status='closed' WHERE pickup_id = {pickup_id}"""
        db.execute(query)
    
    try:
        pickups = db.fetchall(f"""
                        SELECT pickup.*, tbl_user.name AS user_name , tbl_category.name AS category_name
                        FROM pickup
                        LEFT JOIN tbl_user ON tbl_user.login_id = pickup.user_id
                        LEFT JOIN tbl_category ON tbl_category.id = pickup.category_id
                        WHERE pickup.company_id= {company_id}  AND pickup.status = 'attended'
                    """)
    except Exception as e:
        flash(f"Failed to delete location: {str(e)}", "danger")
        print(f"updated {e}")

    print(f"this is reviews:{pickups}")
    return render_template("company/confirmed_pickups.html", pickups=pickups)

@app.route("/closed-pickups", methods=["GET", "POST"])
def closed_pickups():
    canceled = request.args.get('canceled')
    login_id = session.get('user_id')
    company = db.fetchone(f"""SELECT * FROM tbl_company WHERE login_id={login_id}""")
    if company:
        company_id = company['id']  
    else:
        company_id = None  

    print(f"this is company ID{company_id}")
    if canceled:
        try:
            pickups = db.fetchall(f"""
                            SELECT pickup.*, tbl_user.name AS user_name , tbl_category.name AS category_name
                            FROM pickup
                            LEFT JOIN tbl_user ON tbl_user.login_id = pickup.user_id
                            LEFT JOIN tbl_category ON tbl_category.id = pickup.category_id
                            WHERE pickup.company_id= {company_id}  AND pickup.status = 'canceled'
                        """)
        except Exception as e:
            flash(f"Failed to delete location: {str(e)}", "danger")
            print(f"updated {e}")
    else:
        try:
            pickups = db.fetchall(f"""
                            SELECT pickup.*, tbl_user.name AS user_name , tbl_category.name AS category_name
                            FROM pickup
                            LEFT JOIN tbl_user ON tbl_user.login_id = pickup.user_id
                            LEFT JOIN tbl_category ON tbl_category.id = pickup.category_id
                            WHERE pickup.company_id= {company_id}  AND pickup.status = 'closed'
                        """)
        except Exception as e:
            flash(f"Failed to delete location: {str(e)}", "danger")
            print(f"updated {e}")

    print(f"this is reviews:{pickups}")
    return render_template("company/closed_pickups.html", pickups=pickups)


# running application 
if __name__ == '__main__': 
    app.run(debug=True) 