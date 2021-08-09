from demo import User, db
query1 = User.query.filter_by(name='Bob')
query2 = User.query.filter(User.name.like('%b%'))
query3 = User.query.filter(User.name.like('%b%')).limit(5)
query4 = User.query.filter(User.name.ilike('%b%'))
num_users = User.query.filter_by(name='Bob').count()

# for i in query4:
#     print(i)
print(num_users)