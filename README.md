# ytt2ass
Youtube timedtext (YTT) to ASS subtitle format conversion

---
這個工具用於產生 ASS 字幕重現 Youtube 影片中 YTT 字幕風格。

## 使用說明
(TODO)

## 由來
一般在 Youtube 上建立 CC 字幕，只能編輯文字，而無法編輯風格，如顏色，大小，位置等，不過現在有了 [YTSubConverter](https://github.com/arcusmaximus/YTSubConverter) ，這個工具可以將 ASS 字幕轉換為 YTT 字幕，上傳到 Youtube 後可呈現特別的字幕風格:

[HIMEHINA『ヒトガタ』『人型』MV](https://www.youtube.com/watch?v=J8PUUv4LFkQ)
![](https://github.com/nitsaick/ytt2ass/raw/master/img/1.gif)

[Kizuna AI - AIAIAI (feat. 中田ヤスタカ)【Official Music Video】](https://www.youtube.com/watch?v=S8dmq5YIUoc)
![](https://github.com/nitsaick/ytt2ass/raw/master/img/2.gif)

上面兩個影片中的歌詞顯示皆為 Youtube 的 CC 字幕，可以看到比起一般的 CC 字幕，這兩個影片的字幕有特別的位置，顏色，可以做到卡拉OK的滾動風格，這些都是套用了 YTT 格式後可以達到的效果

YTT (YouTube Timed Text) 是 Youtube 獨有的字幕格式:
```
<?xml version="1.0" encoding="utf-8" ?><timedtext format="3">
<head>
<pen id="1" b="1" fc="#FEFEFE" bo="0" ec="#000000" et="3" fs="2"/>
...
<ws id="0"/>
...
<wp id="13" ap="3" ah="0" av="3"/>
</head>
<body>
<p t="1841" d="1234" wp="1" ws="1" p="1">Hey,Mr&amp;MrsVirtual,</p>
...
```

大多數 Youtube 下載工具都能下載 CC 字幕，通常會將字幕轉換為 SRT 字幕格式，這在一般的 CC 字幕是可行的，但如果是有套用 YTT 格式的 CC 字幕，下載下來的 SRT 播放出來會出現以下情況:

![](https://github.com/nitsaick/ytt2ass/raw/master/img/3.gif)

這是因為 YTT 裡面有大量不同風格但重複文字的字幕， 再加上 SRT 不能設定位置，大小，所以下載下來的 SRT 沒辦法達到相同的字幕風格。

而本工具的目的就是將 YTT 字幕轉換為具有相同風格 ASS 字幕格式。

## TODO
* 寫使用說明
* 轉換後的效果比較
* Add english README
* Add more optional
* Remove style which have not been used 
* Support vertical subtitle
* ...

## Reference
* [YTSubConverter](https://github.com/arcusmaximus/YTSubConverter)
* [【字幕進階】使用.ytt格式製作Youtube炫炮字幕](https://forum.gamer.com.tw/C.php?bsn=60608&snA=310)