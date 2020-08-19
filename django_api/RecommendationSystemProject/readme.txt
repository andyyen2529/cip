1.先裝anaconda(python3.6) 

2.安裝requirements.txt裡面所要裝的東西

3..這個步驟是為了要放入離線訓練好的中文模型
  到Anaconda3資料夾 在 C:\users\Anaconda3 或是 D:\Users\nt094400 
  之後anaconda3\envs\自己的虛擬環境\Lib\site-packages\speech-recognition\pocketsphinx-data 把zh-cn資料夾放進去

4..看看跑步跑的起來
  cmd啟動虛擬環境 activate 虛擬環境的名稱
  切換路徑到  django-api\RecommendationSystemProject (有manage.py的地方) 執行 python manage.py runserver
  跑得起來的話就可以到browser 127.0.0.1://demo1 開始測試