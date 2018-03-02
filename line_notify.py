import requests

def lxe_line_notify(message):
    line_notify_token = 'GECD1YtE5gOpILNzRxo9f90l3O1UxwlGCSS8dkSAeCa'
    line_notify_api = 'https://notify-api.line.me/api/notify'
    payload = {'message': message}
    headers = {'Authorization': 'Bearer ' + line_notify_token}  # 発行したトークン
    line_notify = requests.post(line_notify_api, data=payload, headers=headers)
