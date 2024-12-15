class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:"root@123"@localhost:3306/car_dealership'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
