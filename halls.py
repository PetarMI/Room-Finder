import urllib2
from lxml import etree
from pyquery import PyQuery as pq
import smtplib
import json
import httplib
import time
import logging

living_science_url = "http://reservation.livingscience.ch/en/living"
student_village_url = "http://studentvillage.ch/en/accommodation/"
logging.basicConfig(filename='rooms.log',level=logging.DEBUG)
prev_room = ""

def get_contents_url(url):
    sock = urllib2.urlopen(url)
    htmlSource = sock.read()                           
    sock.close()
    
    return htmlSource

def get_contents_file(filename):
    with open (filename, "r") as html_file:
        html_source = html_file.read()

    return html_source

def validateHTML(html_src):
    try:
        validated_html = html_src.decode('utf-8', 'ignore')
    except Exception as e:
        log_event(str(e), False)

    return validated_html

def send_mail(halls):
    try: 
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login("petar2394@gmail.com", "***")
        
        header = 'To:' + "petar2394@gmail.com" + '\n' + 'From: ' + "petar2394@gmail.com" + '\n' + 'Subject:Room Available \n'
        msg = header + "\nA room is available at " + halls + "!\n\n"
        server.sendmail("petar2394@gmail.com", "petar2394@gmail.com", msg)
        server.quit()
    except Exception as e:
        log_event("Couldn't send email", False)

def log_event(msg, status):
    t = get_time()
    if (status):
        logging.info(msg + " at: " + t)
    else:
        logging.warning(msg + " at: " + t)

def get_time():
    return time.strftime('%H:%M %d-%b')

def check_halls(url, selector):
    raw_html = get_contents_url(url)
    html_src = validateHTML(raw_html)
    try:
        d = pq(html_src)
        entries = d.find(selector).text().split().count("Available")
    except Exception as e:
        log_event("Error while parsing HTML", False)

    return entries

def check_SV():
    raw_html = get_contents_url(student_village_url)
    html_src = validateHTML(raw_html)
    global prev_room
    free_rooms = ""
    free_count = 0

    try:
        d = pq(html_src)
        rooms = d.find('tbody').children()
        for r in rooms:
            room = pq(r)
            if (room.text().split().count("Available") > 0):
                room_id = room.find(".font_weight_normal").text()
                free_rooms += room_id
                free_count += 1
    except Exception as e:
        log_event("Error while parsing HTML for STUDENT VILLAGE", False)

    if (free_count > 0):
        if (prev_room == free_rooms):
            free_count = 0
            log_event("Found same available rooms at STUDENT VILLAGE", True)
        else:
            prev_room = free_rooms
    else:
        prev_room = ""

    return free_count

def search():
    ls_count = check_halls(living_science_url, '.list.scroll')
    sv_count = check_SV()

    if (ls_count > 0):
        log_event("AVAILABLE room in LIVING SCIENCE", True)
        send_mail("LIVING SCIENCE")

    if (sv_count > 0):
        log_event("AVAILABLE room in STUDENT VILLAGE", True)
        send_mail("STUDENT VILLAGE")
    
    if (ls_count == 0 and sv_count == 0):
       log_event("NO rooms", True)

if __name__ == "__main__":
    while True:
        search()
        time.sleep(1200) # 3600 seconds = 1 hour