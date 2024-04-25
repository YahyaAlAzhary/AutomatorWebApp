import datetime
from pytz import timezone
import random
import gspread
import time
import sys
import re
import calendar
from google.oauth2 import service_account
from googleapiclient.discovery import build
from Automator import JointUpdates


class AgeException(Exception):
    def __init__(self, message="Invalid age"):
        super().__init__(message)


class MedicareIDException(Exception):
    def __init__(self, message="Invalid Medicare ID"):
        super().__init__(message)


class ShoeSizeException(Exception):
    def __init__(self, message="Shoe size not found"):
        super().__init__(message)


def age(birthdate):
    today = datetime.date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age


def generate_random_ip():
    return '.'.join(
        str(random.randint(0, 255)) for _ in range(4)
    )


def generate_random_time():
    tz = timezone('EST')
    current_datetime = datetime.datetime.now(tz)

    # Create a timedelta representing the shifts
    minutes_shift = datetime.timedelta(minutes=(random.randint(10, 30)))

    result = (current_datetime - minutes_shift).strftime("%I:%M:%S %p")
    hours, minutes, seconds = result.split(':')
    if int(hours) < 8 and seconds.__contains__("AM"):
        hours = 8
    if int(hours) >= 5 and seconds.__contains__("PM"):
        hours = 4

    if len(str(hours)) == 1:
        hours = '0' + str(hours)

    if len(str(minutes)) == 1:
        minutes = '0' + str(minutes)

    if len(str(seconds)) == 1:
        seconds = '0' + str(seconds)

    return f"{hours}:{minutes}:{seconds}"


def isValid(input):
    pattern = re.compile("[^0-9]")
    return not bool(pattern.search(input))


def validElem(x, start):
    if isValid(x[start].strip()):
        return x[start].strip()
    start += 1
    if isValid(x[start].strip()):
        return x[start].strip()
    start += 1
    if isValid(x[start].strip()):
        return x[start].strip()
    start += 1
    if isValid(x[start].strip()):
        return x[start].strip()
    start += 1
    if isValid(x[start].strip()):
        return x[start].strip()
    start += 1
    if isValid(x[start].strip()):
        return x[start].strip()


def mainjoint(sheetName, users, inputrow, credentials, service, drive_service, edits):
    users = [user.strip() for user in users]
    print(users)
    check_empty = False
    if "" in users:
        check_empty = True
    leads = {}
    # "dani"   "hs"   "mohammad"   "os"   "pankaj"
    inp = sheetName.lower()

    sheetsNames = {"dani": "Yahya Dani",
                   "hs": "my hs",
                   "mohammad": "My Muhammad Muzammil",
                   "os": "my outsourcing",
                   "pankaj": "My Pankaj"}

    sh = sheetsNames.get(inp)

    client = gspread.authorize(credentials)

    sheet = client.open(sh).sheet1

    values = sheet.get_all_values()
    if inputrow == "":
        rownum = 2
        x = None
        print("Running")
        sheetIf = {"hs": [1, 2, 34, 32],
                   "mohammad": [1, 3, 29, 2],
                   "os": [1, 2, 40, 38],
                   "pankaj": [0, 2, 34, 1]}
        for row in values[1:]:

            ifs = sheetIf.get(inp)

            if inp == "dani" and (row[3] != "") and (row[1] == ""):
                leads[rownum] = row

            elif (inp != "dani" and not row[ifs[0]].lower().__contains__("upl") and (row[ifs[1]] != "") and row[
                ifs[2]] != "done"
                  and row[ifs[3]].strip() in users and not check_empty):
                leads[rownum] = row

            elif (inp != "dani" and not row[ifs[0]].lower().__contains__("upl") and (row[ifs[1]] != "") and row[
                ifs[2]] != "done"
                  and check_empty and row[ifs[3]].strip() not in users):
                leads[rownum] = row
            rownum += 1

        if len(leads) == 0:
            return ["done"]
    else:
        leads[inputrow] = values[inputrow - 1]

    for rownum in leads:

        x = leads[rownum]

        sheets = {
            "dani": ['B', 16, 5, 6, 13, 9, 10, 11, 8, 12, 14, 15, 7, 17, 18, 26, 25, 27, 28, 3, 4,
                     20, 21, 22, 23, 24, "intermittent", '1u_Ui9mT-K2QeHGRtJI0W9borqJOaW2Io', "filler"],
            "hs": ['AI', 19, 7, 8, 15, 11, 12, 13, 10, 14, 16, 17, 9, 20, 18, 28, 27, 29, 30, 2, 6, 22, 23, 26, 24, 25,
                   'intermittent', '1-FxYZ0_tBDSSLxRqMr1iZ3u9YJuJZDtQ', 'filler'],
            "mohammad": ['AD', 16, 5, 6, 13, 9, 10, 11, 8, 12, 14, 15, 7, 17, 18, 26, 25,
                         27, 28, 3, 4, 20, 21, 22, 23, 24, "intermittent", '1leDl1DQLnvP2eXc5wZuHP-5ihHeVOVTW',
                         "filler"],
            "os": ['AO', 18, 7, 8, 15, 11, 12, 13, 10, 14, 16, 17, 9, 19, 20, 28, 27, 29, 30,
                   2, 6, 22, 23, 24, 25, 26, x[32].strip(), '1GaywPLW27xmRlRxtEcmZKfgqZenCSzLL', x[31]],
            "pankaj": ['AI', 20, 4, 5, 12, 8, 9, 10, 7, 11, 18, 19, 6, 21, 22, 31, 30, 32, 33, 2,
                       3, 24, 25, 26, 27, 28, "intermittent", '1vhvGahmDDKFa8aH_Z61Z_aLRAHbs-J6f', "filler"]}

        sh = sheets.get(inp)

        cell = sh[0] + str(rownum)

        # patient's shoe size
        patshoesize = edits.get("patshoesize", x[sh[1]].strip())

        # patient's name
        FirstName = x[sh[2]].strip()
        LastName = x[sh[3]].strip()

        doubleSpacePattern = re.compile("\s\s+")
        patname = doubleSpacePattern.sub(" ", (f"{FirstName} {LastName}".title()))
        patname = edits.get("patname", patname)
        print(patname)

        # patient's id
        MIDpattern = re.compile("^[0-9][A-Z][A-Z0-9][0-9][A-Z][A-Z0-9][0-9][A-Z]{2}[0-9]{2}$")
        patmed = edits.get('patmed', x[sh[4]].strip().upper())
        if not bool(MIDpattern.match(patmed)):
            raise MedicareIDException

        # patient's city,state,zipcode
        city = edits.get('patcity', x[sh[5]].replace(',', '').strip())

        statePattern = re.compile("[A-Z]{2}")
        state = edits.get('patstate', x[sh[6]].upper())
        state = statePattern.search(state).group()

        zipcodePattern = re.compile("[^0-9-]")
        zipcode = edits.get('patzipcode', zipcodePattern.sub(" ", x[sh[7]])).strip()
        zipcodePattern.sub(" ", x[sh[7]])
        patadd2 = city + ', ' + state + ", " + zipcode

        # patient's street address
        patadd1 = edits.get('patadd1', x[sh[8]].strip())
        if patadd1.__contains__(zipcode):
            patadd1 = patadd1.split(city)
            patadd1 = patadd1[0].rstrip()
        patadd1 = doubleSpacePattern.sub(" ", patadd1)

        # patient's city/state/zipcode
        patadd3 = city + ' / ' + state + " / " + zipcode

        # patient's phone number
        patphone = edits.get('patphone', x[sh[9]].strip())

        # patient's height
        patht = edits.get('patht', x[sh[10]].strip().lower())
        pathtPattern = re.compile("([A-Za-z])|([^0-9]$)")
        patht = pathtPattern.sub("", patht)

        # patient's weight
        patwt = edits.get('patwt', x[sh[11]].strip())

        # patient's date of birth
        baddob = edits.get('patdob', x[sh[12]].strip())
        month_mapping = {
            "jan": "January",
            "f": "February",
            "mar": "March",
            "ap": "April",
            "jun": "June",
            "jul": "July",
            "au": "August",
            "s": "September",
            "o": "October",
            "n": "November",
            "d": "December"
        }

        MonthNamePattern = re.compile("^([a-zA-Z]+)[^0-9]+([0-9]{1,2})[^0-9]+([0-9]{4})$")
        MonthNumPattern = re.compile("^([0-9]{1,2})[^0-9]+([0-9]{1,2})[^0-9]+([0-9]{4})$")

        if bool(MonthNamePattern.search(baddob)):
            month = MonthNamePattern.search(baddob).group(1).lower()

            for prefix, month_name in month_mapping.items():
                if month.startswith(prefix):
                    month = month_name

            day = MonthNamePattern.search(baddob).group(2)
            year = MonthNamePattern.search(baddob).group(3)

        elif bool(MonthNumPattern.search(baddob)):
            month = MonthNumPattern.search(baddob).group(1)
            month = calendar.month_name[int(month)]
            day = MonthNumPattern.search(baddob).group(2)
            year = MonthNumPattern.search(baddob).group(3)
        else:
            print("DOB format is wrong in sheet")
            return ["age", patname, sheetName, rownum]

        patdob = month + " " + day + " " + year
        nummonth = list(calendar.month_name).index(month.capitalize())
        # patient's age
        try:
            patage = age(datetime.date(int(year), nummonth, int(day)))
        except (ValueError, TypeError):
            print("DOB format is wrong in sheet")
            return ["age", patname, sheetName, rownum]

        # patient's gender
        patgender = edits.get('patgender', x[sh[13]].lower().strip())
        if patgender.lower().__contains__('f'):
            patgender = "Female"
        else:
            patgender = "Male"

        # patient's waist size
        patsizew = edits.get('patsizew', x[sh[14]].upper().strip())

        # current est time
        pattime = edits.get('pattime', generate_random_time())

        # patient's order date
        nowMonth = str(datetime.date.today().month)
        nowDay = str(datetime.date.today().day)
        nowYear = str(datetime.date.today().year)
        if len(nowMonth) == 1:
            nowMonth = '0' + nowMonth
        if len(nowDay) == 1:
            nowDay = '0' + nowDay
        if pattime.__contains__("PM") and datetime.datetime.now().strftime("%I:%M:%S %p").__contains__("AM"):
            nowDay = int(nowDay) - 1
        patorderdate = f"{nowMonth}-{nowDay}-{nowYear}"
        patorderdate = patorderdate.replace(nowYear, nowYear[2:])
        patorderdate = edits.get('patorderdate', patorderdate)

        # patient's tried treatments
        patpaintr = edits.get('patpaintr', x[sh[15]].strip().lower())
        if patpaintr == "no" or patpaintr == "na" or patpaintr == "none":
            patpaintr = "Nothing"

        # patient's pain duration
        patpainyear = edits.get('patpainyear', x[sh[16]].lower().strip())
        if patpainyear.isnumeric():
            patpainyear = patpainyear + " years"
        patpainyear.replace("yrs", " years")
        patpainyear.replace("yearss", "years")
        patpainyear = doubleSpacePattern.sub(" ", patpainyear)
        patpainyear.replace("a year", "1 year")

        if patpainyear.startswith("since ") and patpainyear[6:].isdigit():
            year = datetime.date.today().year - int(patpainyear[6:])
            patpainyear = str(year) + " years"
        elif patpainyear.startswith("from ") and patpainyear[5:].isdigit():
            year = datetime.date.today().year - int(patpainyear[5:])
            patpainyear = str(year) + " years"
        else:
            patpainyear = patpainyear.replace("since", "")
            patpainyear = patpainyear.replace("for", "")
            patpainyear = patpainyear.replace('ago', "")
            patpainyear = patpainyear.replace("monthes", "months")
            patpainyear = patpainyear.strip()
            if patpainyear == "more the year":
                patpainyear = "more than 1 year"
            elif patpainyear in ['years', "many years", "couple years", "couple of years", "long time", "few years",
                                 "some years"]:
                patpainyear = 'Several years'
            elif patpainyear in ["year", "1 years", "a year", "last year"]:
                patpainyear = "1 year"
            elif patpainyear == "months":
                patpainyear = "Several months"
            else:
                num = ''
                for i in patpainyear:
                    if i.isnumeric():
                        num += i
                if (not patpainyear.__contains__("years") and not patpainyear.__contains__(
                        "year")) and patpainyear.__contains__("y") and num.isnumeric():
                    if int(num) > 1:
                        patpainyear = patpainyear.replace("y", " years")
                    else:
                        patpainyear = patpainyear.replace("y", " year")
                if num == "1":
                    patpainyear = patpainyear.replace("months", "month")
                    patpainyear = patpainyear.replace("years", "year")
                elif (num.isnumeric() and int(num) > 1 and (not patpainyear.__contains__("years")) and
                      (not patpainyear.__contains__("months"))):
                    patpainyear = patpainyear.replace("month", "months")
                    patpainyear = patpainyear.replace("year", "years")

        # what increases the patient's pain
        patpainworse = edits.get('patpainworse', x[sh[17]].strip())
        weatherPainPattern = re.compile("[^a-zA-Z]+\s[Ww]eather")

        if bool(weatherPainPattern.search(" " + patpainworse)):
            patpainworse.replace("weather", "bad weather")
            patpainworse.replace("Weather", "bad weather")

        if patpainworse.lower() == "na":
            patpainworse = "Nothing"

        # patient's cause of pain
        patpaincause = edits.get('patpaincause', x[sh[18]].strip().lower())
        patpaincause = patpaincause.replace('arthiritis', 'arthritis').replace('arthrities', 'arthritis')
        if patpaincause.__contains__("age") and not patpaincause.__contains__("old age"):
            patpaincause = patpaincause.replace('age', 'old age')

        arthPattern = re.compile("arth[a-z]*", re.IGNORECASE)
        patpaincause = arthPattern.sub('arthritis', patpaincause)

        # patient's ip address
        patipadd = generate_random_ip()

        sheetsElbow = {"dani": x[25].strip(),
                       "hs": "0",
                       "mohammad": validElem(x, 19),
                       "os": x[sh[24]].strip(),
                       "pankaj": x[25].strip()}

        codes = edits.get("lcodes", x[sh[19]].replace(" ", "").upper())
        rstring = edits.get('requestBraces', x[sh[20]].lower().replace("wirst", "wrist").replace("writs", "wrist"))
        rstring = " " + rstring
        requestedBraces = []
        Lcodes = []
        direction = []
        painlevel = []
        BackPain = x[sh[21]].strip()
        KneePain = x[sh[22]].strip()
        ShoulderPain = x[sh[23]].strip()
        WristPain = x[sh[24]].strip()
        AnklePain = x[sh[25]].strip()
        ElbowPain = sheetsElbow.get(inp)
        randomlevel = validElem(x, sh[21])

        hipPain = randomlevel

        leftKneePattern = re.compile("[^a-zA-Z][Ll][a-zA-Z]*[^a-zA-Z]+[Kk][a-zA-Z]*" + "|" + "[^a-zA-Z]LKB")
        rightKneePattern = re.compile("[^a-zA-Z][Rr][a-zA-Z]*[^a-zA-Z]+[Kk][a-zA-Z]*")
        bothKneesPattern = re.compile("[^a-zA-Z][Bb][^a][a-zA-Z]*[^a-zA-Z]+[Kk][a-zA-Z]*")

        leftWristPattern = re.compile("[^a-zA-Z][Ll][a-zA-Z]*[^a-zA-Z]+[Ww][a-zA-Z]*")
        rightWristPattern = re.compile("[^a-zA-Z][Rr][a-zA-Z]*[^a-zA-Z]+[Ww][a-zA-Z]*")
        bothWristsPattern = re.compile("[^a-zA-Z][Bb][^a][a-zA-Z]*[^a-zA-Z]+[Ww][a-zA-Z]*")

        leftAnklePattern = re.compile("[^a-zA-Z][Ll][a-zA-Z]*[^a-zA-Z]+[Aa][a-zA-Z]*")
        rightAnklePattern = re.compile("[^a-zA-Z][Rr][a-zA-Z]*[^a-zA-Z]+[Aa][a-zA-Z]*")
        bothAnklesPattern = re.compile("[^a-zA-Z][Bb][^a][a-zA-Z]*[^a-zA-Z]+[Aa]nk[a-zA-Z]*")

        leftShoulderPattern = re.compile("[^a-zA-Z][Ll][a-zA-Z]*[^a-zA-Z]+[Ss][a-zA-Z]*")
        rightShoulderPattern = re.compile("[^a-zA-Z][Rr][a-zA-Z]*[^a-zA-Z]+[Ss][a-zA-Z]*")
        bothShouldersPattern = re.compile("[^a-zA-Z][Bb][^a][a-zA-Z]*[^a-zA-Z]+[Ss][a-zA-Z]*")

        leftElbowPattern = re.compile("[^a-zA-Z][Ll][a-zA-Z]*[^a-zA-Z]+[Ee][a-zA-Z]*")
        rightElbowPattern = re.compile("[^a-zA-Z][Rr][a-zA-Z]*[^a-zA-Z]+[Ee][a-zA-Z]*")
        bothElbowsPattern = re.compile("[^a-zA-Z][Bb][^a][a-zA-Z]*[^a-zA-Z]+[Ee][a-zA-Z]*")

        leftHipPattern = re.compile("[^a-zA-Z][Ll][a-zA-Z]*[^a-zA-Z]+[Hh][a-zA-Z]*")
        rightHipPattern = re.compile("[^a-zA-Z][Rr][a-zA-Z]*[^a-zA-Z]+[Hh][a-zA-Z]*")
        bothHipsPattern = re.compile("[^a-zA-Z][Bb][^a][a-zA-Z]*[^a-zA-Z]+[Hh][a-zA-Z]*")

        backLcodePattern = re.compile("[Ll](06|04)[0-9]{2}")
        kneeLcodePattern = re.compile("[Ll]18[0-9]{2}")
        wristLcodePattern = re.compile("[Ll]3916")
        ankleLcodePattern = re.compile("[Ll]19[0-9]{2}")
        shoulderLcodePattern = re.compile("[Ll](36|3960)[0-9]{0,2}")
        elbowLcodePattern = re.compile("[Ll](37|3960)[0-9]{0,2}")
        hipLcodePattern = re.compile("[Ll]16[0-9]{2}")

        patterns_dict = {
            leftKneePattern: [kneeLcodePattern, "left", "left knee", KneePain],
            rightKneePattern: [kneeLcodePattern, "right", "right knee", KneePain],
            bothKneesPattern: [kneeLcodePattern, "both", "knee", KneePain],

            leftWristPattern: [wristLcodePattern, "left", "left wrist", WristPain],
            rightWristPattern: [wristLcodePattern, "right", "right wrist", WristPain],
            bothWristsPattern: [wristLcodePattern, "both", "wrist", WristPain],

            leftAnklePattern: [ankleLcodePattern, "left", "left ankle", AnklePain],
            rightAnklePattern: [ankleLcodePattern, "right", "right ankle", AnklePain],
            bothAnklesPattern: [ankleLcodePattern, "both", "ankle", AnklePain],

            leftShoulderPattern: [shoulderLcodePattern, "left", "left shoulder", ShoulderPain],
            rightShoulderPattern: [shoulderLcodePattern, "right", "right shoulder", ShoulderPain],
            bothShouldersPattern: [shoulderLcodePattern, "both", "shoulder", ShoulderPain],

            leftElbowPattern: [elbowLcodePattern, "left", "left elbow", ElbowPain],
            rightElbowPattern: [elbowLcodePattern, "right", "right elbow", ElbowPain],
            bothElbowsPattern: [elbowLcodePattern, "both", "elbow", ElbowPain],

            leftHipPattern: [hipLcodePattern, "left", "left hip", hipPain],
            rightHipPattern: [hipLcodePattern, "right", "right hip", hipPain],
            bothHipsPattern: [hipLcodePattern, "both", "hip", hipPain],
        }

        for pattern in patterns_dict:
            if bool(pattern.search(rstring)):
                array = patterns_dict[pattern]
                code = array[0].search(codes).group()
                Lcodes.append(code)
                if array[1] == "both":
                    Lcodes.append(code)
                    direction.append("left")
                    direction.append("right")
                    requestedBraces.append(f"left {array[2]}")
                    requestedBraces.append(f"right {array[2]}")
                    if isValid(array[3]):
                        painlevel.append(array[3])
                        painlevel.append(array[3])
                    else:
                        painlevel.append(randomlevel)
                        painlevel.append(randomlevel)
                else:
                    direction.append(array[1])
                    requestedBraces.append(array[2])
                    if isValid(array[3]):
                        painlevel.append(array[3])
                    else:
                        painlevel.append(randomlevel)

        if bool(backLcodePattern.search(codes)):
            direction.append("")
            requestedBraces.append("back")
            Lcodes.append(backLcodePattern.search(codes).group())
            painlevel.append(BackPain)

        # check if ankle is present then shoe size is present
        flag = False
        if "L1906" in Lcodes or "L1971" in Lcodes:
            for char in patshoesize:
                if char.isnumeric() and 1 <= int(char) <= 9:
                    flag = True
            if not flag:
                print("Shoe Size not found")
                return ["shoe", patname, sheetName, rownum]

        print(requestedBraces)

        # patient's pain levels

        PainFrequency = edits.get('painfrequency', sh[26].strip())
        PainFrequency = PainFrequency.lower().replace("everyday", "daily")
        if PainFrequency == "" or PainFrequency == "comes and goes":
            PainFrequency = "intermittent"

        destination_folder = sh[27]

        patinjury = "Negative"
        patsurgery = "Negative"
        patbend = "Positive"
        patweakness = "Positive"
        pattwist = "Negative"
        pattogether = "Negative"
        patoneleg = "Negative"
        patstatus = edits.get('patstatus', sh[28].lower())

        if (patpaincause.lower().__contains__("injur") or patpaincause.lower().__contains__("accident") or
                patstatus.__contains__("injur")):
            patinjury = "Positive"

        if patpaincause.lower().__contains__("surg") or patstatus.__contains__("surg"):
            patsurgery = "Positive"

        if patstatus.__contains__("both"):
            patinjury = "Positive"
            patsurgery = "Positive"

        if inp == "os":
            patweakness = "Negative"

            if (x[33].lower().strip() == "negative" or x[33].lower().strip() == "-" or
                    x[33].lower().strip() == ""):
                patbend = "Negative"

            if x[34].lower().strip().__contains__('p'):
                patweakness = "Positive"

            if x[35].lower().strip().__contains__('p'):
                pattwist = "Positive"

            if x[36].lower().strip().__contains__('p'):
                pattogether = "Positive"

            if x[37].lower().strip().__contains__('p'):
                patoneleg = "Positive"

        # Doctor Getter
        sheet2 = client.open('Doctors Sheet').sheet1
        values = sheet2.get_all_values()
        i = random.randint(1, len(values) - 1)
        temp = ''
        letter = 0

        state = state.strip()

        letters_only = ""
        for char in state:
            if char.isalpha():
                letters_only += char
        state = letters_only
        print("looping")
        start_time = time.time()
        while True:
            if values[i][1].lower().__contains__(state.lower()):
                break
            else:
                i = random.randint(1, len(values) - 1)
            if time.time() - start_time > 5:
                print("No Doctor found")
                sys.exit()

        row = values[i]
        drname = edits.get('drname', row[2].strip())
        drsigname = edits.get('drsigname', row[3].strip())
        npidr = edits.get('npidr', row[4].strip())
        dradd2 = edits.get('dradd2', row[6].strip())
        dradd3 = edits.get('dradd3', row[7].strip())
        dradd4 = edits.get('dradd4', row[8].strip())
        if ((inp == "os" and x[3].lower().strip() != "old one") or (inp == "hs" and x[4].lower().strip() == "remote") or
                (inp == "dani" and x[30] == "doctor phone")):
            drphone = row[9].strip()
        else:
            drphone = "800.204.1227"
        drphone = edits.get('drphone', drphone)

        index = 0
        while index < len(requestedBraces):

            # dict,,, brace: [folder for copy, standard file id]
            source = {'back': ["167G2A-Qv2_bCcSX5tiEqGVZw6D9Bw-zN",
                               "13lBRUk6qtCFN0v1ZIz8HaB3C0sr49wGUBRPRAq1YU68"],
                      'right knee': ["1k7rgqFEnXBJTmoCMop3WjyZQRroOiyiL",
                                     "1o-5Hr17dspLKjgWs0Pu3n6l6PIN5ipXbTn7TIKwhCoo"],
                      'left knee': ["1z206-SY9OBiJDKHVlC3A4UDrLHWYP6Om",
                                    "18G-IMgeGTQr7OsD2bzxrRY72soRl7KGSbyXinzMcp_0"],
                      'right wrist': ["1OTDQRCy3Pe0Tdr48Vwd0iy8_ICGdMEdw",
                                      "1Rc_sYaMYGum6loh89CT5kisDblwRw6ukkMpHGISQRvw"],
                      'left wrist': ["18DZetvbFrkmbvp7IZxCltN9Oufkkg-0H",
                                     "1JbBJKxFqT7-VrlVdOL5eRnI_m0T7tUobTpWODdYSY5E"],
                      'right ankle': ["1Ulcb0Q32xjXutlDhZid1vRMwwRiCQaje",
                                      "1WEbTY8Cr2emVo7GYrm9K0TXt1Jx2VQG02IsGnawnq9c"],
                      'left ankle': ["1SCjSwU6sGe4Xx5YcOpzd5lH19xV19SUM",
                                     "11UjQp8wcsQWzpQugdVZYi1tn-5tOT7sjof27xxRktFM"],
                      'right shoulder': ["1RQf2JVVC_ymke3G9GAMpzIlpSq5BGY5e",
                                         "16gJ7emB2OWegavmhZ5p0lXdbHXO2_QlngXcD2Gdw00A"],
                      'left shoulder': ["1f6GYXQc9FtMM5Onc1yb3wSEeksO3dByy",
                                        "1vSSHr5tjTmuSBhmfokExB1bn5gmV3_4ZHbcBLrhR0jw"],
                      'right elbow': ["1p5lLo3YIa5WtEIBKgS9UTNs_alNool57",
                                      "1h_g0LhjL4l3_22RqtxrWlk4Kp7L0_4NbQWa4XsVLS2A"],
                      'left elbow': ["1h26GSNqAGiCfl-8UwxGvTs_bunwoyZd0",
                                     "1sZdNGbSUO5xA33ED6UtIcT-f06EF_do8m9OZMoCbC9A"],
                      'left hip': ["1TT8yzwsd1tcSe_WjUTTQfAMq7PI6awNo",
                                   "12H6758iiq41-Moou24VDok4vafXbAzl4nTqvSMP0Al8"],
                      'right hip': ["1BXJNrFci9dGBE8UnIfuxKDWK1UtTpFiu",
                                    "1bN510bULDloMuNEvMG8PtDLD3EB_M1qOzz44fq90XLw"]}

            source_folder_id = (source.get(requestedBraces[index]))[0]

            patpainlevel = painlevel[index]
            code = Lcodes[index]

            def copy_file(file_id, new_folder_id):
                copied_file = {
                    'parents': [new_folder_id]
                }
                output = drive_service.files().copy(fileId=file_id, body=copied_file).execute()
                return output

            copiedFile = copy_file((source.get(requestedBraces[index]))[1], source_folder_id)

            # Specify the folder IDs
            destination_folder_id = destination_folder

            # Get the list of files in the source folder

            document_id = copiedFile['id']
            document_name = copiedFile['name']
            print(f"Selected document: {document_name} (ID: {document_id})")

            # Edit the document by replacing a list of words
            replacement_words = [drname, drsigname, npidr,
                                 dradd2, dradd3, dradd4,
                                 patname, patmed, patadd1,
                                 patadd2, patadd3, str(patphone),
                                 str(patht), str(patwt), str(patage), patdob,
                                 patgender, str(patsizew),
                                 patorderdate, patpaintr, str(patpainlevel),
                                 patpainyear, patpainworse,
                                 patpaincause, patipadd, str(patshoesize),
                                 code, code, code, code, PainFrequency, patinjury,
                                 patsurgery, patbend, patweakness, pattwist,
                                 pattogether,
                                 patoneleg, pattime, drphone]

            words_to_replace = ['drname', 'drsigname', 'npidr', 'dradd2', 'dradd3', 'dradd4', 'patname', 'patmed',
                                'patadd1', 'patadd2', 'patadd3', 'patphone', 'patht', 'patwt', 'patage', 'patdob',
                                'patgender', 'patsizew', 'patorderdate', 'patpaintr', 'patpainlevel', 'patpainyear',
                                'patpainworse', 'patpaincause', 'patipadd', 'patshoesize', 'L0651', "L1852",
                                "L1971",
                                "L3960", 'intermittent', 'patinjury', 'patsurgery', 'patbend', 'patweakness',
                                'pattwist',
                                'pattogether', 'patoneleg', 'pattime', '800.204.1227']

            # Replace words in the document content
            requests = []
            for i in range(len(words_to_replace)):
                request = {
                    'replaceAllText': {
                        'containsText': {
                            'text': words_to_replace[i],
                            'matchCase': False
                        },
                        'replaceText': replacement_words[i]
                    }
                }
                requests.append(request)

            # Send the update requests to the document
            service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

            print('Words replaced successfully.')

            # Specify the file ID and new name
            file_id = document_id
            new_name = FirstName + "_" + LastName + "_" + code + "_" + direction[index]
            new_name = new_name.replace(" ", "_")

            # Update the file name
            file = {'name': new_name}
            updated_file = drive_service.files().update(fileId=file_id, body=file).execute()

            # Print the updated file name
            print(f"File renamed to: {updated_file['name']}")

            # Move the edited document to the destination folder
            file = drive_service.files().get(fileId=document_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))

            # Remove the document from its current folder(s)
            drive_service.files().update(fileId=document_id, addParents=destination_folder_id,
                                         removeParents=previous_parents).execute()

            print(f"The document '{new_name}' (ID: {document_id}) has been moved to the destination folder.")
            print()

            index += 1
        sheet = sheet
        sheet.update(cell, [["done"]])
    return ["done"]


if __name__ == "__mainjoint__":
    mainjoint('os', ["yy"])
