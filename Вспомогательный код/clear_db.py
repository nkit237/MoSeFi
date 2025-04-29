import db_session
from db_session import Film

db_sess = db_session.create_session()
db_sess.query(Film).filter(Film.about == None).delete()
db_sess.query(Film).filter(Film.link == None).delete()
db_sess.commit()