import requests
import json
import csv


def crock_csv_generator(request):

    crock_raw_data = None

    with open('councilrock_2021.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        crock_raw_data = list(reader)

    crock_school_data = {}
    for entry in crock_raw_data:
        entry_key = entry['Year'] + '-' + entry['Account']
        crock_school_data[entry_key] = entry

#    return json.dumps(crock_school_data)


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

    getReportUrl = 'http://tomsdev.jonnou.net/rest/job-data/5161/'

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
    ]

    output_data = []
    output_data.append(fields)

    output_text = ','.join(fields) + '\n'

    year = "2021"

    for account in report_data:


        account_key = year + "-" + account['accountNumber']

        address_list = account['address'].split('\n')

        address = ''
        city = ''
        if len(address_list) == 2:
            address1 = address_list[0]
            address2 = address_list[1]
        else:
            address1 = ' '.join(address_list[:2])
            address2 = address_list[3]

#        address1, address2 = account['address'].split('\n')
        city = address2.split(None,3)

        # batch field - the actual batch value should come as an input to the function
        batch = ''
        if account['obligations'][0]['settlement'] in ('P','E'):
            batch = 'H0922'

        row_data = [
        # Municipality: Code Is determined by the first 2 digits of the Account Number 
        account['accountNumber'][:2],
        account['accountNumber'],
        account['obligor']['fullName'],
        address1,
        city[0],
        city[1],
        city[2],
        crock_school_data[account_key]['OccCode'],
        crock_school_data[account_key]['OccValue'],
        # Bill Type: Always defaults to the letter “O” (occupation)
        'O',
        # Action Code: Will be the letter “A”, when we send the account on report as paid
        'A' if account['obligations'][0]['settlement'] == 'P' else '',
        # Batch: Is blank until the obligor goes on report. It’s the report date “HMMYY”
        batch,
        # Original amount due from the file
        crock_school_data[account_key]['TotalAmtDue'],
        # Payment Type: Is “P”. Indicates the that the Amount Due is in the penalty phase.
        'P',
        # orginal comment line from file 
        crock_school_data[account_key]['Comments']
        ]

# wrap row data in quotes
        formatted_row = []
        for element in row_data:
            formatted_row.append('"' + element + '"')
        output_text += ','.join(formatted_row)
        output_text += '\n'

    return output_text
