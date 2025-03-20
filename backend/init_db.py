from backend.models import Users , db

result = Users.query.all()

if len(result) == 0:
    admin = Users(name="admin",email="admin@test.com",password="1234")
    db.session.add(admin)
    db.session.commit()