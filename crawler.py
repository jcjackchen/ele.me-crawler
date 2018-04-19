# coding: utf-8

import urllib
import urllib2
import cookielib
import json
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
chromedriver = "/Users/jcjack/Desktop/Computer Network-PKU/project/chromedriver"
cookie_file = "cookie.txt"
mobile_phone = "13360161111"
poi_file = "poi.json"

def getJsonFromUrl(url):
    req = urllib2.Request(url)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    data = json.loads(res)
    return data

def getJsonWithCookie(url,cookie):

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie)) 
    res_data = opener.open(url)
    res = res_data.read()
    data = json.loads(res)
    return data 


def getLocation():
    url = "https://www.ele.me/restapi/shopping/v1/cities"
    try :
        data = getJsonFromUrl(url)
    except Exception as e:
        return e
    BJ = data["B"][0]
    uni_name = unicode("name","utf-8")
    uni_lon = unicode("longitude","utf-8")
    uni_lat = unicode("latitude","utf-8") 

    if BJ[uni_name] == unicode("北京","utf-8"):
        return BJ[uni_lat], BJ[uni_lon]
    else:
        return "Change of location"

def login():
    browser = webdriver.Chrome(chromedriver)
    login_url = "https://h5.ele.me/login/#redirect=https%3A%2F%2Fwww.ele.me%2Fshop%2F162650838&page=password"
    browser.get(login_url)

    inputs = browser.find_elements_by_tag_name("input")
    button = browser.find_element_by_class_name("SubmitButton-2wG4T")

    inputs[0].send_keys("13360161111")
    inputs[1].send_keys("jyc123456")
    button.click()

    cookie = browser.get_cookies()
    return cookie


def login_by_code():
    mobile_send_code = "https://h5.ele.me/restapi/eus/login/mobile_send_code"
    mobile_values = {"mobile":mobile_phone,"captcha_value":"","captcha_hash":""}
    data = urllib.urlencode(mobile_values)
    req = urllib2.Request(mobile_send_code,data)
    try:
        response = urllib2.urlopen(req).read()
    except Exception as e:
        captchas = "https://h5.ele.me/restapi/eus/v3/captchas"
        values = {"captcha_str":mobile_phone}
        data = urllib.urlencode(values)
        captcha_req = urllib2.Request(captchas,data)
        captcha_value = ""
        captcha_hash = ""
        browser = webdriver.Chrome(chromedriver)

        while(captcha_value == "" or captcha_hash == ""):
            response = urllib2.urlopen(captcha_req).read()

            response = json.loads(response)
            captcha_hash = response["captcha_hash"]
            captcha_image = response["captcha_image"]
            
            browser.get(captcha_image)
            captcha_value = raw_input("captcha:")
            
            mobile_values["captcha_value"] = captcha_value
            mobile_values["captcha_hash"] = captcha_hash
            data = urllib.urlencode(mobile_values)
            req = urllib2.Request(mobile_send_code,data)
            try:
                response = urllib2.urlopen(req).read()
            except Exception as e:
                captcha_value = ""
        
        browser.quit()

    response = json.loads(response)
    validate_token = response["validate_token"]
    login_by_mobile = "https://h5.ele.me/restapi/eus/login/login_by_mobile"
    status = True

    cookie = cookielib.MozillaCookieJar(cookie_file)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie)) 

    while status:
        validate_code = raw_input("validate_code:")
        values = {"mobile":mobile_phone,"validate_code":validate_code,"validate_token":validate_token}
        data = urllib.urlencode(values)
        req = urllib2.Request(login_by_mobile,data)
        try:
            response = opener.open(req)
            status = False
        except Exception as e:
            pass

    cookie.save(ignore_discard=True, ignore_expires=True)
    return cookie


def location_load():
    data = json.load(open(poi_file))
    uni_name = unicode("name","utf-8")
    uni_lon = unicode("longitude","utf-8")
    uni_lat = unicode("latitude","utf-8") 

    L = []
    name = []
    for p in data:
        L.append("latitude="+str(p[uni_lat])+"&longitude="+str(p[uni_lon]))
        name.append(p[uni_name])

    return L,name


def crawl():

    start_time = time.time()
    timeset = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    datafile = open(timeset+" Data.txt",'w')
    log = open(timeset+" Log",'w')

    ids = set()
    offset = 0
    L,name = location_load()
    cookie = cookielib.MozillaCookieJar()
    try:
        cookie.load(cookie_file, ignore_discard=True, ignore_expires=True)
    except Exception as e:
        cookie = login_by_code()

    string = "Total #POIs to explore: " + len(name)
    print(string)
    log.write(string)
    log.flush()

    loc = L.pop()
    loc_name = name.pop()
    log.write(loc_name.encode(encoding='UTF-8'))
    log.flush()
    print(loc_name+":")

    while True:
        time.sleep(1)
        url = "https://www.ele.me/restapi/shopping/restaurants?extras%5B%5D=activities&"+ loc +"&limit=30&offset="+ str(offset) +"&terminal=web"
        try :
            data = getJsonWithCookie(url,cookie)
            if data == []:
                print("Restaurants around have been searched...")
                if len(L) > 0:
                    if len(L)%10 == 0:
                        print("******There are " + str(len(L)) + " #POIs remained to explore******")
                        print("Time elapsed: "+ str(int(time.time()-start_time)) + "s")
                    offset = 0
                    loc = L.pop()
                    loc_name = name.pop()
                    log.write(loc_name.encode(encoding='UTF-8'))
                    log.flush()
                    print(loc_name+":")
                    continue
                else:
                    string = "total time spend: " + str(int((time.time()-start_time)/60)) + " min"
                    print(string)
                    log.write(string+'\n')
                    log.flush()
                    return
            print(url)
            log.write(url+'\n')
            log.flush() 
        except Exception as e:
            print("Failed to load data, relogin...")
            cookie = login_by_code()
            continue

        offset += 30
        try :
            for each in data :
                curr_id = each['id']
                if curr_id in ids:
                    continue
                else:
                    ids.add(curr_id)
                result =""+str(each['id'])+",'"+each['address']+"','"+each['name']+"',"+str(each['latitude'])+","+str(each['longitude'])+","+str(each['recent_order_num']) +","+str(each['regular_customer_count'])+","+ \
                    str(each['order_lead_time'])+","+str(each['phone'])+","+str(each['rating'])+","+str(each['rating_count'])+","+str(each['recommend']['is_ad'])+","+str(each['status'])+","+ \
                    str(each['is_new'])+"\n";#+str(each['float_delivery_fee']) +","+str(each['float_minimum_order_amount']) + "\n";
                datafile.write(result.encode(encoding='UTF-8'));
                datafile.flush()
            #print each['address'],each['name'],each['latitude'], each['longitude'], str(each['recent_order_num']), each['regular_customer_count'], \
            #each['phone'], each['rating'], each['rating_count'], each['recommend'], each['status'],each['is_new']
        except Exception as A:
            print (A)

if __name__ == "__main__":
    crawl()