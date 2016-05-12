from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Items, Users

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy users
benioff = Users(name = 'David Benioff', email = 'david.benioff@hbo.com', picture='http://www.tvweek.com/blogs/tvbizwire/david%20benioff.png')
martin = Users(name = 'George RR Martin', email = 'george.martin@remotehouse.com', picture='http://cdn1.sciencefiction.com/wp-content/uploads/2011/10/George-RR-Martin.png')
session.add(benioff)
session.add(martin)
session.commit()

# Add categories
names = ['Lannister', 'Stark', 'Baratheon', 'Tully', 'Targaryen', 'Bolton', 'Martell', 'Tyrell']

for house in names:
    name = Category(name = house)
    session.add(name)
    session.commit()

# Add items
ned = Items(name = 'Ned', image = 'http://vignette2.wikia.nocookie.net/gameofthrones/images/9/9c/EddardStark.jpg/revision/latest?cb=20110626030942', description = 'Ned Stark is an honourable hero who is unfortunately decapitated for treason.', user_id = '1', cat_name='Stark')
session.add(ned)

tyrion = Items(name = 'Tyrion', image = 'https://upload.wikimedia.org/wikipedia/en/5/50/Tyrion_Lannister-Peter_Dinklage.jpg', description = 'Tyrion is a dwarf but super-intelligent and able to outwit everybody else.', user_id = '2', cat_name='Lannister')
session.add(tyrion)

robert = Items(name = 'Robert', image ='http://images6.fanpop.com/image/photos/37500000/robert-baratheon-house-baratheon-37581104-1995-3000.jpg', description = 'Robert was a great warrior who defeated Rhaegar but then turned out to be a drunken oaf of a king.', user_id = '1', cat_name='Baratheon')
session.add(robert)

daenerys = Items(name = 'Daenerys', image='https://pbs.twimg.com/profile_images/608013046192185344/Vp1n5A14.jpg', description= 'Daenerys was originally forced into a marriage with a Dothraki but he died.', user_id='2', cat_name='Targaryen')
session.add(daenerys)

ramsay = Items(name='Ramsay', image='http://assets.viewers-guide.hbo.com/large5536cfd8d61fb.jpg', description='Ramsay is a brutal psychopath who likes to flay people and hunt innocent women.', user_id='1', cat_name='Bolton')
session.add(ramsay)

oberyn = Items(name='Oberyn', image='http://vignette1.wikia.nocookie.net/gameofthrones/images/5/5f/Oberyn-Martell-401-promo.jpg/revision/latest?cb=20140406140908', description = 'Oberyn is a gifted fighter known as the Red Viper with a specialty in poisons and almost killed Gregor Clegane.', user_id='2', cat_name='Martell')
session.add(oberyn)

margaery = Items(name='Margaery', image='http://cdn.hbowatch.com/wp-content/uploads/2013/05/Game-of-Thrones-Season-3-Margaery-Tyrell.jpg', description='Margaery was married to Joffrey who was later poisoned to death', user_id='1', cat_name='Tyrell')
session.add(margaery)

session.commit()