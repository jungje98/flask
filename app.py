import os
import uuid
import flask
import urllib

from PIL import Image
from tensorflow.keras.models import load_model
from flask import Flask, render_template, request, send_file
from tensorflow.keras.preprocessing.image import load_img, img_to_array

import os
from gtts import gTTS
import playsound

import pymysql


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(BASE_DIR, '3rd_densenet201_1.h5'))


ALLOWED_EXT = set(['jpg', 'jpeg', 'png'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT


classes = ['바나나킥', '포카칩', '화이트하임', '양파링', '오레오', '아몬드 빼빼로', '후렌치파이', '벌집핏자', '새우깡', '꼬북칩']


def predict(filename, model):
    img = load_img(filename, target_size = (75, 75))
    img = img_to_array(img)
    img = img.reshape(1, 75, 75, 3)

    img = img.astype('float32')
    img = img/255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(10):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[ : : -1]
    prob = res[:3]
    
    prob_result = []
    class_result = []
    for i in range(3):
        prob_result.append((prob[i]*100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result, prob_result


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/success', methods = ['GET', 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd() , 'static/images')
    if request.method == 'POST':
        if(request.form):
            link = request.form.get('link')
            try :
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img , filename)
                output = open(img_path , "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result, prob_result = predict(img_path , model)

                predictions = {
                      "class1": class_result[0],
                        "class2": class_result[1],
                        "class3": class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                }

                # TTS
                snack_name = 'snack_name.mp3'
                name_tts = gTTS(text = class_result[0], lang = 'ko')
                name_tts.save("./static/" + snack_name)

                snack_info = 'snack_info.mp3'
                info_tts = gTTS(text = prob_result[0], lang = 'ko')
                info_tts.save("./static/" + snack_info)


                # sql 연동

                db = pymysql.connect(host = 'localhost', user = 'root', db = 'snack', password = '0516', charset='utf8')
                cur = db.cursor()

                sql = "SELECT * from sn_info"
                cur.execute(sql)

                data_list = cur.fetchall()

                return render_template('success.html', data_list = data_list)



            except Exception as e: 
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if(len(error) == 0):
                return  render_template('success.html', img = img , predictions = predictions)
            else:
                return render_template('home.html', error = error) 

            
        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img , file.filename))
                img_path = os.path.join(target_img , file.filename)
                img = file.filename

                class_result , prob_result = predict(img_path , model)

                predictions = {
                      "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                }


            else:
                error = "Please upload images of jpg, jpeg, heic and png extension only"

            if(len(error) == 0):
                return  render_template('success.html', img  = img , predictions = predictions)
            else:
                return render_template('home.html', error = error)

    else:
        return render_template('home.html')


if __name__ == "__main__":
    app.run(debug = True)