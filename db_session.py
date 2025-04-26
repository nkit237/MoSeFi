import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


class Film(SqlAlchemyBase):
    __tablename__ = 'films'

    id = sa.Column(sa.Integer,
                   primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=True)
    genre = sa.Column(sa.String, index=True, nullable=True)
    about = sa.Column(sa.String, nullable=True)
    link = sa.Column(sa.String, nullable=True)
    grade = sa.Column(sa.Float, nullable=True)
    quantity = sa.Column(sa.Integer, nullable=True)

    watch = orm.relationship("Watch", back_populates='film')


class Review(SqlAlchemyBase):
    __tablename__ = 'reviews'

    id = sa.Column(sa.Integer,
                   primary_key=True, autoincrement=True)
    id_film = sa.Column(sa.Integer, nullable=True)
    review = sa.Column(sa.String, nullable=True)
    id_user = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    user = orm.relationship('User')


class Watch(SqlAlchemyBase):
    __tablename__ = 'watchs'

    id = sa.Column(sa.Integer,
                   primary_key=True, autoincrement=True)
    id_user = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    id_film = sa.Column(sa.Integer, sa.ForeignKey("films.id"))
    user = orm.relationship('User')
    film = orm.relationship('Film')


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer,
                   primary_key=True, autoincrement=True)
    id_user = sa.Column(sa.Integer, nullable=True)
    name = sa.Column(sa.String, nullable=True)

    review = orm.relationship("Review", back_populates='user')
    watch = orm.relationship("Watch", back_populates='user')


global_init("test.db")
