import json
from urllib import request
import boto3
import datetime

print('Loading function')

s3 = boto3.client('s3')

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    bucket = 'solarshed'
    key = 'heartbeat.txt'
    try:
        alert = None
        response = s3.get_object(Bucket=bucket, Key=key)
        last_mod = response.get("LastModified")
        now = datetime.datetime.now(datetime.timezone.utc)
        first_line = response.get('Body').read().decode('utf-8').split('\n')[0]
        if int((now - last_mod).total_seconds()) > 60 * 30:
            alert = 'WARNING: It has been more than 30 minutes, ' + str(
                int((now - last_mod).total_seconds()/60))
        else:
            print('OK: ' + str(int((now - last_mod).total_seconds()/60)) +
            ' ' + first_line)
            return True
        print(alert)

        last_mod_str = last_mod.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        data = {
            "payload": {
                "summary": "Solar Shed Heartbeat Alert",
                "timestamp": now.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
                "source": "solarshed.localhost",
                "severity": "critical",
                "component": "heartbeat",
                "group": "solar-shed",
                "class": "heartbeat",
                "custom_details": {
                  "last_heartbeat": first_line,
                  "last_modified": last_mod_str,
                  "message": alert
                }
            },
            "routing_key": "a52bbb5d27044209d0962681dc29de55",
            "event_action": "trigger",
            "client": "AWS Lambda"
        }

        url = 'https://events.pagerduty.com/v2/enqueue'
        headers = {'Content-Type':'application/json'}
        bindata = json.dumps(data).encode('utf-8')
        req = request.Request(url, bindata, headers)
        resp = request.urlopen(req)
        print(resp.read());
        print(resp.getheaders());

        return True
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. '
              'Make sure they exist and your bucket is in the same region '
              'as this function.'.format(key, bucket))
        raise e

