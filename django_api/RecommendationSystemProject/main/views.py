import datetime
import time
from django.shortcuts import render,HttpResponse
from django.http import JsonResponse


import jieba
import re
import heapq
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# 隱藏 warning (WARNING:tensorflow:9 out of the last 9 calls to <function nn_predict)
import logging
logger = tf.get_logger()
logger.setLevel(logging.ERROR)

# Create your views here.

def demo1(request):
    return render(request, 'main/demo1.html')
    
def demo2(request):
    return render(request, 'main/demo2.html')
    
def demo4(request):
    return render(request, 'main/demo4.html')
    
def getRecommendCategories(request):

    tStart = time.time()#計時開始
    
    customerText = request.GET['customerText']
    
    top_three_ensemble = nn_predict(customerText)

    tEnd = time.time()#計時結束
    
    html = "<html><body><p>It is now %s. 三個類別是: %s。 總共耗時: %s 秒</p><a href='/main/demo1'>Go back.</a></body></html>" % (datetime.datetime.now(), top_three_ensemble, tEnd - tStart)
    return HttpResponse(html)
    
def getRecommendCategoriesAjax(request):

    tStart = time.time()#計時開始
    
    customerText = request.GET['customerText']
    
    top_three_ensemble = nn_predict(customerText)

    tEnd = time.time()#計時結束
    
    # html = "<html><body>It is now %s. 三個類別是: %s。 總共耗時: %s 秒</body></html>" % (datetime.datetime.now(), top_three_ensemble, tEnd - tStart)
    # return HttpResponse(html)
    
    return JsonResponse({'recommendCategories':top_three_ensemble})
    
def getRecommendCategoriesAjaxByAudioFile(request):

    tStart = time.time()#計時開始
    
    # customerText = request.GET['customerText']
    audio_file = request.FILES.get('audio_file') # 目錄會產生一個files.wav資料夾
    with open('files.wav','wb') as fp:
        for chunk in audio_file.chunks():
            fp.write(chunk)
    import speech_recognition as sr
    r = sr.Recognizer()                        #預設辨識英文
    with sr.WavFile('files.wav') as source:  #讀取wav檔
        audio = r.record(source)
    try:
        # print("Transcription: " + r.recognize_google(audio,language="zh-TW"))
        print("Transcription: " + r.recognize_sphinx(audio,language="zh_cn"))
                                              #使用Google的服務
    except LookupError:
        print("Could not understand audio")
    # 會有英文，但是沒有標點符號，注意大小寫問題(已修正)
    
    # customerText = r.recognize_google(audio,language="zh-TW")
    customerText = r.recognize_sphinx(audio,language="zh_cn")
    
    top_three_ensemble = nn_predict(customerText)    

    tEnd = time.time()#計時結束
    

    print(tEnd - tStart)
    # return JsonResponse({'recommendCategories':top_three_ensemble}) # 先註解之後恢復
    
    # html = "<html><body><p>翻譯後字串為: %s </p><p>It is now %s. 三個類別是: %s。 總共耗時: %s 秒</p></body></html>" % (customerText, datetime.datetime.now(), top_three_ensemble, tEnd - tStart)
    # return HttpResponse(html)
    
    ans_text = "翻譯後字串為: %s " % (customerText,)
    ans_text2 = "It is now %s. 三個類別是: %s。 總共耗時: %s 秒" % (datetime.datetime.now(), top_three_ensemble, tEnd - tStart)
    
    context = {'ans_text': ans_text, 'ans_text2': ans_text2}
    return render(request, 'main/demo2.html', context)
    
def getRecommendCategoriesAjaxByAudio(request):

    tStart = time.time()#計時開始
    
    import speech_recognition as sr
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        # print("Transcription: " + r.recognize_google(audio,language="zh-TW"))
        print("Transcription: " + r.recognize_sphinx(audio,language="zh_cn"))
                                              #使用Google的服務
    except LookupError:
        print("Could not understand audio")
    # 會有英文，但是沒有標點符號，注意大小寫問題(已修正)
    
    # customerText = r.recognize_google(audio,language="zh-TW")
    customerText = r.recognize_sphinx(audio,language="zh_cn")
    
    top_three_ensemble = nn_predict(customerText)
    
    tEnd = time.time()#計時結束

    print(tEnd - tStart)
    # return JsonResponse({'recommendCategories':top_three_ensemble}) # 先註解之後恢復
    
    # html = "<html><body><p>翻譯後字串為: %s </p><p>It is now %s. 三個類別是: %s。 總共耗時: %s 秒</p></body></html>" % (customerText, datetime.datetime.now(), top_three_ensemble, tEnd - tStart)
    # return HttpResponse(html)

    
    ans_text = "翻譯後字串為: %s " % (customerText,)
    ans_text2 = "It is now %s. 三個類別是: %s。 總共耗時: %s 秒" % (datetime.datetime.now(), top_three_ensemble, tEnd - tStart)
    
    context = {'ans_text': ans_text,'ans_text2': ans_text2, 'top_three_ensemble': top_three_ensemble}
    return render(request, 'main/demo4.html', context)
    # return JsonResponse({'recommendCategories':top_three_ensemble})
    
def nn_predict(customerText):

    ## jieba settings
    # jieba.set_dictionary('dict.txt.big')
    # jieba.load_userdict("userdict0714.txt")

    #padding settings
    max_length = 20
    trunc_type='post'
    padding_type='post' # 0 加在尾端

    #tokenizer settings
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    
    # transfer labels to num
    label_index_dict = {
        '數位金融 - 數位存款帳戶': 0,
        '數位金融 - 網路銀行': 1,
        '數位金融 - 行動銀行': 2,
        '數位金融 - LINE個人化服務': 3,
        '數位金融 - 網路ATM': 4,
        '行動支付 - Fitbit Pay': 5,
        '行動支付 - Hami Pay': 6,
        '基金投資': 7,
        '貸款': 8,
        '信託': 9,
        'ATM相關服務': 10,
        '信用卡': 11,
        '綜合對帳單': 12,
        'MyBill 輕鬆繳': 13,
        '存款帳戶': 14,
        0: '數位金融 - 數位存款帳戶',
        1: '數位金融 - 網路銀行',
        2: '數位金融 - 行動銀行',
        3: '數位金融 - LINE個人化服務',
        4: '數位金融 - 網路ATM',
        5: '行動支付 - Fitbit Pay',
        6: '行動支付 - Hami Pay',
        7: '基金投資',
        8: '貸款',
        9: '信託',
        10: 'ATM相關服務',
        11: '信用卡',
        12: '綜合對帳單',
        13: 'MyBill 輕鬆繳', 
        14: '存款帳戶',
    }  
    

    ######需要分類的問題######
    # user_sentences = '學生是否可以調高信用卡額度'
    user_sentences = customerText
    # print(user_sentences)
    
    # 資料前處理 -- jieba 斷詞、去除標點符號、英文轉小寫
    
    #去除標點符號、全部轉為小寫
    reg = "[^0-9A-Za-z\u4e00-\u9fa5]"
    user_sentences_without_punctuation = re.sub(reg,'', user_sentences)
    user_sentences_without_punctuation = user_sentences_without_punctuation.lower()

    # jieba
    words = jieba.cut(user_sentences_without_punctuation, cut_all=False)
    sentence_split = ''
    for word in words:
        sentence_split += ' ' + word
    user_sentences_split = sentence_split
    
    # tokenlize
    user_sequences = tokenizer.texts_to_sequences([user_sentences_split,])
    user_padded = pad_sequences(user_sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)
    print(user_sequences)
    print(user_padded)
    
    # NN、LSTM、CNN
    
    # NN
    model = tf.keras.models.load_model('./models/nn_model.h5')
    # #https://github.com/tensorflow/tensorflow/issues/38561
    
    @tf.function(experimental_relax_shapes=True)
    def predictNN(t):
        return model(t)
    # sentences_probabilities = model.predict(user_padded)
    sentences_probabilities = predictNN(user_padded)
    sentences_top_three = heapq.nlargest(3, zip(sentences_probabilities[0], list(range(len(sentences_probabilities[0])))))
    top_three_nn = []
    for i in sentences_top_three:
        top_three_nn.append(label_index_dict[i[1]])
 
    # LSTM
    modelLSTM = tf.keras.models.load_model('./models/lstm_model.h5')
    # #https://github.com/tensorflow/tensorflow/issues/38561
    
    @tf.function(experimental_relax_shapes=True)
    def predictLSTM(t):
        return modelLSTM(t)
    # sentences_probabilities = modelLSTM.predict(user_padded)
    sentences_probabilities = predictLSTM(user_padded)
    sentences_top_three = heapq.nlargest(3, zip(sentences_probabilities[0], list(range(len(sentences_probabilities[0])))))
    top_three_lstm = []
    for i in sentences_top_three:
        top_three_lstm.append(label_index_dict[i[1]])


        
    # CNN
    modelCNN = tf.keras.models.load_model('./models/cnn_model.h5')
    # #https://github.com/tensorflow/tensorflow/issues/38561
    
    @tf.function(experimental_relax_shapes=True)
    def predictCNN(t):
        return modelCNN(t)
    # sentences_probabilities = modelCNN.predict(user_padded)
    sentences_probabilities = predictCNN(user_padded)
    sentences_top_three = heapq.nlargest(3, zip(sentences_probabilities[0], list(range(len(sentences_probabilities[0])))))
    top_three_cnn = []
    for i in sentences_top_three:
        top_three_cnn.append(label_index_dict[i[1]])

        
    # 集成式學習(取nn、LSTM、CNN)三個神經網路共同決策出三個最可能的結果 
    temp = []
    for index in range(3):
        temp.extend([top_three_lstm[index], top_three_cnn[index], top_three_nn[index]])
    uniq = []
    [uniq.append(x) for x in temp if x not in uniq]
    top_three_ensemble = uniq[:3]
    
    
    return top_three_ensemble