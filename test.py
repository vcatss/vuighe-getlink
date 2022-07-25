from time import sleep
import requests
import json
import re
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
def get_post_ep(url_raw):
  """
  Read html to find value of data-id and data-episode-id
  """
  html = requests.get(url_raw)
  regex_pattern_step1 = r'(data-id=".*?" data-video-id=)|(data-episode-id=".*?")'
  regex_pattern_step2 = r'".*?"'
  match = re.findall(regex_pattern_step1, html.text)

  # get data_id 
  match_data_id = re.search(regex_pattern_step2, match[0][0])
  data_id = match_data_id.group(0)

  # match ep id 
  match_ep_id = re.search(regex_pattern_step2, match[1][1])
  ep_id = match_ep_id.group(0)

  return data_id, ep_id

def get_api_json(data_id, ep_id, url_raw):
  """
  Call vuighe api 
  """
  # discard double quote "
  data_id = data_id.strip('\"')
  ep_id = ep_id.strip('\"')

  # build api url
  url = 'https://vuighe.net/api/v2/films/'+data_id+'/episodes/'+ ep_id
  header = {
  "Referer":url_raw,
  'Content-Type': 'application/json',
  'X-Requested-With': 'XMLHttpRequest',
  }
  result = requests.get(url, headers=header)
  print(url)
  return result.json();

def decode_m3u8_hash(hash):
  result = ""
  for i in range(len(hash)):
    o = ord(hash[i])
    r = o ^ 69 
    decode_char = chr(r)
    result+= decode_char
  return result

def full_decode_flow(vuighe_link):
    data_id, ep_id = get_post_ep(vuighe_link)
    resp_json = get_api_json(data_id, ep_id, vuighe_link)
    try:
        
        try:
            fb = resp_json["sources"]["fb"][0]["src"]
            type = resp_json["sources"]["fb"][0]["type"]
            quality = resp_json["sources"]["fb"][0]["quality"]
            if "http" in fb:
                print("Found fb")
                print(fb,type,quality)
            else:
                print("Ops => found FB but not a good link")
                #document.querySelectorAll('.player-video')[0].getAttribute("src")
                #document.querySelectorAll('.setting-server-item')[0]
                options = uc.ChromeOptions()
                options.add_argument("--headless")
                driver = uc.Chrome(use_subprocess=True,options=options)
                driver.get(vuighe_link)
                sleep(1)
                driver.execute_script("document.querySelectorAll('.setting-server-item')[0].click()")
                sleep(1)
                htmls = driver.execute_script("return document.querySelectorAll('.player-video')[0]['src']")
                while htmls == "":
                    sleep(0.5)
                    htmls = driver.execute_script("return document.querySelectorAll('.player-video')[0]['src']")
                driver.quit()
                print(htmls,type,quality)
        except:
            print("No fb")
        try:
            m3u8 = resp_json["sources"]["m3u8"]["1"]
            m3u8_encrypt = resp_json["sources"]["m3u8"]["1"]
            m3u8_link = decode_m3u8_hash(m3u8_encrypt)
            if "http" in m3u8:
                print("Found m3u8")
            else:
                print("Found but blob")
        except:
            print("No fb")
        try:
            vip = resp_json["sources"]["vip"][0]["src"]
        except:
            print("No vip")
        try:
            gd = resp_json["sources"]["gd"][0]["src"]
        except:
            print("No gd")
        try:
            pt = resp_json["sources"]["gd"][0]["src"]
        except:
            print("No pt")
        try:
            yt = resp_json["sources"]["gd"][0]["src"]
        except:
            print("No yt")
    except:
        print("??")

def get_page_anime(page):
    html = requests.get(f"https://vuighe.net/anime/trang-{page}")
    soup = BeautifulSoup(html.text, features="html.parser")
    list = soup.findAll("div",{"class":"tray-item"})
    for item in list:
        try:
            soup = BeautifulSoup(str(item), features="html.parser")
            title = soup.find("div",{"class":"tray-item-title"})
            url = "https://vuighe.net" + soup.find("a")["href"]
            image = soup.find("img",{"class":"tray-item-thumbnail"})["data-src"]

            #=> find first link

            print("[Title]: " + title.text)
            print("[Url]: " + url)
            print("[Image]:" + image)

            #=> find session
            html2 = requests.get(url)
            soup2 = BeautifulSoup(html2.text, features="html.parser")
            seasons = soup2.findAll("div",{"class": "season-item"})
            if len(seasons) != 0:
                print(f"Found {len(seasons)}")
                for season in seasons:
                    soup3 = BeautifulSoup(str(season), features="html.parser")
                    name = soup3.find("span", {"class": "season-item-name"}).text.replace(" -","").strip()
                    start = soup3.find("div", {"class": "season-item"})["data-begin"]
                    end = soup3.find("div", {"class": "season-item"})["data-end"]
                    print(name,start,end)
            else:
                min = soup2.find("input", {"name": "current-episode"})["min"]
                max = soup2.find("input", {"name": "current-episode"})["max"]
                print(f"Found {min} - {max} episode")
                for i in range(1,10):
                    print(i)
                    url2 = url + f"/tap-{i}"
                    print(url2)
                    full_decode_flow(url2)

            print("============")
        except:
            continue


get_page_anime(1)

#full_decode_flow("https://vuighe.net/rwby-hyousetsu-teikoku/tap-1-bao-gom-tap-1-2-3")
