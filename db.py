#-*- coding: UTF-8 -*-
#!/usr/bin/python
import MySQLdb
import time
import re
import os
import urllib
from datetime import datetime
from xml.sax.saxutils import unescape

f = open('workfile.tex', 'w')
def db(hst, usr, pw, dba):
    db = MySQLdb.connect(host=hst, user=usr, passwd=pw, db=dba)
    # you must create a Cursor object. It will let
    # you execute all the queries you need
    cur = db.cursor()

    # Use all the SQL you like
    cur.execute("SELECT `id`, `title`, `body`, `timestamp` as `date` FROM `entries` WHERE isdraft = 'false' ORDER BY timestamp ASC")
    years = {}
    # ([],[],[],[],[],[],[],[],[],[],[],[])
    # print all the first cell of all the rows
    for row in cur.fetchall():
        if len(row) >= 4:
            dt_obj = datetime.fromtimestamp(row[3])
            if repr(dt_obj.year) not in years:
                years[repr(dt_obj.year)] = ([],[],[],[],[],[],[],[],[],[],[],[])
            title = row[1].decode('iso-8859-1')
            body = row[2].decode('iso-8859-1')
            # translation table for Umlaut
            table = {
                ord(u'$'): u'\$',
                ord(u'"'): u'"{}',
                ord(u'ä'): u'{\\\"a}',
                ord(u'ö'): u'{\\\"o}',
                ord(u'ü'): u'{\\\"u}',
                ord(u'Ä'): u'{\\\"A}',
                ord(u'Ö'): u'{\\\"O}',
                ord(u'Ü'): u'{\\\"U}',
                ord(u'ß'): u'{\\ss}',
                ord(u'%'): u'\\%',
                ord(u'†'): u'\\textdied',
                ord(u'‡'): u'\\ddag',
                ord(u'†'): u'\\textdagger',
                ord(u'_'): u'\_',
            }
            title = title.translate(table)
            body = body.translate(table)
            title = re.sub(r'[^\x00-\x7F]','', title)
            body = re.sub(r'[^\x00-\x7F]','', body)
            title = title.encode('utf-8')
            body = body.encode('utf-8')
            years[repr(dt_obj.year)][dt_obj.month-1].append((row[0], title, body, row[3]))
    db.close()
    year(years)
    f.close

def year(years):
    for key in sorted(years.keys()):
        (jan,feb,mar,apr,mai,jun,jul,aug,sep,okt,nov,dez) = years[key]
        # print years
        if len(jan)+len(feb)+len(mar)+len(apr)+len(mai)+len(jun)+len(jul)+len(aug)+len(sep)+len(okt)+len(nov)+len(dez) > 0:
            f.write("\chapter{"+ key + "}\n")
            # print months
            if len(jan) > 0:
                f.write("\section{Januar " + key + "}\n")
                month(jan)
            if len(feb) > 0:
                f.write("\section{Februar " + key + "}\n")
                month(feb)
            if len(mar) > 0:
                f.write("\section{M{\\\"a}rz " + key + "}\n")
                month(mar)
            if len(apr) > 0:
                f.write("\section{April " + key + "}\n")
                month(apr)
            if len(mai) > 0:
                f.write("\section{Mai " + key + "}\n")
                month(mai)
            if len(jun) > 0:
                f.write("\section{Juni " + key + "}\n")
                month(jun)
            if len(jul) > 0:
                f.write("\section{Juli " + key + "}\n")
                month(jul)
            if len(aug) > 0:
                f.write("\section{August " + key + "}\n")
                month(aug)
            if len(sep) > 0:
                f.write("\section{September " + key + "}\n")
                month(sep)
            if len(okt) > 0:
                f.write("\section{Oktober " + key + "}\n")
                month(okt)
            if len(nov) > 0:
                f.write("\section{November " + key + "}\n")
                month(jan)
            if len(nov) > 0:
                f.write("\section{Dezember " + key + "}\n")
                month(dez)
            f.write("\n\n\n\\clearpage")

def month(month):
    for (id, title, body, timestamp) in month:
        f.write("\subsection{" + title + "}\n")
        f.write(bodyCleaning(body, title)+"\n\n")

def bodyCleaning(body, title):
    img = re.compile('<img src="{}([^"]+)"')
    cleanedBody = body
    for tag in img.finditer(cleanedBody):
        cleanedURL = tag.group(1).replace('{}','').replace("\_","_").replace("\%","%")
        # print title + ": " + cleanedURL
        urllib.urlretrieve(cleanedURL, "images/" + os.path.basename(cleanedURL))
        if os.path.splitext(cleanedURL)[1] != ".gif":
            escapedURL = cleanedURL.replace("_","\_").replace("%","\%")
            cleanedBody = re.sub('<img src="{}([^"]+)"[{}\s]* />', "\n\n \\begin{figure}[ht]\\centering\\href{" + escapedURL + "}{\\includegraphics[width=1.0 \\textwidth]{" + "images/" + os.path.basename(escapedURL.replace("%","\%")) + "}}\\caption{" + title + "}\\end{figure}\n\n", body, 1)

    ahref = re.compile('<a href="([^"]+)"')
    for tag in ahref.finditer(cleanedBody):
        cleanedURL = tag.group(1).replace('{}','')
        print title + ": " + cleanedURL
        cleanedBody = cleanedBody + "\n \\\\ \\href{" + cleanedURL + "}{Link}"

    cleanedBody = re.sub('<[^<]+?>', '', cleanedBody)
    html_escape_table = {
        "&amp;":"\&",
        "&quot;":'"{}',
        "&apos;":'"{}',
        "&gt;":">",
        "&lt;":"<",
        "&nbsp;":" ",
        "&#699;":"'",
        "&#31069;":"",#祝
        "&#25105;":"",#我
        "&#22909;":"",#好
        "&#36816;":"",#运
    }
    cleanedBody = unescape(cleanedBody, html_escape_table)
    return cleanedBody
db()
