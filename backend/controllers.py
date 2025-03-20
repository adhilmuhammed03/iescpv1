from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from flask import current_app as app
from backend.models import Users, Campaign, db,AdRequest,Flagged
from dateutil import parser
from sqlalchemy import or_
import backend.init_db
app.secret_key = 'iescp'

@app.route("/admin_dashboard")
def admin_dashboard():
    if 'user' in session:
        usr = session['user']
        if usr['role'] == 0:
            campaigns = Campaign.query.all()
            flagged = Flagged.query.all()
            flagged_campaigns = []
            flagged_users = []
            for item in flagged:
                if item.user_or_campaign == 0:
                    result = fetch_flagged_campaings(item.flagged_id)
                    flagged_campaigns.append(result)
                else:
                    result = fetch_flagged_users(item.flagged_id)
                    flagged_users.append(result)
            return render_template("admin_dashboard.html",usr=usr,campaigns=campaigns,flagged_users=flagged_users,
                                   flagged_campaigns=flagged_campaigns)
    return "<h1>Unauthorized Access</h1>"

@app.route("/influencer_dashboard")
def influencer_dashboard():
    if 'user' in session:
        usr = session['user']
        if usr['role'] == 1:
            campaigns = fetch_private_campaigns(usr['user_id'])
            incoming_requests = fetch_ad_requests_by_target(usr['user_id'])
            outgoing_requests = fetch_ad_requests_by_source(usr['user_id'])
            ad_request_details = fetch_ad_requests_details()
            completed = fetch_completed_ad_requests(usr['user_id'])
            targets = fetch_target_details()
            sources = fetch_source_details()
            personal_info = fetch_influencer_details(usr['user_id'])
            return render_template("influencer_dashboard.html", Influencer=usr,
                                   campaigns=campaigns,
                                   incoming_requests=incoming_requests,
                                   outgoing_requests=outgoing_requests,ad=ad_request_details,
                                   targets=targets,info=personal_info,sources=sources,
                                   completed=completed)
    return "<h1>Unauthorized Access</h1>"
def fetch_influencer_details(user_id):
    personal_info = Users.query.filter_by(user_id=user_id).first()
    return personal_info

@app.route("/sponsor_dashboard")
def sponsor_dashboard():
    if 'user' in session:
        usr = session['user']
        if usr['role'] == 2:
            campaigns = fetch_sponsor_campaigns(usr['user_id'])
            incoming_requests = fetch_ad_requests_by_target(usr['user_id'])
            outgoing_requests = fetch_ad_requests_by_source(usr['user_id'])
            ad_request_details = fetch_ad_requests_details()
            targets = fetch_target_details()
            sources = fetch_source_details()
            return render_template("sponsor_dashboard.html", campaigns=campaigns, usr=usr,
                                   incoming_requests=incoming_requests,
                                   outgoing_requests=outgoing_requests,ad=ad_request_details,
                                   targets=targets,sources=sources)
    return "<h1>Unauthorized Access</h1>"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        pwd = request.form.get("pwd")
        usr = Users.query.filter_by(email=email, password=pwd).first()
        if usr:
            session['user'] = {'user_id': usr.user_id, 'role': usr.role, 'name': usr.name, 'email': usr.email}
            if usr.role == 0:
                return redirect(url_for("admin_dashboard"))
            elif usr.role == 1:
                return redirect(url_for("influencer_dashboard"))
            elif usr.role == 2:
                return redirect(url_for("sponsor_dashboard"))
        else:
            flash("Invalid Credentials")
            return render_template("login.html", msg="Invalid Credentials")
    return render_template("login.html", msg="")

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        role = request.form["role"]
        uname = request.form.get("Uname")
        email = request.form.get("email")
        pwd = request.form.get("pwd")
        usr = Users.query.filter_by(email=email).first()
        if not usr:
            role_num = 1 if role.lower() == 'influencer' else 2
            new_user = Users(name=uname, email=email, password=pwd, role=role_num)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', msg="User already exists")
    return render_template("signup.html", msg="")

@app.route('/add/campaign/<sponsor_id>', methods=["GET", "POST"])
def create_new_campaign(sponsor_id):
    if request.method == "POST":
        campaignName = request.form.get("campaignName")
        campaigndescription = request.form.get("campaignDescription")
        start_date = parser.parse(request.form.get("startDate"))
        end_date = parser.parse(request.form.get("endDate"))
        budget = request.form.get("budget")
        niche = request.form["niche"]
        visibility = request.form["visibility"]
        new_campaign = Campaign(campaign_name=campaignName, campaign_description=campaigndescription, start_date=start_date,
                                end_date=end_date, budget=budget, niche=niche, visibility=visibility, sponsor_id=sponsor_id)
        db.session.add(new_campaign)
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))
    return render_template("create_campaign.html")

@app.route('/edit/campaign/<campaign_id>', methods=["GET", "POST"])
def edit_campaign(campaign_id):
    campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
    if request.method == "POST":
        campaign.campaign_name = request.form.get("campaignName")
        campaign.campaign_description = request.form.get("campaignDescription")
        campaign.start_date = parser.parse(request.form.get("startDate"))
        campaign.end_date = parser.parse(request.form.get("endDate"))
        campaign.budget = request.form.get("budget")
        campaign.niche = request.form["niche"]
        campaign.visibility = request.form["visibility"]
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))
    return render_template("edit_campaign.html", campaign=campaign)

@app.route('/delete/campaign/<campaign_id>', methods=["GET","POST"])
def delete_campaign(campaign_id):
    AdRequest.query.filter_by(campaign_id=campaign_id).delete()
    Campaign.query.filter_by(campaign_id=campaign_id).delete()
    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))

def fetch_sponsor_campaigns(user_id):
    return Campaign.query.filter_by(sponsor_id=user_id).all()
@app.route('/find',methods = ["GET","POST"])
def find_page():
    influencers = Users.query.filter_by(role=1).all()
    campaigns = Campaign.query.all()
    public_campaigns = Campaign.query.filter_by(visibility=0).all()
    users = Users.query.filter(or_(Users.role == 1, Users.role == 2)).all()

    if 'user' in session:
        usr = session['user']
        if usr['role'] == 0:
            return render_template("admin_find.html",campaigns = campaigns,users=users)
        elif usr['role'] == 1:
            return render_template("influencer_find.html",campaigns=public_campaigns)
        elif usr['role'] == 2:
            campaigns = fetch_sponsor_campaigns(usr['user_id'])
            return render_template("sponsor_find.html",influencers=influencers,campaigns=campaigns)
    return "<h1>Unauthorized Access</h1>"

@app.route('/adrequest/send/<target>',methods=["GET","POST"])
def send_ad_request(target):
    if 'user' in session:
        usr = session['user']
        source = usr['user_id']
        campaign_id = request.form['campaign']
        target = target
        requirements = request.form.get('adrequestDescription')
        amount = request.form.get('amount')
        adrequest = AdRequest(campaign_id=campaign_id,source=source,target=target,amount=amount,requirements=requirements)
        db.session.add(adrequest)
        db.session.commit()
        if usr['role'] == 0:
            return redirect(url_for("admin_dashboard"))
        elif usr['role'] == 1:
            return redirect(url_for("influencer_dashboard"))
        elif usr['role'] == 2:
            return redirect(url_for("sponsor_dashboard"))

    return "<h1>Unauthorized Access</h1>"

@app.route('/flag/campaign/<campaign_id>', methods=["GET","POST"])
def flag_campaign(campaign_id):
    flagged = Flagged(flagged_id = campaign_id,user_or_campaign = 0,status='pending')
    db.session.add(flagged)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/flag/user/<user_id>', methods=["GET","POST"])
def flag_user(user_id):
    flagged = Flagged(flagged_id = user_id,user_or_campaign = 1,status='pending')
    db.session.add(flagged)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))
def fetch_flagged_campaings(campaign_id):
    return Campaign.query.filter_by(campaign_id = campaign_id).first()
def fetch_flagged_users(user_id):
    return Users.query.filter_by(user_id=user_id).first()
@app.route('/remove/user/<user_id>', methods=["GET","POST"])
def remove_user(user_id):
    Users.query.filter_by(user_id=user_id).delete()
    Flagged.query.filter_by(flagged_id=user_id).delete()
    db.session.commit()
    return redirect(url_for('admin_dashboard'))
@app.route('/remove/campaign/<campaign_id>', methods=["GET","POST"])
def remove_campaign(campaign_id):
    Campaign.query.filter_by(campaign_id=campaign_id).delete()
    Flagged.query.filter_by(flagged_id=campaign_id).delete()
    db.session.commit()
    return redirect(url_for('admin_dashboard'))
@app.route('/ignore/<flagged_id>',methods=["GET","POST"])
def ignore_flag(flagged_id):
    Flagged.query.filter_by(flagged_id=flagged_id).delete()
    db.session.commit()
    return redirect(url_for('admin_dashboard'))
def fetch_influencer_campaigns(user_id):
    accepted_request = AdRequest.query.filter_by(target=user_id,status='accepted').all()
    campaigns = []
    for item in accepted_request:
        result = Campaign.query.filter_by(campaign_id=item.campaign_id)
    return campaigns
def fetch_private_campaigns(user_id):
    user = Users.query.filter_by(user_id=user_id).first()
    campaigns = Campaign.query.filter_by(niche=user.niche,visibility=1).all()
    return campaigns


def fetch_ad_requests_by_source(source_id):
    return AdRequest.query.filter_by(source=source_id).all()
def fetch_ad_requests_by_target(target_id):
    return AdRequest.query.filter_by(target= target_id).filter(AdRequest.status!="completed").all()
def fetch_completed_ad_requests(target_id):
    return AdRequest.query.filter_by(target=target_id).filter_by(status="completed").all()
def fetch_ad_requests_details():
    ad_request = AdRequest.query.all()
    d = {}
    for item in ad_request:
        result = Campaign.query.filter_by(campaign_id =item.campaign_id).first()
        d[item.adrequest_id] = result
    return d
def fetch_target_details():
    t = {}
    ad_request = AdRequest.query.all()
    for item in ad_request:
        result = Users.query.filter_by(user_id=item.target).first()
        t[item.adrequest_id] = result
    return t
def fetch_source_details():
    s = {}
    ad_request = AdRequest.query.all()
    for item in ad_request:
        result = Users.query.filter_by(user_id=item.source).first()
        s[item.adrequest_id] = result
    return s


@app.route('/edit/adrequest/<adrequest_id>',methods=["GET","POST"])
def edit_ad_request(adrequest_id):
    ad_request = AdRequest.query.filter_by(adrequest_id=adrequest_id).first()
    if request.method == "POST":
        description = request.form.get('adrequestDescription')
        amount = request.form.get('amount')
    
        ad_request.requirements = description
        ad_request.amount = amount
        db.session.commit()
    usr = session['user']
    if usr['role'] == 1:
        return redirect(url_for("influencer_dashboard"))
    elif usr['role'] == 2:
        return redirect(url_for("sponsor_dashboard"))
@app.route('/payment/adrequest/<adrequest_id>',methods=["GET","POST"])
def confirm_payment(adrequest_id):
    ad_request = AdRequest.query.filter_by(adrequest_id=adrequest_id).first()
    if request.method == "POST":
        ad_request.payment_status="Completed"
        db.session.commit()
        usr = session['user']
        if usr['role'] == 1:
            return redirect(url_for("influencer_dashboard"))
        elif usr['role'] == 2:
            return redirect(url_for("sponsor_dashboard"))

    
@app.route('/delete/adrequest/<adrequest_id>',methods=["GET","POST"])
def delete_ad_request(adrequest_id):
    ad_request = AdRequest.query.filter_by(adrequest_id=adrequest_id).delete()
    db.session.commit()
    usr = session['user']
    if usr['role'] == 1:
        return redirect(url_for("influencer_dashboard"))
    elif usr['role'] == 2:
        return redirect(url_for("sponsor_dashboard"))
@app.route('/review/adrequest/<adrequest_id>',methods=["GET","POST"])
def review_ad_request(adrequest_id):
    ad_request = AdRequest.query.filter_by(adrequest_id=adrequest_id).first()
    if request.method == "POST":
        review = request.form.get("review")
        print(review)
        ad_request.review=review
        db.session.commit()
        usr = session['user']
        if usr['role'] == 1:
            return redirect(url_for("influencer_dashboard"))
        elif usr['role'] == 2:
            return redirect(url_for("sponsor_dashboard"))
@app.route('/accept/adrequest/<adrequest_id>',methods=["GET","POST"])
def accept_ad_request(adrequest_id):
    ad_request = AdRequest.query.filter_by(adrequest_id=adrequest_id).first()
    campaign = Campaign.query.filter_by(campaign_id = ad_request.campaign_id).first()
    ad_request.status = 'accepted'
    campaign.status = 'assigned'
    db.session.commit()
    usr = session['user']
    if usr['role'] == 1:
        return redirect(url_for("influencer_dashboard"))
    elif usr['role'] == 2:
        return redirect(url_for("sponsor_dashboard"))
@app.route('/complete/adrequest/<adrequest_id>',methods=["GET","POST"])
def complete_ad_request(adrequest_id):
    ad_request = AdRequest.query.filter_by(adrequest_id=adrequest_id).first()
    ad_request.status = "completed"
    campaign = Campaign.query.filter_by(campaign_id = ad_request.campaign_id).first()
    campaign.status = 'pending'
    db.session.commit()
    usr = session['user']
    if usr['role'] == 1:
        return redirect(url_for("influencer_dashboard"))
    elif usr['role'] == 2:
        return redirect(url_for("sponsor_dashboard"))

@app.route('/edit/userinfo/<user_id>',methods=["GET","POST"])
def edit_user_info(user_id):
    user = Users.query.filter_by(user_id=user_id).first()
    if request.method == "POST":
        niche = request.form['niche']
        platform = request.form['platform']
        followers = request.form.get('followers')
        user.niche = niche
        user.platform = platform
        user.followers = followers
        db.session.commit()
        return redirect(url_for('influencer_dashboard'))
@app.route('/filter',methods=["GET","POST"])
def filter():
    usr = session['user']
    niche = request.form['niche']
    if usr['role'] == 1:
        campaigns = Campaign.query.filter_by(niche=niche).all()
        return render_template('influencer_find.html',campaigns=campaigns)
    elif usr['role'] == 2:
        influencers = Users.query.filter_by(niche=niche,role=1).all()
        campaigns = Campaign.query.filter_by(sponsor_id=usr['user_id']).all()
        return render_template('sponsor_find.html',influencers=influencers,campaigns=campaigns)

@app.route('/api/get/campaigns',methods=["GET"])
def get_campaign_details():
    campaigns = Campaign.query.all()
    d = {}
    for item in campaigns:
        l = []
        l.append(item.campaign_name)
        l.append(item.campaign_description)
        d[item.campaign_id] = l
    return jsonify(d)
@app.route('/',methods=["GET","POST"])
def home():
    return render_template('home.html')

    

