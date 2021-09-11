# -*- coding: utf-8 -*-



from io import BytesIO
import glob, urllib,re,os,sys,json
import numpy as np
import pandas as pd
import MeCab as mc
from flask import Flask, session,render_template,url_for, redirect,request,flash, jsonify
from collections import Counter
slothlib_path = 'http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt'
slothlib_file = urllib.request.urlopen(slothlib_path)
slothlib_stopwords = [line.decode("utf-8").strip() for line in slothlib_file]
default_stop_words = [ u'てる', u'いる', u'なる', u'れる', u'する', u'ある', u'こと', u'これ', u'さん', u'して', \
             u'くれる', u'やる', u'くださる', u'そう', u'せる', u'した',  u'思う',  \
             u'それ', u'ここ', u'ちゃん', u'くん', u'', u'て',u'に',u'を',u'は',u'の', u'が', u'と', u'た', u'し', u'で', \
             u'ない', u'も', u'な', u'い', u'か', u'ので', u'よう', u'',u'なっ',u'やっ']
stop_words = [ss for ss in slothlib_stopwords if not ss==u'']
#stop_words += newstitles
#stop_words += addstopwords
#stop_words += default_stop_words
tagger = mc.Tagger('-Ochasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
tagger.parseToNode("")
env = os.getenv("RECOMMENDER_ENV","development")
app = Flask(__name__)
app.secret_key = 'hogeshu'
app.config['SESSION_TYPE'] = 'filesystem'
@app.route('/')
def index():
    text = "SPICE・11/26(月)オススメの音楽記事 ↓記事はこちらをチェック↓ ▼ペット・ショップ・ボーイズ、19年ぶりの単独来日公演が決定 http://spice.eplus.jp/articles/218523 ▼野田洋次郎（RADWIMPS）＆桐谷美玲 ニュージーランドで撮影した淡麗グリーンラベルの新CMのメイキング映像公開 http://spice.eplus.jp/articles/218459 ▼AAA、2年連続4大ドームツアー完遂 ツアーファイナル・福岡ヤフオク！ドーム公演をレポート http://spice.eplus.jp/articles/218489 ▼DIR EN GREYの薫(Gt)、初の個展『ノウテイカラノ』『krim&zon展』を2019年開催 http://spice.eplus.jp/articles/218527 ▼この子 来年1月に初の全国流通盤となる1stアルバムをリリース決定 海ワンマンライブの開催も発表に http://spice.eplus.jp/articles/218530 ▼Eve アクションRPG『ドラガリアロスト』に書き下ろし曲「楓」を楽曲提供 http://spice.eplus.jp/articles/218493   ▽そのほかの記事はこちらから▽ https://spice.eplus.jp/articles/music"
    tagger = mc.Tagger('-Ochasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    tagger.parseToNode("")
    node = tagger.parseToNode(text)


    #print([node.surface for node in nodes if node.feature.split(",")[0] in ("名詞", "動詞", "形容詞") and node.surface not in stop_words + more_stop_words])
    word_list = []
    while node:
        if node.feature.split(",")[0] in ("名詞", "動詞", "形容詞") and node.surface not in stop_words:
            word_list.append(node.surface)
        node = node.next
    word_count= Counter(word_list)
    print(word_count)
    words = [key for key, value in word_count.most_common()[:10]]
    jsonify(words)
    return render_template('index.html',text=words)
    #return


@app.route('/img_recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'GET':
        res = request.args.get('get_value')
        return res
    elif request.method == 'POST':
        #print(request.form["article_content"])
        #return "ast"
        p = re.compile(r"<[^>]*?>")
        text = p.sub("",request.form["article_content"]).replace(" ","").replace("nbsp","")
        node = tagger.parseToNode(text)
        word_list = []
        while node:
            if node.feature.split(",")[0] in ("名詞", "動詞", "形容詞") and node.surface not in stop_words and len(node.surface)>2:
                word_list.append(node.surface)
            node = node.next
        word_count= Counter(word_list)
        words=[key for key, value in word_count.most_common()[:3]]
        img_urls =[]
        img_tens = []
        print(words)
        for word in words:
            print(word)
            result = urllib.request.urlopen("https://pixabay.com/api/?key=10840772-2f1d92e3e5d5163e1066d95db&q="+urllib.parse.quote_plus(word, encoding='utf-8')+"&image_type=photo&pretty=true&per_page=20&lang=ja")
            content = json.loads(result.read().decode('utf8'))
            if len(content["hits"]) > 1:
                df = pd.DataFrame(content["hits"])
                img_tens.extend(df[:int(12/len(words))]["webformatURL"].values)
                img_urls.extend(df[df["tags"].str.contains(word)]["webformatURL"].values)
        if len(img_urls) > 9:
            return jsonify(img_urls)
        else:
            return jsonify(img_tens)



if __name__ == '__main__':
    if env != "production":
      #app.run(debug=True,host='192.168.11.2',port=5000)
      app.run(debug=True,host='192.168.1.238',port=5000)

    else:
      app.run(debug=False,host='0.0.0.0',port=5000)
