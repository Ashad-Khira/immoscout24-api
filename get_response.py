import random, cloudscraper
from curl_cffi import requests as curl_cffi_requests
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

# TODO - Random user agent
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=500)

impersonate_arr = [
    'chrome123',
    'chrome124',
    'firefox133',
    'chrome120',
    'firefox135',
    'edge99',
    'chrome99_android',
    'chrome131_android',
    'edge101'
]

proxy_arr = ['''http://brd-customer-hl_87625cf5-zone-freemium:qsclmnsra6bv@brd.superproxy.io:33335''']


def request_me(url):
    errors = []
    proxies_dict = {'CurlCffi': 0, 'CloudScraper': 0, 'total': 0}
    response = None
    for i in range(6):
        try:
            print(f"🕸️Crawling URL: {url} - Tries: {i + 1}")
            if i % 2 == 0:
                proxies_dict['total'] = i + 1
                s = curl_cffi_requests.Session()
                s.headers.update({'User-Agent': user_agent_rotator.get_random_user_agent()})
                s.impersonate = random.choice(impersonate_arr)
                
                home_response = s.get('https://www.immoscout24.ch')
                if home_response.status_code == 200:
                    main_response = s.get(url=url)
                    proxies_dict['CurlCffi'] += 1
                    if '''__INITIAL_STATE__''' in main_response.text and main_response.status_code == 200:
                        response = main_response.text
                        break
                    else:
                        continue
                else:
                    continue
            else:
                scraper = cloudscraper.create_scraper()
                main_response = scraper.get(url=url).text
                proxies_dict['CloudScraper'] += 1
                if '''__INITIAL_STATE__''' in main_response.text and main_response.status_code == 200:
                    response = main_response
                    break
                else:
                    continue
        except Exception as e:
            errors.append(str(e))
    
    return {
        'response': response,
        'proxies_retries': proxies_dict,
        'errors': errors
    }


if __name__ == '__main__':
    print(request_me(
        url='https://www.immoscout24.ch/mieten/4002514533'
    ))
