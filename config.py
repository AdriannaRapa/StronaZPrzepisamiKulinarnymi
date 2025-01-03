class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:TwojeHaslo@localhost/foodlab_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'twój_tajny_klucz'
