import json
import sqlite3
import math
from flask import Flask, request
from flask_cors import CORS, cross_origin
app  = Flask(__name__)
cors = CORS(app, resources = {r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

# get users
@app.route('/users', methods=['GET'])
@cross_origin()
def get_users():
    # request
    keyword     = request.args.get('keyword')
    search_type = request.args.get('search_type')
    start_age   = request.args.get('start_age')
    end_age     = request.args.get('end_age')
    page        = int(request.args.get('page'))
    per_page    = int(request.args.get('per_page'))

    # connection
    conn = sqlite3.connect('user.db')
    cur  = conn.cursor()

    # prepare query
    q_str   = ''
    q_param = []

    # search by keyword
    if keyword:
        if search_type == 'name':
            q_str += ' WHERE (first_name like ? or last_name like ?)'
            q_param.append('%' + keyword + '%')
            q_param.append('%' + keyword + '%')
        elif search_type == 'email':
            q_str += ' WHERE email like ?'
            q_param.append('%' + keyword + '%')
        elif search_type == 'gender':
            q_str += ' WHERE gender = ?'
            q_param.append(keyword)

    # search by age range
    if start_age and end_age:
        if not q_str:
            q_str += ' WHERE age >= ? and age <= ?'
        else:
            q_str += ' and (age >= ? and age <= ?)'
        q_param.append(int(start_age))
        q_param.append(int(end_age))
    elif start_age and not end_age:
        if not q_str:
            q_str += ' WHERE age >= ?'
        else:
            q_str += ' and age >= ?'
        q_param.append(int(start_age))
    elif not start_age and end_age:
        if not q_str:
            q_str += ' WHERE age <= ?'
        else:
            q_str += ' and age <= ?'
        q_param.append(int(end_age))

    # count search users
    cur.execute('SELECT count(*) FROM users' + q_str, q_param)
    user_count = cur.fetchone()[0]

    # pagination
    q_str += ' LIMIT ? OFFSET ?'
    q_param.append(per_page)
    q_param.append((page - 1) * per_page)

    # send query search users
    cur.execute('SELECT * FROM users' + q_str, q_param)
    user_rows = cur.fetchall()

    # prepare data
    users_as_dict = []
    for row in user_rows:
        users_as_dict.append({
            'id'       : row[0],
            'firstname': row[1],
            'lastname' : row[2],
            'email'    : row[3],
            'gender'   : row[4],
            'age'      : row[5]
        })

    # response
    res_users = {
        'data': users_as_dict,
        'meta': {
            'page'      : page,
            'per_page'  : per_page,
            'total_page': math.ceil(user_count / per_page),
            'total_data': user_count,
        }
    }

    return res_users

if __name__ == '__main__':
    app.run()