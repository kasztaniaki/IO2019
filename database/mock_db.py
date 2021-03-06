import os
import json
import string
import random
import datetime

from database.dbmodel import Pool, db, Software, OperatingSystem, User, SoftwareList, Reservation, Issue

MOCK_DATA_PATH = './database/mock_data'


def gen_mock_users(filename):
    with open(os.path.join(MOCK_DATA_PATH, filename)) as json_file:
        data = json.load(json_file)
        for user_data in data['users']:
            password = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
            User.add_user(user_data['Email'], password, user_data['Name'], user_data['Surname'], user_data['IsAdmin'])


def gen_mock_pools(filename):
    with open(os.path.join(MOCK_DATA_PATH, filename)) as json_file:
        data = json.load(json_file)
        for pool_data in data['pools']:
            pool = Pool.add_pool(pool_data['ID'], pool_data['Name'], pool_data['MaximumCount'],
                                 pool_data['Description'], pool_data['Enabled'])
            operating_system = OperatingSystem.add_operating_system(pool_data['OSName'])
            pool.set_operating_system(operating_system)

            for name, version in pool_data['InstalledSoftware']:
                software = Software.add_software(name)
                pool.add_software(software, version)


def gen_mock_issues(filename):
    with open(os.path.join(MOCK_DATA_PATH, filename)) as json_file:
        data = json.load(json_file)
        for issue_data in data['issues']:
            user_id = User.get_user_by_email(issue_data['Email']).ID
            Issue.add_issue(issue_data['PoolID'], user_id, issue_data['Subject'], issue_data['Message'])


def gen_mock_reservations(filename):
    with open(os.path.join(MOCK_DATA_PATH, filename)) as json_file:
        data = json.load(json_file)
        for res_data in data['reservations']:
            user = User.get_user(res_data["UserID"])
            pool = Pool.get_pool(res_data["PoolID"])
            today = datetime.datetime.now()
            sd = datetime.datetime.fromtimestamp(int(res_data["StartDate"]))
            start_date = today + datetime.timedelta(
                days=-today.weekday() + sd.weekday(),
                hours=-today.hour + sd.hour - 2,
                minutes=-today.minute + sd.minute,
                seconds=-today.second,
                microseconds=-today.microsecond
            )
            ed = datetime.datetime.fromtimestamp(int(res_data["EndDate"]))
            end_date = today + datetime.timedelta(
                days=-today.weekday() + ed.weekday(),
                hours=-today.hour + ed.hour - 2,
                minutes=-today.minute + ed.minute,
                seconds=-today.second,
                microseconds=-today.microsecond
            )
            reservation = Reservation(
                PoolID=pool.ID,
                UserID=user.ID,
                StartDate=start_date,
                EndDate=end_date,
                MachineCount=res_data["Count"],
                Cancelled=res_data["Cancelled"]
            )

            db.session.add(reservation)
            db.session.commit()


def gen_mock_data():
    gen_mock_pools('pools.json')
    gen_mock_users('users.json')
    gen_mock_reservations('reservations.json')
    gen_mock_issues('issues.json')
