import sys
import csv
import os
import requests
from flask import make_response
from app.lib.constantcontact import ConstantContact
from app import celery


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    prcnt = round(100.0 * count / float(total), 1)
    bar = '█' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s %s\r' % (bar, prcnt, '%', status))
    sys.stdout.flush()


def WriteDictToCSV(csv_file, csv_columns, dict_data):
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)
    return


def WriteCSVFile(eventId):
    # ConstantContact setupçj
    API_KEY = "hhw49s75dvjzf7fn46hxx3mp"
    API_ACCESS_CODE = "97b44606-0a25-4641-a4ca-4eb543846b31"
    cc = ConstantContact(API_KEY, API_ACCESS_CODE)

    # Make API request and retrieve all registrants
    event_reg_params = {"eventId": eventId, "limit": "limit"}
    request = cc.eventspot.events.eventId.registrants(
        variable=event_reg_params)

    # List of registrants
    registrants = request["results"]

    if len(registrants) == 0:
        print("Please check your eventId. Exiting now...")
        sys.exit(0)

    # Dictionary to keep track of our registrants
    users = {}

    # Loop over registrants and extract first_name, last_name, email
    #   and store as a user in the users dictionary
    for user in registrants:
        uid = user["id"]
        users[uid] = {"first_name": user["first_name"],
                      "last_name": user["last_name"]}

    # We are using the user variable so we can remove registrants
    del registrants

    # Keep track of our total users and the current index for our progress bar
    total_users = len(users)
    current_user_index = 1

    # Now loop over our users and perform an API request to retrieve a user's
    #   company name since we need company_name in the CSV export
    for uid in users:
        # Output progress bar
        progress_status = "User: "+str(current_user_index)+"/"+str(total_users)
        progress(current_user_index, total_users, status=progress_status)

        # Make API request for user's company name
        try:
            reg_user_params = {"eventId": eventId, "registrantId": uid}
            reg_user_req = cc.eventspot.events.eventId.registrants.registrantId(
                variable=reg_user_params
            )

            # Store company name in respective user
            company_name = reg_user_req["sections"][1]["fields"][2]["value"]
            users[uid]["company"] = company_name

            # Store the registration date in respective user
            registration_date = reg_user_req["registration_date"]
            users[uid]["registration_date"] = registration_date

            # increment our current index for our progress bar
            current_user_index += 1
        except requests.exceptions.HTTPError as err:
            print("Could not process User ID:", uid)
            print(err)
            print("Skipping", uid)
            print("-----------------------------")
            continue

    # Our WriteDictToCSV function requires a list of dictionary values
    dict_data = []
    for uid in users:
        dict_data.append(users[uid])

    # Don't need our users dictionary anymore so remove it
    del users

    # Perform CSV export
    csv_columns = ["first_name", "last_name", "company", "registration_date"]
    currentPath = os.getcwd()
    csv_file = currentPath + "/app/csv/registrants.csv"

    WriteDictToCSV(csv_file, csv_columns, dict_data)


@celery.task
def download_csv(eventId):
    WriteCSVFile(eventId=eventId)
    currentPath = os.getcwd()
    csv_string = ""
    with open(currentPath + "/app/csv/registrants.csv") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            csv_string += ", ".join(row) + "\n"
    response = make_response(csv_string)
    cd = 'attachment; filename=registrants.csv'
    response.headers['Content-Disposition'] = cd
    response.mimetype = 'text/csv'

    return response
