import os
import requests
import json

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
#    name = os.environ.get("NAME", "World")
    session = requests.Session()
    loginUrl = 'http://tomsdev.jonnou.net/accounts/login/'
    try:
        response = session.get(loginUrl)
    except:
        return 'Could not get session option from TOMS'

    if response.status_code not in [200, 302, 301]:
        return 'Got error when getting session from TOMS %d' % response.status_code

    headers = {
               'Content-type': 'application/x-www-form-urlencoded',
               'X-CSRFToken': response.cookies['csrftoken']
    }
    
    loginData = {'username': 'ghhweb', 'password': 'ghhweb01222013'}

    try:
        response = session.post(loginUrl, data=loginData, headers=headers)
    except:
        return 'Exception thrown trying to log into TOMS'

    if response.status_code not in [200, 302, 301]:
        return 'Error code returned trying to log into TOMS %d ' % response.status_code

    if session == None or headers == None:
            return 'Empty header or session object returned from login attempt'

    getReportUrl = 'http://tomsdev.jonnou.net/rest/job-data/4866/'

    try:
        response = session.get(getReportUrl, headers= headers)
    except: 
        return 'Exception throw retrieving report data'

    if response.status_code not in [200, 302, 301]:
        return 'Error code returned retrieving report data'

    report_data = json.loads(response.text)

    fields = [
        'Municipality Code',
        'Account Number',
        'Name',
        'Address',
        'City',
        'State',
        'Zip Code',
        'Occupational Code',
        'Occupational Value',
        'Bill Type',
        'Action Code',
        'Batch',
        'Amount Due',
        'Payment Type',
        'Comment',
        'TaxYear',        
    ]

    output_data = []
    output_data.append(fields)

    output_text = ','.join(fields) + '\n'

    for account in report_data:
        address1, address2 = account['address'].split('\n')
        city = address2.split(None,3)

        row_data = [
        '--Municipality Code--',
        account['accountNumber'],
        account['obligor']['fullName'],
        address1,
        city[0],
        city[1],
        city[2],
        '--Occupational Code--',
        '--Occupational Value--',
        '--Bill Type--',
        '--Action Code--',
        '--Batch--',
        '--Amount Due--',
        '--Payment Type--',
        '--Comment--',
        '--TaxYear--',
        ]
        output_data.append(row_data)
        output_text += ','.join(row_data)
        output_text += '\n'

#    return json.dumps(output_data)
    return output_text

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
