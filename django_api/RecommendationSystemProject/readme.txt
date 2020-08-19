1.先裝anaconda(python3.6) 

2.安裝相關套件， 安裝方法到將虛擬環境啟動(cmd 打activate)之後，cd到env_setup，輸入 setupenv.bat即可

3..這個步驟是為了要放入離線訓練好的中文模型
  到Anaconda3資料夾 在 C:\users\Anaconda3 或是 D:\Users\nt094400 
  之後anaconda3\Lib\site-packages\speech-recognition\pocketsphinx-data 把zh-cn資料夾放進去
  (參考資料 https://www.cnblogs.com/lishangzhi/p/12089981.html)

4.到django_api/RecommendationSystemProject/main/views中
  註解掉第73、80、109、116行
  取消註解第74、81、110、117行  (為了是要轉成使用離線模型作語音轉文字而不是使用google的api)

5.看看跑不跑的起來
  cmd啟動虛擬環境(cmd 打activate)
  切換路徑到  django-api\RecommendationSystemProject (有manage.py的地方) 執行 python manage.py runserver
  跑得起來的話就可以到browser http://127.0.0.1:8000/main/demo4 開始測試

6.修改django_api/RecommendationSystemProject/main/views中的程式碼，
  把第 134註解掉 # return render(request, 'main/demo4.html', context)
  加上一行  return JsonResponse({'recommendCategories':top_three_ensemble}) 這步驟是為了改成回傳json而不是整個template，
  就可以透過 http://127.0.0.1:8000/main/recommend_categories/audio/ajax_calls/ 得到回傳的類別
  ex.{"recommendCategories": ["\u5b58\u6b3e\u5e33\u6236", "\u4fe1\u8a17", "\u8cb8\u6b3e"]}