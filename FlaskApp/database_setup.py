import os
import sys
import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

with sqlalchemy.create_engine(
    'postgresql:///postgres', isolation_level='AUTOCOMMIT').connect() as \
        connection:
    connection.execute('CREATE DATABASE catalog')

db_string = 'postgresql:///catalog'

db = create_engine(db_string)
Base = declarative_base()


class Genres(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Movies(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    genre_id = Column(Integer, ForeignKey('genres.id'))
    title = Column(String(250), nullable=False)
    description = Column(String(250))
    genre = relationship('Genres')


Session = sessionmaker(db)
session = Session()

Base.metadata.create_all(db)

# Create Genres Table
comedy = Genres(name='Comedy')
horror = Genres(name='Horror')
action = Genres(name='Action')
drama = Genres(name='Drama')
romance = Genres(name='Romance')

session.add(comedy)
session.add(horror)
session.add(action)
session.add(drama)
session.add(romance)
session.commit()

# Create Movies Table

shining = (
    'A family heads to an isolated hotel for the winter where a '
    'sinister presence influences the father into violence, while his pyschic'
    'son sees horrific forebodings from both past and future.'
    )

the_shining = Movies(
    title='The Shining',
    description=shining,
    genre_id=2
    )

red_october = (
    'In November 1984 the Soviet Unions best submarine captain '
    'violates orders and heads for the US either trying to defect or start a '
    'war.'
    )

the_hunt_for_red_october = Movies(
    title='The Hunt for Red October',
    description=red_october,
    genre_id=3
    )

notebook = (
    'A poor yet passionate young man falls in love with a rich young '
    ' woman, giving her a sense of freedom, but they are soon separated '
    'because of their social differences.'
    )

the_notebook = Movies(
    title='The Notebook',
    description=notebook,
    genre_id=5
    )

other_guys = (
    'Two mismatched New York City detectives seize an opportunity '
    'to step up like the top cops, whom they idolize, only things do not '
    'quite go as planned.'
    )

the_other_guys = Movies(
    title='The Other Guys',
    description=other_guys,
    genre_id=1
    )

man = (
    'A look at the life of the astronaut, Neil Armstrong, and the '
    'legendary space mission that led him to become the first man to walk on '
    'the Moon on July 20, 1969.'
    )

first_man = Movies(
    title='First Man',
    description=man,
    genre_id=4
    )

avengers = (
    'The Avengers and their allies must be willing to sacrifice '
    'all in an attempt to defeat the powerful Thanos before his blitz of '
    'devastation and ruin puts an end to the universe.'
    )

avengers_infinity_war = Movies(
    title='Avengers Infinity War',
    description=avengers,
    genre_id=3
    )

session.add(the_shining)
session.add(the_hunt_for_red_october)
session.add(the_notebook)
session.add(the_other_guys)
session.add(first_man)
session.add(avengers_infinity_war)
session.commit()
