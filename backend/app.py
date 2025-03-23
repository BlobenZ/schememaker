from PIL import Image, ImageFont, ImageDraw
import json
import os
from flask import Flask, send_file, request, send_from_directory
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_folder="../build", static_url_path="/")
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def textsize(draw, text, font):
    im = Image.new(mode="P", size=(0, 0))
    draw = ImageDraw.Draw(im)
    _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
    return width, height

def getSchedule(file):
    schedule = []
    date = ""
    with open(file, encoding="utf-8") as f:
        data = json.load(f)
        for time in data:
            if time != "date":
                schedule.append([data[time]["divison"], data[time]["team1"], data[time]["team2"]])
            else:
                date = data[time].upper()
    return schedule, date

def getFileFromName(name):
    path = "./TeamLogos/"
    files = [i for i in os.listdir(path) if os.path.isfile(os.path.join(path,i)) and name.lower() in i.lower()]
    return files[0]

def getTRIFromName(name):
    file = getFileFromName(name)
    #Should only be one file
    triWithFile = file.split('-')[1]
    tri = triWithFile.split('.')[0]
    return tri.strip().upper()

def data_to_json(date, d_1, t1_1, t2_1,d_2, t1_2, t2_2,d_3, t1_3, t2_3,d_4, t1_4, t2_4):
    data = {}
    data["date"] = date
    data["18:30"] = {
        "division": d_1,
        "team1":    t1_1,
        "team2":    t2_1
    }
    data["19:30"] = {
        "division": d_2,
        "team1":    t1_2,
        "team2":    t2_2
    }
    data["20:30"] = {
        "division": d_3,
        "team1":    t1_3,
        "team2":    t2_3
    }
    data["21:30"] = {
        "division": d_4,
        "team1":    t1_4,
        "team2":    t2_4
    }
    return data

def getScheduleFromData(data):
    print(data)
    schedule = []
    date = ""
    for time in data:
        if time != "date":
            print(data[time])
            schedule.append([data[time]["division"], data[time]["team1"], data[time]["team2"]])
        else:
            date = data[time].upper()
    return schedule, date

@app.route("/")
def home():
    print("Return home page")
    print(app.static_folder + "/index.html")
    print(send_from_directory(app.static_folder, "index.html"))
    return send_from_directory(app.static_folder, "index.html")

@app.route("/teamnames/")
def get_team_names():
    path = "./TeamLogos/"
    print(os.listdir(path))
    print(app.static_folder + "../bnackend/TeamLogos/")
    print(os.listdir(app.static_folder))
    print(os.listdir(app.static_folder + "../bnackend/TeamLogos/"))
    files = [i for i in os.listdir(path) if os.path.isfile(os.path.join(path,i))]
    print(files)
    return files

@app.route("/generate")
def generate_scheme():
    date = request.args.get('date')
    d_1 = request.args.get('1d')
    t1_1 = request.args.get('1t1')
    t2_1 = request.args.get('1t2')
    d_2 = request.args.get('2d')
    t1_2 = request.args.get('2t1')
    t2_2 = request.args.get('2t2')
    d_3 = request.args.get('3d')
    t1_3 = request.args.get('3t1')
    t2_3 = request.args.get('3t2')
    d_4 = request.args.get('4d')
    t1_4 = request.args.get('4t1')
    t2_4 = request.args.get('4t2')

    #Base image info
    img_width, img_height = 1400, 1080
    baseScheme = Image.open('template.png')
    draw = ImageDraw.Draw(baseScheme)

    #Colors
    divisionTextColor = 10, 10, 10
    teamNameTextColor = 255, 255, 255
    dateTextColor = 199, 155, 59

    #Fonts
    font_teams_tri = ImageFont.truetype("Fonts/Oswald-Bold.ttf", 54)
    font_teams = ImageFont.truetype("Fonts/Oswald-Regular.ttf", 26)
    font_division = ImageFont.truetype("Fonts/Oswald-SemiBold.ttf", 28)
    font_date = ImageFont.truetype("Fonts/Oswald-Medium.ttf", 35)

    #Get todays stream data
    stream, date = getScheduleFromData(data_to_json(date, d_1, t1_1, t2_1,d_2, t1_2, t2_2,d_3, t1_3, t2_3,d_4, t1_4, t2_4))

    #Print date
    t_width, t_height = textsize(draw, date, font_date)
    datePos = (24, 186)
    draw.text(datePos, date, dateTextColor, font=font_date)

    #Print divisions
    divisionTextPosMargin = 15
    divisionYPos = [212 + divisionTextPosMargin, 393 + divisionTextPosMargin, 575 + divisionTextPosMargin, 764 + divisionTextPosMargin]
    for game in stream:
        text = "DIVISION " + game[0].upper()
        t_width, t_height = textsize(draw, text, font_division)
        text_division_1_pos = ((img_width / 2) - (t_width / 2), divisionYPos[stream.index(game)])
        draw.text(text_division_1_pos, text, divisionTextColor, font=font_division)

    #Print tri codes
    triYPosMargin = 6
    triYPos = [228 + triYPosMargin, 409 + triYPosMargin, 591 + triYPosMargin, 781 + triYPosMargin]
    for game in stream:
        #Left team
        text = getTRIFromName(game[1]).upper()
        t_width, t_height = textsize(draw, text, font_teams_tri)
        #Start 300 - End 600
        text_x_pos = 462 - (t_width / 2)
        text_pos = (text_x_pos, triYPos[stream.index(game)])
        draw.text(text_pos, text, teamNameTextColor, font=font_teams_tri)

        #Right team
        text = getTRIFromName(game[2]).upper()
        t_width, t_height = textsize(draw, text, font_teams_tri)
        #Start 790 - End 1050
        text_x_pos = 928 - (t_width / 2)
        text_pos = (text_x_pos, triYPos[stream.index(game)])
        draw.text(text_pos, text, teamNameTextColor, font=font_teams_tri)

    #Print team name
    teamYPosMargin = 8
    teamYPos = [305 + teamYPosMargin, 486 + teamYPosMargin, 668 + teamYPosMargin, 857 + teamYPosMargin]
    for game in stream:
        #Left team
        text = game[1].upper()
        t_width, t_height = textsize(draw, text, font_teams)
        #Start 300 - End 600
        text_x_pos = 462 - (t_width / 2)
        text_pos = (text_x_pos, teamYPos[stream.index(game)])
        draw.text(text_pos, text, teamNameTextColor, font=font_teams)

        #Right team
        text = game[2].upper()
        t_width, t_height = textsize(draw, text, font_teams)
        #Start 790 - End 1050
        text_x_pos = 925 - (t_width / 2)
        text_pos = (text_x_pos, teamYPos[stream.index(game)])
        draw.text(text_pos, text, teamNameTextColor, font=font_teams)

    #Print team logos
    logoYPos = [280, 450, 640, 830]
    for game in stream:
        base_width = 150
        #Left side
        teamLogo = Image.open('TeamLogos/' + getFileFromName(game[1]))
        wpercent = (base_width / float(teamLogo.size[0]))
        hsize = int((float(teamLogo.size[1]) * float(wpercent)))
        teamLogo = teamLogo.resize((base_width, hsize), Image.Resampling.LANCZOS)
        baseScheme.paste(teamLogo, (200, logoYPos[stream.index(game)] - (int((float(teamLogo.size[1]))) // 2)), mask=teamLogo)
        #Right side
        teamLogo = Image.open('TeamLogos/' + getFileFromName(game[2]))
        wpercent = (base_width / float(teamLogo.size[0]))
        hsize = int((float(teamLogo.size[1]) * float(wpercent)))
        teamLogo = teamLogo.resize((base_width, hsize), Image.Resampling.LANCZOS)
        baseScheme.paste(teamLogo, (1050, logoYPos[stream.index(game)] - (int((float(teamLogo.size[1]))) // 2)), mask=teamLogo)

    dateString = date.lower().replace(' ', '-')
    baseScheme.save(f'scheme-{dateString}.png')

    try:
        return send_file(f'./scheme-{dateString}.png', download_name="scheme.png", as_attachment=True)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    app.run()