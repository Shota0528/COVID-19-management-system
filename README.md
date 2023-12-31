# データベース論及び演習 18班 Covid-19管理システム
## 概要
ある大学ではCOVID-19感染対策として、教職員及び学生(以降、関係者)の体調管理記録と行動記録を収集し、2次感染を最小限にしたい。
このため、体調管理と行動記録をWebベースで収集し、状況を把握・管理するシステムを構築することとなった。

## 機能要件
- 関係者は，午前または午後どちらか1回は体調を記録する。体調記録のテンプレートは，COVID体調観察表.pdf
- 関係者は，最低限，一日に1回は行動記録を入力する。行動記録は，自宅以外の飲食店など不特定多数の人と接触する場所に出入りしたときは必ず記録する。従って，一日に複数の場所に行った場合は，行った場所の数だけ記録する。一日中，自宅にいた場合は，一日中自宅にいたことを記録する。行動記録のテンプレートは，COVID行動記録.pdf
- Covid-19に感染した場合，または濃厚接触者と指定された場合は，感染または濃厚接触者として，感染または濃厚接触者と指定された日付を入力する。
- Covid-19に感染または濃厚接触者となった場合は，発生した日から1週間，出校停止とする。出校停止期間中も，体調と行動記録は入力する。
- 管理者は，COVIDに感染している関係者の数を把握できる。
- その他，管理するのに有効な機能があれば追加する。以下はその事例である。
    - 管理者は，体調記録または行動記録を3日連続して入力していない関係者をピックアップし，入力するように連絡する。
    - 管理者は，熱が37.5度以上，関節痛・だるさなどの症状が5個以上チェックされている関係者をピックアップし，連絡する。
など

## 開発スケジュール
- 6月29日　
    
    - 機能要件の確認(追加機能は必要か、データはどのように入力するか、など)	
    - テーブル設計  
    - テーブル定義のためのSQL作成
    - テストデータの作成
    - テストデータをテーブルに入力するためのPythonプログラム作成
<br>
<br>

- 7月6日
	
    - テーブル定義
	- テストデータ作成
	- 機能要件の確定(画面イメージ、ルーティング情報、テンプレートファイル名)
        - メインメニューの決定
        - サブメニューの決定(ルーティング情報，テンプレートファイル名，画面遷移)
	    - コーディング
<br>
<br>

- 7月13日
    - モジュールの結合
    - デバッグ
	- 並列して発表用資料PPT作成
<br>
<br>

- 7月20日
	- 発表用資料PPT作成
    - 15:00~作品発表会および相互評価

## ファイル共有について
ファイル共有については以下のように行う。

- main
    
    本番用のファイルを置く。

- share
    
    共有用のファイルを置く。デフォルトファイルなどもここに置く。個人でデフォルトファイルを更新したものを置く場合には`学籍番号_元のファイル名`とする。

- 個人名
    
    個人のバックアップなどに使用する。基本的に他人のリポジトリは更新しないこととする。

## コミットの書き方について
コミットの書き方については原則以下のように行う。

- 最初のコミットの時
    - First Commit

- ファイルを追加したとき
    - add:hogehogeを追加

- 修正したとき
    - fix:hogehogeのhugahugaを修正

- ファイルを上書きしたとき
    - update:hogehogeを追加

- ファイルを消した時
    - del:hogehogeを削除