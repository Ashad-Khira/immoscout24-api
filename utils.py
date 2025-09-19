import json, re
from parsel import Selector
from get_response import request_me


def c_replace(html=''):
    if isinstance(html, str):
        html = html.replace("&gt;", ">")
        html = html.replace("&q;", '"')
        html = html.replace("&lt;", "<")
        html = html.replace("&amp;", "&")
        html = html.replace("&trade;", "™")
        html = html.replace("&rsquo;", "’")
        html = html.replace("&lsquo;", "‹")
        html = html.replace("&Reg;", "®")
        html = html.replace("\r\n", " ")
        html = html.replace("", "")
        # html = html.replace(vbLf, " ").replace(vbCrLf, " ").replace(vbCr, " ")
        html = html.replace("\t", " ")
        html = html.replace("\n", " ")
        html = html.replace("\r", " ")
        html = html.replace("&nbsp;", " ")
        html = re.sub("<script[^>]*>([\w\W]*?)</script>", " ", html)
        html = re.sub("\* style specs start[^>]*>([\w\W]*?)style specs end *", " ", html)
        html = re.sub("<style[^>]*>([\w\W]*?)</style>", " ", html)
        html = re.sub("<!--([\w\W]*?)-->", " ", html)
        html = re.sub("<([\w\W]*?)>", " ", html)
        html = re.sub("<.*?>", " ", html)
        # html = str(emoji.get_emoji_regexp().sub(u'', html))
        html = re.sub(" +", " ", html)
        return html.strip()
    
    elif isinstance(html, list):
        return [j for j in [c_replace(i) for i in html] if j]
    else:
        raise TypeError(f'must be str or list - object pass is ({type(html)}) object....')


def main(main_url):
    api_response_details = {}
    response_data = request_me(url=main_url)
    if response_data.get('response'):
        respo_text = Selector(text=response_data.get('response'))
        main_response = {}
        
        try:
            script_data = respo_text.xpath('//script[contains(text(),"__INITIAL_STATE__")]//text()').get()
            match = re.search(r'__INITIAL_STATE__\s*=\s*(\{.*\})', script_data, re.DOTALL)
            json_data = json.loads(match.group(1))
            
            try:
                Title = json_data['listing']['listing']['localization']['de']['text']['title']
            except:
                try:
                    Title = json_data['listing']['listing']['localization']['en']['text']['title']
                except:
                    Title = ""
            
            try:
                description = json_data['listing']['listing']['localization']['de']['text']['description']
            except:
                try:
                    description = json_data['listing']['listing']['localization']['en']['text']['description']
                except:
                    description = ""
            description = c_replace(description)
            
            image_data = []
            try:
                main_images = json_data['listing']['listing']['localization']['de']['attachments']
            except:
                try:
                    main_images = json_data['listing']['listing']['localization']['en']['attachments']
                except:
                    main_images = []
            for j in main_images:
                image_data.append(j['url'])
            
            try:
                Provider_Info = json_data['listing']['listing']['lister']
            except:
                Provider_Info = {}
            
            Provider = {
                "name": Provider_Info.get("legalName"),
                "address": Provider_Info.get("address"),
                "phone": Provider_Info.get("phone"),
                "given_name": Provider_Info.get("contacts", {}).get("inquiry", {}).get("givenName")
            }
            
            try:
                Advertisement_Number = json_data['listing']['listing']['id']
            except:
                Advertisement_Number = ""
            
            try:
                DisplayReferenceId = json_data['travelTime']['hasDefaultPOI'][0]['externalIds']['displayReferenceId']
            except:
                DisplayReferenceId = ""
            
            try:
                characteristics = json_data['travelTime']['hasDefaultPOI'][0]['characteristics']
                main_information = {
                    "numberOfRooms": characteristics.get("numberOfRooms"),
                    "floor": characteristics.get("floor"),
                    "livingSpace": characteristics.get("livingSpace"),
                    "yearBuilt": characteristics.get("yearBuilt")
                }
            except:
                main_information = {}
            
            try:
                main_address = json_data['travelTime']['hasDefaultPOI'][0]['address']
                Address = {
                    "locality": main_address.get("locality"),
                    "country": main_address.get("country"),
                    "street": main_address.get("street"),
                    "postalCode": main_address.get("postalCode"),
                    "region": main_address.get("region"),
                    "latitude": main_address.get("geoCoordinates", {}).get("latitude"),
                    "longitude": main_address.get("geoCoordinates", {}).get("longitude")
                }
            except:
                Address = {}
            
            try:
                Main_Area = json_data['travelTime']['hasDefaultPOI'][0]['prices']['rent']
            except:
                Main_Area = {}
            
            Area = {
                "net": Main_Area.get("net"),
                "gross": Main_Area.get("gross"),
                "extra": Main_Area.get("extra")
            }
            
            main_response['Title'] = Title
            main_response['Description'] = description
            main_response['Images'] = image_data
            main_response['Provider'] = Provider
            main_response['Advertisement_Number'] = Advertisement_Number
            main_response['DisplayReferenceId'] = DisplayReferenceId
            main_response['Main_Information'] = main_information
            main_response['Address'] = Address
            main_response['Area'] = Area
            
            api_response_details.update({
                'error': 'OK',
                'response_code': 200,
                'proxies_retries': response_data.get('proxies_retries')
            })
            api_response_details.update({"parsed_results": main_response})
            api_response_details.update({'html': response_data.get('response')})
            
            return api_response_details
        
        except Exception as e:
            api_response_details.update({'error': str(e), 'response_code': 500})
    else:
        api_response_details.update({
            'response_code': 500,
            'message': f'Unable to obtain the correct response from the URL: {main_url}',
            'error': response_data.get('errors'),
            'proxies_retries': response_data.get('proxies_retries')
        })
    
    return api_response_details
