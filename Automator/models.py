from Automator import db, login_manager
from Automator import app
from Automator import bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    password_hash = db.Column(db.String(), nullable=False)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


with app.app_context():
    # db.drop_all()
    # db.create_all()
    # user1 = User(username="yy", password_hash=bcrypt.generate_password_hash("").decode('utf-8'))
    # db.session.add(user1)
    # db.session.commit()
    # user = User.query.filter_by(username="yy").first()
    # print(user.check_password_correction(attempted_password=""))
    pass
