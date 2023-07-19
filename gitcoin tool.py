import time
import requests

# login to get api and scorer id - https://scorer.gitcoin.co/#/
# api key - https://scorer.gitcoin.co/#/dashboard/api-keys
# scorer id - https://scorer.gitcoin.co/#/dashboard/scorer

gitcoin_api = ''
scorer_id = ''

headers = {
    'accept': 'application/json',
    'X-API-Key': gitcoin_api,
    'Content-Type': 'application/json',
}

stamps_headers = {
    'authority': 'api.scorer.gitcoin.co',
    'accept': 'application/json, text/plain, */*',
    'origin': 'https://passport.gitcoin.co',
    'referer': 'https://passport.gitcoin.co/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

json_data = {
    'address': '',
    'community': 'Deprecated',
    'scorer_id': scorer_id,
    'signature': '',
    'nonce': '',
}

params = {
    'limit': '1000',
    'include_metadata': 'false',
}


def read_file(filename):
    result = []
    with open(filename, 'r') as file:
        for tmp in file.readlines():
            result.append(tmp.replace('\n', ''))

    return result


def write_to_file(filename, text):
    with open(filename, 'a') as file:
        file.write(f'{text}\n')


def check_wallet(address, private):
    json_data['address'] = address
    try:
        score = requests.post('https://api.scorer.gitcoin.co/registry/submit-passport', headers=headers, json=json_data).json()['score']
    except Exception as e:
        print(f'Rate limit error: 125 requests per 15 min. (https://docs.passport.gitcoin.co/building-with-passport/scorer-api/endpoint-definition#rate-limits)')
        print('Waiting 16 min.')
        time.sleep(16 * 60)
        check_wallet(address, private)
        pass
    print(f'{private};{address};{score}')
    # write_to_file('Score.txt', f'{private};{address};{score}')
    all_in_one = f'{private};{address};{score};'

    try:
        stamps = requests.get('https://api.scorer.gitcoin.co/ceramic-cache/stamp', params={'address': address},
                              headers=stamps_headers).json()['stamps']
    except Exception as e:
        print(f'Rate limit error: 125 requests per 15 min. (https://docs.passport.gitcoin.co/building-with-passport/scorer-api/endpoint-definition#rate-limits)')
        print('Waiting 16 min.')
        time.sleep(16 * 60)
        check_wallet(address, private)
        return None

    for stamp in stamps:
        all_in_one += f'{stamp["provider"]}:'

    write_to_file('all in one.txt', all_in_one[:-1])


def main():
    addresses = read_file('address;private.txt')
    for wallet in addresses:
        address, private = wallet.strip().split(';')
        check_wallet(address, private)


if __name__ == '__main__':
    main()
