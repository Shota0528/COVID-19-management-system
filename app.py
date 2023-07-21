from MyDatabase import my_open , my_query , my_close
import pandas as pd
from flask import Flask, redirect, url_for, render_template, request, session
import datetime
import smtplib
from email.mime.text import MIMEText

dsn = {
    'host' : '',  #ホスト名(IPアドレス)
    'port' : '',        #mysqlの接続ポート番号
    'user' : 'root',      #dbアクセスするためのユーザid
    'password' : '',    #ユーザidに対応するパスワード
    'database' : 'covid19' #オープンするデータベース名
}

app = Flask(__name__ ,static_folder="static")

app.secret_key = 'user'
app.permanent_session_lifetime = datetime.timedelta(minutes=60)

#ルーティング定義
@app.route("/")
def top():
    return render_template("top.html",
        title = "COVID-19管理システムトップ"
    )

@app.route("/register")
def register():
    return render_template("register.html",
        title = "アカウント登録"
    )

@app.route("/register2", methods=["POST"])
def register2():
    username = request.form["username"]
    userpassword = request.form["userpassword"]
    usercode = request.form["usercode"]
    facultyoffice = request.form["facultyoffice"]
    kind = request.form["kind"]
    phone = request.form["phone"]
    email = request.form["email"]

    dbcon,cur = my_open(**dsn) 
    
    dt_now = datetime.datetime.now()
    sqlstring = f"""
        INSERT INTO user
        (usercode,userpassword,facultyoffice,namae,kind,phone,email,adminflag,lastupdate)
        values
        ('{usercode}','{userpassword}','{facultyoffice}','{username}','{kind}','{phone}','{email}',0,'{dt_now}')
        ;
    """
    
    my_query(sqlstring,cur) 
    
    dbcon.commit()
    my_close(dbcon, cur)
    
    return render_template("msg.html",
        title = "アカウント登録完了", 
        msg = f"ようこそ{username}さん", 
        linkname = "ログイン", 
        link = "/login"
    )

@app.route("/login")
def login():
    if "usercode" in session:
        return render_template("msg.html",
            title = "ログイン確認", 
            msg = "ログインしています", 
            linkname = "ログアウト", 
            link = "/logout"
        )
    else:
        return render_template("login.html",
        title = "ログイン"
    )

@app.route("/login2", methods=["POST"])
def login2():
    usercode = request.form["usercode"]
    userpassword = request.form["userpassword"]

    dbcon,cur = my_open(**dsn) 
    
    sqlstring = f"""
        SELECT * FROM user WHERE usercode='{usercode}' AND userpassword='{userpassword}';
    """
    
    my_query(sqlstring,cur)

    recset = pd.DataFrame(cur.fetchall())
    
    if recset.empty:
        return render_template("msg.html",
            title = "ログインエラー", 
            msg = "名前またはパスワードが違います", 
            linkname = "ログイン", 
            link = "/login"
        )
        
    adminflag = recset["adminflag"][0]
    if adminflag == 1:
        session["admin"] = 1

    userID = int(recset.userID[0])
    usercode = recset.usercode[0]
    username = recset.namae[0]
    
    # adminflagを1にするためにuserIDをログイン時に確認
    print(userID)
    
    my_close(dbcon, cur)
    
    session["usercode"] = usercode
    session["userID"] = userID
    return render_template("msg.html",
        title = "ログイン完了",
        msg = f"ようこそ{username}さん", 
        linkname = "ログアウト", 
        link = "/logout"
    )

@app.route("/logout")
def logout():
    if "usercode" in session:
        session.pop("usercode", None)
        session.pop("admin", None)
        return render_template("msg.html",
            title = "ログアウト完了", 
            msg = "ログアウトしました", 
            linkname = "ログイン", 
            link = "/login"
        )
    else:  
        return render_template("msg.html",
            title = "ログアウトエラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/mypage")
def mypage():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn) 
        
        sqlstring = f"""
            SELECT * FROM infected WHERE userID='{session["userID"]}';
        """
        
        my_query(sqlstring,cur)

        recset = pd.DataFrame(cur.fetchall())

        if recset.empty:
            return render_template("mypage.html", 
            title = "マイページ", 
            infectflag = 0, 
            attendancestop = ""
        )
        infect = recset["infect"][0]
        closecontact = recset["closecontact"][0]
        
        infectflag = 0
        if infect == 1 or closecontact == 1:
            infectflag = 1
        
        attendancestop = recset["attendancestop"][0]
        
        my_close(dbcon, cur)
        return render_template("mypage.html", 
            title = "マイページ", 
            infectflag = infectflag, 
            attendancestop = attendancestop
        )
    else:
        return render_template("msg.html",
            title = "体調観察記録エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/health")
def health():
    if "usercode" in session:
        dt_now = datetime.datetime.now()
        return render_template("health.html",
            title = "体調観察記録", 
            dt_now = dt_now
        )
    else:  
        return render_template("msg.html",
            title = "体調観察記録エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/health2", methods=["POST"])
def health2():
    recorddate = request.form["recorddate"]
    timezone = int(request.form["timezone"])
    temperature = float(request.form["temperature"])
    jointpain = 1 if request.form.get("jointpain")=="1" else 0
    washedoutfeeling = 1 if request.form.get("washedoutfeeling")=="1" else 0
    headache = 1 if request.form.get("headache")=="1" else 0
    sorethroat = 1 if request.form.get("sorethroat")=="1" else 0
    breathless = 1 if request.form.get("breathless")=="1" else 0
    coughsneezing = 1 if request.form.get("coughsneezing")=="1" else 0
    nausea = 1 if request.form.get("nausea")=="1" else 0
    abdominalpain = 1 if request.form.get("abdominalpain")=="1" else 0
    tastedisorder = 1 if request.form.get("tastedisorder")=="1" else 0
    olfactorydisorder = 1 if request.form.get("olfactorydisorder")=="1" else 0
    
    dbcon,cur = my_open(**dsn) 
    dt_now = datetime.datetime.now()
    
    sqlstring = f"""
        INSERT INTO symptoms
        (temperature,jointpain,washedoutfeeling,headache,sorethroat,breathless,coughsneezing,nausea,abdominalpain,tastedisorder,olfactorydisorder,lastupdate)
        values
        ({temperature},{jointpain},{washedoutfeeling},{headache},{sorethroat},{breathless},{coughsneezing},{nausea},{abdominalpain},{tastedisorder},{olfactorydisorder},'{dt_now}')
        ;
    """
    
    my_query(sqlstring, cur)
    
    sqlstring = f"""
        SELECT * FROM symptoms ORDER BY symptomsID DESC;
    """
    
    my_query(sqlstring, cur)
    
    recset = pd.DataFrame(cur.fetchall())
    symptomsID = recset.symptomsID[0]
    
    sqlstring = f"""
        INSERT INTO healthmanagement
        (symptomsID,userID,recorddate,timezone,lastupdate)
        values
        ({symptomsID},{session["userID"]},'{recorddate}',{timezone},'{dt_now}')
        ;
    """
    
    my_query(sqlstring, cur)
    
    dbcon.commit()
    my_close(dbcon,cur)

    return render_template("msg.html",
        title = "体調観察記録", 
        msg = "体調管理記録を登録しました", 
        linkname = "体調観察確認", 
        link = "/checkhealth"
    )

@app.route("/checkhealth")
def checkhealth():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn)
        sqlstring = f"""
            SELECT * FROM health_symptoms WHERE timezone=0 AND userID='{session["userID"]}' ORDER BY recorddate ASC;
        """
        my_query(sqlstring, cur)
        df_AM = pd.DataFrame(cur.fetchall())
        
        sqlstring = f"""
            SELECT * FROM health_symptoms WHERE timezone=1 AND userID='{session["userID"]}' ORDER BY recorddate ASC;
        """
        my_query(sqlstring, cur)
        df_PM = pd.DataFrame(cur.fetchall())
        
        # HTMLで表記する際のindexを作成
        df_index = ["体温", " 関節・筋肉痛", "だるさ", "頭痛", "咽頭痛", "息苦しさ", "咳・くしゃみ", "吐気・嘔吐", "腹痛・下痢", "味覚障害", "嗅覚障害"]

        # AM, PMにデータがないときにmsg.htmlでreturn
        if df_AM.empty:
            if df_PM.empty: 
                my_close(dbcon, cur)
                return render_template("msg.html", 
                    title = "体調観察確認エラー", 
                    msg = "記録が1件もありません", 
                    linkname = "体調観察登録", 
                    link = "/health"
                )
            else:
                df_PM = df_PM.drop(columns=["symptomsID", "userID", "timezone"])
                date_list_PM = df_PM["recorddate"].to_list()
                date_list = sorted(list(set(date_list_PM)))
                for column in df_PM.columns:
                    df_PM.loc[df_PM[column]==0, [column]]=""
                    df_PM.loc[df_PM[column]==1, [column]]="有り"
                df_PM["temperature"] = df_PM["temperature"].astype(str) + "℃"
                df_PM["recorddate"] = pd.to_datetime(df_PM["recorddate"])
                df_PM = df_PM.sort_values("recorddate").drop(columns="recorddate").T
                my_close(dbcon, cur)
                return render_template("checkhealth.html",
                    title = "体調観察確認", 
                    date_list = date_list, 
                    table_index = df_index, 
                    table_data_AM = df_AM, 
                    table_data_PM = df_PM
                )
        else:
            if df_PM.empty:
                df_AM = df_AM.drop(columns=["symptomsID", "userID", "timezone"])
                date_list_AM = df_AM["recorddate"].to_list()
                date_list = sorted(list(set(date_list_AM)))
                for column in df_AM.columns:
                    df_AM.loc[df_AM[column]==0, [column]]=""
                    df_AM.loc[df_AM[column]==1, [column]]="有り"
                df_AM["temperature"] = df_AM["temperature"].astype(str) + "℃"
                df_AM["recorddate"] = pd.to_datetime(df_AM["recorddate"])
                df_AM = df_AM.sort_values("recorddate").drop(columns="recorddate").T
                my_close(dbcon, cur)
                return render_template("checkhealth.html",
                    title = "体調観察確認", 
                    date_list = date_list, 
                    table_index = df_index, 
                    table_data_AM = df_AM, 
                    table_data_PM = df_PM
                )
            else:
                df_AM = df_AM.drop(columns=["symptomsID", "userID", "timezone"])
                df_PM = df_PM.drop(columns=["symptomsID", "userID", "timezone"])
                
                # AMとPMでどちらかしか登録がないかどうかを確認するためのdate_listを作成するためにAM, PMのrecorddateをリストにする
                date_list_AM = df_AM["recorddate"].to_list()
                date_list_PM = df_PM["recorddate"].to_list()
                
                # AMとPMでどちらかしか登録がないかどうかを確認するためのdate_listを作成
                # 重複を削除し, listにした後ソートする.
                date_list = sorted(list(set(date_list_AM + date_list_PM)))
                
                # AMとPMでどちらかしか登録がない場合に, recorddateをその日付に, その他は空にしたものをDFに追加
                for i in date_list:
                    if not (i in date_list_AM):
                        df_AM.loc[i] = [i, "", "", "", "", "", "", "", "", "", "", ""]
                    
                    if not (i in date_list_PM):
                        df_PM.loc[i] = [i, "", "", "", "", "", "", "", "", "", "", ""]
                
                # HTML表示を見据えて, データが0なら空白, 1なら有りに変換
                for column in df_AM.columns:
                    df_AM.loc[df_AM[column]==0, [column]]=""
                    df_AM.loc[df_AM[column]==1, [column]]="有り"
                
                for column in df_PM.columns:
                    df_PM.loc[df_PM[column]==0, [column]]=""
                    df_PM.loc[df_PM[column]==1, [column]]="有り"
                
                # 体温に単位を付ける
                df_AM["temperature"] = df_AM["temperature"].astype(str) + "℃"
                df_PM["temperature"] = df_PM["temperature"].astype(str) + "℃"

                # 日付でソートするためにrecorddateの型をstrからdatetimeに変換
                df_AM["recorddate"] = pd.to_datetime(df_AM["recorddate"])
                df_PM["recorddate"] = pd.to_datetime(df_PM["recorddate"])
                
                # HTMLで表示する際にはrecorddateは要らないので削除
                df_AM = df_AM.sort_values("recorddate").drop(columns="recorddate").T
                df_PM = df_PM.sort_values("recorddate").drop(columns="recorddate").T
                    
                my_close(dbcon, cur)
                return render_template("checkhealth.html",
                    title = "体調観察確認", 
                    date_list = date_list, 
                    table_index = df_index, 
                    table_data_AM = df_AM, 
                    table_data_PM = df_PM
                )
    else:  
        return render_template("msg.html",
            title = "体調観察確認エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/changehealth")
def changehealth():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn)
        sqlstring = f"""
            SELECT * FROM health_symptoms WHERE timezone=0 AND userID='{session["userID"]}' ORDER BY recorddate ASC;
        """
        my_query(sqlstring, cur)
        df_AM = pd.DataFrame(cur.fetchall())
        
        sqlstring = f"""
            SELECT * FROM health_symptoms WHERE timezone=1 AND userID='{session["userID"]}' ORDER BY recorddate ASC;
        """
        my_query(sqlstring, cur)
        df_PM = pd.DataFrame(cur.fetchall())
        
        # HTMLで表記する際のindexを作成
        df_index = ["体温", " 関節・筋肉痛", "だるさ", "頭痛", "咽頭痛", "息苦しさ", "咳・くしゃみ", "吐気・嘔吐", "腹痛・下痢", "味覚障害", "嗅覚障害"]

        # AM, PMにデータがないときにmsg.htmlでreturn
        if df_AM.empty:
            if df_PM.empty:
                my_close(dbcon, cur)
                return render_template("msg.html", 
                    title = "体調観察修正エラー", 
                    msg = "記録が1件もありません", 
                    linkname = "体調観察登録", 
                    link = "/health"
                )
            else:
                df_PM = df_PM.drop(columns=["userID", "timezone"])
                date_list_PM = df_PM["recorddate"].to_list()
                date_list = sorted(list(set(date_list_PM)))
                for column in df_PM.columns:
                    if column == "symptomsID":
                        continue
                    else:                    
                        df_PM.loc[df_PM[column]==0, [column]]=""
                        df_PM.loc[df_PM[column]==1, [column]]="有り"
                df_PM["temperature"] = df_PM["temperature"].astype(str) + "℃"
                df_PM["recorddate"] = pd.to_datetime(df_PM["recorddate"])
                df_PM = df_PM.sort_values("recorddate")
                symptomsID_list_PM = df_PM["symptomsID"].to_list()
                df_PM = df_PM.drop(columns=["symptomsID", "recorddate"]).T
                my_close(dbcon, cur)
                return render_template("changehealth.html",
                    title = "体調観察修正データ選択", 
                    date_list = date_list, 
                    table_index = df_index, 
                    table_data_AM = df_AM, 
                    table_data_PM = df_PM,  
                    symptomsID_list_PM = symptomsID_list_PM
                )
        else:
            if df_PM.empty:
                df_AM = df_AM.drop(columns=["userID", "timezone"])
                date_list_AM = df_AM["recorddate"].to_list()
                date_list = sorted(list(set(date_list_AM)))
                for column in df_AM.columns:
                    if column == "symptomsID":
                        continue
                    else:                    
                        df_AM.loc[df_AM[column]==0, [column]]=""
                        df_AM.loc[df_AM[column]==1, [column]]="有り"
                df_AM["temperature"] = df_AM["temperature"].astype(str) + "℃"
                df_AM["recorddate"] = pd.to_datetime(df_AM["recorddate"])
                df_AM = df_AM.sort_values("recorddate")
                symptomsID_list_AM = df_AM["symptomsID"].to_list()
                df_AM = df_AM.drop(columns=["symptomsID", "recorddate"]).T
                my_close(dbcon, cur)
                return render_template("changehealth.html",
                    title = "体調観察修正データ選択", 
                    date_list = date_list, 
                    table_index = df_index, 
                    table_data_AM = df_AM, 
                    table_data_PM = df_PM, 
                    symptomsID_list_AM = symptomsID_list_AM
                )
            else:   
                df_AM = df_AM.drop(columns=["userID", "timezone"])
                df_PM = df_PM.drop(columns=["userID", "timezone"])
                
                # AMとPMでどちらかしか登録がないかどうかを確認するためのdate_listを作成するためにAM, PMのrecorddateをリストにする
                date_list_AM = df_AM["recorddate"].to_list()
                date_list_PM = df_PM["recorddate"].to_list()
                
                # AMとPMでどちらかしか登録がないかどうかを確認するためのdate_listを作成
                # 重複を削除し, listにした後ソートする.
                date_list = sorted(list(set(date_list_AM + date_list_PM)))
                
                # AMとPMでどちらかしか登録がない場合に, recorddateをその日付に, その他は空にしたものをDFに追加
                for i in date_list:
                    if not (i in date_list_AM):
                        df_AM.loc[i] = ["", i, "", "", "", "", "", "", "", "", "", "", ""]
                    
                    if not (i in date_list_PM):
                        df_PM.loc[i] = ["", i, "", "", "", "", "", "", "", "", "", "", ""]
                
                # HTML表示を見据えて, データが0なら空白, 1なら有りに変換
                for column in df_AM.columns:
                    if column == "symptomsID":
                        continue
                    else:
                        df_AM.loc[df_AM[column]==0, [column]]=""
                        df_AM.loc[df_AM[column]==1, [column]]="有り"
                
                for column in df_PM.columns:
                    if column == "symptomsID":
                        continue
                    else:                    
                        df_PM.loc[df_PM[column]==0, [column]]=""
                        df_PM.loc[df_PM[column]==1, [column]]="有り"
                
                # 体温に単位を付ける
                df_AM["temperature"] = df_AM["temperature"].astype(str) + "℃"
                df_PM["temperature"] = df_PM["temperature"].astype(str) + "℃"

                # 日付でソートするためにrecorddateの型をstrからdatetimeに変換
                df_AM["recorddate"] = pd.to_datetime(df_AM["recorddate"])
                df_PM["recorddate"] = pd.to_datetime(df_PM["recorddate"])
                
                # 日付でソート
                df_AM = df_AM.sort_values("recorddate")
                df_PM = df_PM.sort_values("recorddate")
                
                # symptomsIDのリストを作成
                symptomsID_list_AM = df_AM["symptomsID"].to_list()
                symptomsID_list_PM = df_PM["symptomsID"].to_list()
                
                # HTMLで表示する際にはsymptomsIDとrecorddateは要らないので削除
                df_AM = df_AM.drop(columns=["symptomsID", "recorddate"]).T
                df_PM = df_PM.drop(columns=["symptomsID", "recorddate"]).T
                
                my_close(dbcon, cur)
                return render_template("changehealth.html",
                    title = "体調観察修正データ選択", 
                    date_list = date_list, 
                    table_index = df_index, 
                    table_data_AM = df_AM, 
                    table_data_PM = df_PM, 
                    symptomsID_list_AM = symptomsID_list_AM, 
                    symptomsID_list_PM = symptomsID_list_PM
                )
    else:
        return render_template("msg.html", 
            title = "体調観察修正エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/changehealth2", methods=["POST"])
def changehealth2():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn)
        symptomsID = request.form["symptomsID"]

        sqlstring = f"""
            SELECT * FROM health_symptoms WHERE symptomsID = {symptomsID};
        """
        my_query(sqlstring,cur)
        recset = pd.DataFrame(cur.fetchall())
        rowdata = pd.Series(recset.iloc[0])
        
        symptoms_list_eng = ["jointpain", "washedoutfeeling", "headache", "sorethroat", "breathless", "coughsneezing", "nausea", "abdominalpain", "tastedisorder", "olfactorydisorder"]
        symptoms_list_jp = ["関節・筋肉痛", "だるさ", "頭痛", "咽頭痛", "息苦しさ", "咳・くしゃみ", "吐き気・嘔吐", "腹痛・下痢", "味覚障害", "嗅覚障害"]
        
        my_close(dbcon,cur)
        return render_template("changehealth2.html", 
            title = "体調観察修正", 
            table_data = rowdata, 
            symptoms_list_eng = symptoms_list_eng, 
            symptoms_list_jp = symptoms_list_jp, 
            symptomsID = symptomsID
        )
    else:
        return render_template("msg.html", 
            title = "体調観察修正エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )
@app.route("/changehealth3", methods=["GET", "POST"])
def changehealth3():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn)
        symptomsID = request.args.get('symptomsID', '')
        recorddate = request.form["recorddate"]
        timezone = int(request.form["timezone"])
        temperature = float(request.form["temperature"])
        jointpain = 1 if request.form.get("jointpain")=="1" else 0
        washedoutfeeling = 1 if request.form.get("washedoutfeeling")=="1" else 0
        headache = 1 if request.form.get("headache")=="1" else 0
        sorethroat = 1 if request.form.get("sorethroat")=="1" else 0
        breathless = 1 if request.form.get("breathless")=="1" else 0
        coughsneezing = 1 if request.form.get("coughsneezing")=="1" else 0
        nausea = 1 if request.form.get("nausea")=="1" else 0
        abdominalpain = 1 if request.form.get("abdominalpain")=="1" else 0
        tastedisorder = 1 if request.form.get("tastedisorder")=="1" else 0
        olfactorydisorder = 1 if request.form.get("olfactorydisorder")=="1" else 0
        dt_now = datetime.datetime.now()
        
        sqlstring = f"""
            SELECT * FROM healthmanagement WHERE recorddate = '{recorddate}' AND timezone = {timezone} AND userID = {session["userID"]};
        """
        my_query(sqlstring,cur)
        
        df = pd.DataFrame(cur.fetchall())
        
        if not df.empty:
            return render_template("msg.html", 
                title = "体調観察修正エラー", 
                msg = "既にその日のその時間帯(AM/PM)のデータは存在しています", 
                linkname = "体調観察確認", 
                link = "/checkhealth"
            )

        sqlstring = f"""
            UPDATE symptoms
            SET temperature = {temperature},
                jointpain = {jointpain},
                washedoutfeeling = {washedoutfeeling},
                headache = {headache},
                sorethroat = {sorethroat},
                breathless = {breathless},
                coughsneezing = {coughsneezing},
                nausea = {nausea},
                abdominalpain = {abdominalpain},
                tastedisorder = {tastedisorder},
                olfactorydisorder = {olfactorydisorder},
                lastupdate = '{dt_now}'
            WHERE symptomsID = {symptomsID}
        """
        my_query(sqlstring,cur)
        sqlstring = f"""
            UPDATE healthmanagement
            SET symptomsID = {symptomsID}, 
                userID = {session["userID"]}, 
                recorddate = '{recorddate}', 
                timezone = {timezone}, 
                lastupdate = '{dt_now}'
            WHERE symptomsID = {symptomsID}
        """
        my_query(sqlstring,cur)
        dbcon.commit()
        my_close(dbcon,cur)
        
        return render_template("msg.html", 
            title = "体調観察修正完了", 
            msg = "体調観察のデータを修正しました", 
            linkname = "体調観察確認", 
            link = "/checkhealth"
        )
    else:
        return render_template("msg.html", 
            title = "体調観察修正エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/conduct")
def conduct():
    if "usercode" in session:
        dt_now = datetime.datetime.now()
        return render_template("conduct.html", 
            title = "行動記録登録", 
            dt_now = dt_now
        )
    else:
        return render_template("msg.html", 
            title = "行動記録登録エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/conduct2", methods=["POST"])
def conduct2():
    recorddate = request.form["recorddate"]
    actiontime0 = request.form["actiontime0"]
    actiontime1 = request.form["actiontime1"]
    actiontime = actiontime0 + '~' + actiontime1
    location = request.form.get("location", "")
    movementmethod = request.form.get("movementmethod", "")
    dtp = request.form.get("dtp", "")
    arr = request.form.get("arr", "")
    companionflag = 1 if request.form.get("companionflag")=="1" else 0
    relationshipnum = request.form.get("relationshipnum", "")
    specialmention = request.form.get("specialmention", "")
    
    dbcon,cur = my_open(**dsn) 
    dt_now = datetime.datetime.now()
    
    sqlstring = f"""
        INSERT INTO conduct
        (userID,recorddate,actiontime,location,movementmethod,dtp,arr,companionflag,relationshipnum,specialmention,lastupdate)
        values
        ({session["userID"]},'{recorddate}','{actiontime}','{location}','{movementmethod}','{dtp}','{arr}',{companionflag},'{relationshipnum}','{specialmention}','{dt_now}')
        ;
    """
    
    my_query(sqlstring, cur)
    
    dbcon.commit()
    my_close(dbcon,cur)
    
    return render_template("msg.html", 
        title = "行動記録登録", 
        msg = "行動記録を登録しました", 
        linkname = "行動記録確認", 
        link = "/checkconduct"
    )

@app.route("/checkconduct")
def checkconduct():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn) 
        df_index = ["No", "日付", "時間", "場所(行先)", "移動方法", "出発地", "到着地", "同行者", "特記事項"]
        sqlstring = f"""
            SELECT * FROM conduct WHERE userID = {session["userID"]} ORDER BY recorddate ASC;
        """
        my_query(sqlstring, cur)

        df = pd.DataFrame(cur.fetchall())
        
        if df.empty:
            my_close(dbcon, cur)
            return render_template("msg.html", 
                title = "行動記録確認エラー", 
                msg = "行動記録が1件も登録されていません", 
                linkname = "行動記録登録", 
                link = "/conduct"
            )
        else:
            df = df.drop(columns=["conductID", "userID", "lastupdate"])
            for column in df.columns:
                if column == "companionflag":    
                    df.loc[df[column]==0, [column]]="無"
                    df.loc[df[column]==1, [column]]="有"
            
            my_close(dbcon, cur)
            return render_template("checkconduct.html", 
                title = "行動記録確認", 
                table_index = df_index, 
                table_data = df
            )
    else:
        return render_template("msg.html", 
            title = "行動記録確認エラー", 
            msg = "ログインできていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/changeconduct")
def changeconsuct():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn) 
        df_index = ["No", "日付", "時間", "場所(行先)", "移動方法", "出発地", "到着地", "同行者", "特記事項"]
        sqlstring = f"""
            SELECT * FROM conduct WHERE userID = {session["userID"]} ORDER BY recorddate ASC;
        """
        my_query(sqlstring, cur)

        df = pd.DataFrame(cur.fetchall())
        
        if df.empty:
            my_close(dbcon, cur)
            return render_template("msg.html", 
                title = "行動記録修正エラー", 
                msg = "行動記録が1件も登録されていません", 
                linkname = "行動記録確認", 
                link = "/checkconduct"
            )
        else:
            conductID = df["conductID"].to_list()
            df = df.drop(columns=["conductID", "userID", "lastupdate"])
            for column in df.columns:
                if column == "companionflag":    
                    df.loc[df[column]==0, [column]]="無"
                    df.loc[df[column]==1, [column]]="有"
            
            my_close(dbcon, cur)
            return render_template("changeconduct.html", 
                title = "行動記録確認", 
                table_index = df_index, 
                table_data = df, 
                conductID = conductID
            )
    else:
        return render_template("msg.html", 
            title = "行動記録修正エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/changeconduct2", methods=["POST"])
def changeconduct2():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn)
        conductID = request.form["conductID"]

        sqlstring = f"""
            SELECT * FROM conduct WHERE conductID = {conductID};
        """
        my_query(sqlstring,cur)
        recset = pd.DataFrame(cur.fetchall())
        actiontime = recset.iloc[0]["actiontime"]
        actiontime0 = actiontime[0:5]
        actiontime1 = actiontime[6:11]
        rowdata = pd.Series(recset.iloc[0])
        
        my_close(dbcon,cur)
        return render_template("changeconduct2.html", 
            title = "体調観察修正", 
            table_data = rowdata, 
            conductID = conductID, 
            actiontime0 = actiontime0, 
            actiontime1 = actiontime1
        )
    else:
        return render_template("msg.html", 
            title = "体調観察修正エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/changeconduct3", methods=["GET", "POST"])
def changeconduct3():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn)
        conductID = request.args.get('conductID', '')
        recorddate = request.form["recorddate"]
        actiontime0 = request.form["actiontime0"]
        actiontime1 = request.form["actiontime1"]
        actiontime = actiontime0 + '~' + actiontime1
        location = request.form.get("location", "")
        movementmethod = request.form.get("movementmethod", "")
        dtp = request.form.get("dtp", "")
        arr = request.form.get("arr", "")
        companionflag = 1 if request.form.get("companionflag")=="1" else 0
        relationshipnum = request.form.get("relationshipnum", "")
        specialmention = request.form.get("specialmention", "")
        dt_now = datetime.datetime.now()
        
        sqlstring = f"""
            UPDATE conduct
            SET userID = {session["userID"]}, 
                recorddate = '{recorddate}', 
                actiontime = '{actiontime}',
                location = '{location}',
                movementmethod = '{movementmethod}',
                dtp = '{dtp}',
                arr = '{arr}',
                companionflag = '{companionflag}',
                relationshipnum = '{relationshipnum}',
                specialmention = '{specialmention}', 
                lastupdate = '{dt_now}'
            WHERE conductID = {conductID}
        """
        my_query(sqlstring,cur)

        dbcon.commit()
        my_close(dbcon,cur)
        
        return render_template("msg.html", 
            title = "行動記録修正完了", 
            msg = "行動記録のデータを修正しました", 
            linkname = "行動記録確認", 
            link = "/checkconduct"
        )
    else:
        return render_template("msg.html", 
            title = "行動記録修正エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/infect")
def infect():
    if "usercode" in session:
        return render_template("infect.html", 
            title = "濃厚接触者・感染者登録"
        )
    else:
        return render_template("msg.html", 
            title = "濃厚接触者・感染者登録エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/infect2", methods=["POST"])
def infect2():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn)
        closecontact = 1 if request.form.get("closecontact")=="1" else 0
        infect = 1 if request.form.get("infect")=="1" else 0
        attendancestop = request.form.get("attendancestop", "")
        medicalinstitutionname = request.form.get("medicalinstitutionname", "")
        doctorname = request.form.get("doctorname", "")
        
        dt_now = datetime.datetime.now()
        sqlstring = f"""
            INSERT INTO infected
            (userID,closecontact,infect,attendancestop,medicalinstitutionname,doctorname,lastupdate)
            values
            ({session["userID"]},{closecontact},{infect},'{attendancestop}','{medicalinstitutionname}','{doctorname}','{dt_now}')
            ;
        """
        my_query(sqlstring,cur)

        dbcon.commit()
        my_close(dbcon,cur)
        
        return render_template("msg.html", 
            title = "濃厚接触者・感染者登録完了", 
            msg = "濃厚接触者・感染者のデータを登録しました", 
            linkname = "濃厚接触者・感染者確認", 
            link = "/checkinfect"
        )
    else:
        return render_template("msg.html", 
            title = "濃厚接触者・感染者登録エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/checkinfect")
def checkinfect():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn) 
        df_index = ["濃厚接触者", "感染者", "出席停止期間", "医療機関名", "医師氏名"]
        sqlstring = f"""
            SELECT * FROM infected WHERE userID = {session["userID"]};
        """
        my_query(sqlstring, cur)

        df = pd.DataFrame(cur.fetchall())
        
        if df.empty:
            my_close(dbcon, cur)
            return render_template("msg.html", 
                title = "濃厚接触者・感染者確認エラー", 
                msg = "行濃厚接触者・感染者の記録が1件も登録されていません", 
                linkname = "濃厚接触者・感染者登録", 
                link = "/infect"
            )
        else:
            df = df.drop(columns=["infectedID", "userID", "lastupdate"])
            for column in df.columns:    
                df.loc[df[column]==0, [column]]="いいえ"
                df.loc[df[column]==1, [column]]="はい"
            my_close(dbcon, cur)
        return render_template("checkinfect.html", 
            title = "濃厚接触者・感染者確認", 
            table_index = df_index, 
            table_data = df
        )
    else:
        return render_template("msg.html", 
            title = "濃厚接触者・感染者確認エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/changeinfect")
def changeinfect():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn) 
        df_index = ["濃厚接触者", "感染者", "出席停止期間", "医療機関名", "医師氏名"]
        sqlstring = f"""
            SELECT * FROM infected WHERE userID = {session["userID"]};
        """
        my_query(sqlstring, cur)

        df = pd.DataFrame(cur.fetchall())
        
        if df.empty:
            my_close(dbcon, cur)
            return render_template("msg.html", 
                title = "濃厚接触者・感染者修正エラー", 
                msg = "行濃厚接触者・感染者の記録が1件も登録されていません", 
                linkname = "濃厚接触者・感染者登録", 
                link = "/infect"
            )
        else:
            infectedID = df["infectedID"].to_list()
            df = df.drop(columns=["infectedID", "userID", "lastupdate"])
            for column in df.columns: 
                df.loc[df[column]==0, [column]]="いいえ"
                df.loc[df[column]==1, [column]]="はい"
            my_close(dbcon, cur)
        return render_template("changeinfect.html", 
            title = "濃厚接触者・感染者修正", 
            table_index = df_index, 
            table_data = df, 
            infectedID = infectedID
        )
    else:
        return render_template("msg.html", 
            title = "濃厚接触者・感染者修正エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/changeinfect2", methods=["POST"])
def changeinfect2():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn)
        infectedID = request.form["infectedID"]

        sqlstring = f"""
            SELECT * FROM infected WHERE infectedID = {infectedID};
        """
        my_query(sqlstring,cur)
        recset = pd.DataFrame(cur.fetchall())
        rowdata = pd.Series(recset.iloc[0])
        
        my_close(dbcon,cur)
        return render_template("changeinfect2.html", 
            title = "濃厚接触者・感染者修正", 
            table_data = rowdata, 
            infectedID = infectedID
        )
    else:
        return render_template("msg.html", 
            title = "体調観察修正エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/changeinfect3", methods=["GET", "POST"])
def changeinfect3():
    if "usercode" in session:
        dbcon,cur = my_open(**dsn)
        infectedID = request.args.get('infectedID', '')
        closecontact = 1 if request.form.get("closecontact")=="1" else 0
        infect = 1 if request.form.get("infect")=="1" else 0
        attendancestop = request.form.get("attendancestop", "")
        medicalinstitutionname = request.form.get("medicalinstitutionname", "")
        doctorname = request.form.get("doctorname", "")
        dt_now = datetime.datetime.now()
        
        sqlstring = f"""
            UPDATE infected
            SET userID = {session["userID"]}, 
                closecontact = {closecontact},
                infect = {infect},
                attendancestop = '{attendancestop}',
                medicalinstitutionname = '{medicalinstitutionname}',
                doctorname = '{doctorname}', 
                lastupdate = '{dt_now}'
            WHERE infectedID = {infectedID}
        """
        my_query(sqlstring,cur)

        dbcon.commit()
        my_close(dbcon,cur)
        
        return render_template("msg.html", 
            title = "濃厚接触者・感染者修正完了", 
            msg = "濃厚接触者・感染者のデータを修正しました", 
            linkname = "濃厚接触者・感染者確認", 
            link = "/checkinfect"
        )
    else:
        return render_template("msg.html", 
            title = "濃厚接触者・感染者修正エラー", 
            msg = "ログインしていません", 
            linkname = "ログイン", 
            link = "/login"
        )

@app.route("/admin/top")
def admintop():
    if "admin" in session:
        return render_template("admintop.html", 
            title = "[管理者]トップ"
        )
    else:
        return render_template("msg.html", 
            title = "[管理者]トップエラー", 
            msg = "あなたは管理者ではありません",  
            linkname = "ログアウト", 
            link = "/logout"
        )

@app.route("/admin/user")
def adminuser():
    if "admin" in session:
        dbcon,cur = my_open(**dsn)
        df_index = ["ユーザID", "学籍(個人)番号", "学科/部課室", "氏名", "種類", "携帯番号", "メールアドレス"]
        
        sqlstring = f"""
            SELECT * FROM user;
        """
        
        my_query(sqlstring,cur)
        df = pd.DataFrame(cur.fetchall()).drop(columns=["userpassword", "adminflag", "lastupdate"])
        my_close(dbcon,cur)
        return render_template("adminuser.html", 
            title = "[管理者]ユーザ一覧", 
            table_data = df, 
            table_index = df_index
        )
    else:
        return render_template("msg.html", 
            title = "[管理者]ユーザ一覧エラー", 
            msg = "あなたは管理者ではありません", 
            linkname = "ログアウト", 
            link = "/logout"
        ) 

@app.route("/admin/infect")
def admininfect():
    if "admin" in session:
        dbcon,cur = my_open(**dsn)
        
        sqlstring = f"""
            SELECT * FROM infected WHERE infect = 1;
        """
        
        my_query(sqlstring,cur)
        
        df_infect = pd.DataFrame(cur.fetchall())
        
        if df_infect.empty:
            return render_template("msg.html", 
                title = "[管理者]感染者ユーザ一覧", 
                msg = "感染者は一人も居ません", 
                linkname = "[管理者]トップ", 
                link = "/admin/top"
            )
        
        infect_userID_list = df_infect["userID"].to_list()
        infect_attendancestop_list = df_infect["attendancestop"].to_list
        
        df_index = ["ユーザID", "学籍(個人)番号", "学科/部課室", "氏名", "種類", "携帯番号", "メールアドレス", "出席停止期間"]
        
        stmt_formats = ','.join(['%s'] * len(infect_userID_list))
        stmt = """
            SELECT * FROM user WHERE userID IN (%s)
        """
        ## プリペアードステートメント実行
        cur.execute(
            stmt % stmt_formats, 
            tuple(infect_userID_list) 
        )
        
        df = pd.DataFrame(cur.fetchall()).drop(columns=["userpassword", "adminflag", "lastupdate"])
        
        infect_total_num = len(df)
        
        my_close(dbcon,cur)
        return render_template("admininfect.html", 
            title = "[管理者]感染者ユーザ一覧", 
            table_data = df, 
            table_index = df_index, 
            attendancestop = infect_attendancestop_list, 
            infect_total_num = infect_total_num
        )
    else:
        return render_template("msg.html", 
            title = "[管理者]感染者ユーザ一覧エラー", 
            msg = "あなたは管理者ではありません", 
            linkname = "ログアウト", 
            link = "/logout"
        ) 

@app.route("/admin/norecord3days")
def norecord3days():
    if "admin" in session:
        dt_now = datetime.datetime.now()
        df_index = ["ユーザID", "学籍(個人)番号", "学科/部課室", "氏名", "種類", "携帯番号", "メール通知"]
    
        dbcon,cur = my_open(**dsn)
        
        norecord3days_userID_list = []
        #体調管理の記録を3日以上行っていないユーザを確認
        sqlstring = f"""
            SELECT * FROM healthmanagement;
        """
        my_query(sqlstring,cur)
        df_health = pd.DataFrame(cur.fetchall())
        if df_health.empty:
            return render_template("msg.html", 
                title = "[管理者]3日以上連続で記録がないユーザ一覧エラー", 
                msg = "体調観察データが1件もありません", 
                linkname = "[管理者]トップ", 
                link = "/admin/top"
            )
        healthmanagementID = 1
        for date in df_health["recorddate"]:
            continueflag = 0
            dt_native = datetime.datetime.combine(date, datetime.time())
            dif_date = dt_now - dt_native
            dif_date_str = str(dif_date)[0:4]
            dif_date_int = ""
            for i in dif_date_str:
                if i.isspace():
                    break
                elif i == ':' :
                    continueflag = 1    
                else:
                    dif_date_int += i
            if continueflag == 1:
                continue
            dif_date_int = int(dif_date_int)
            if dif_date_int >= 3:
                sqlstring = f"""
                    SELECT * FROM healthmanagement WHERE healthmanagementID = {healthmanagementID};
                """
                my_query(sqlstring,cur)
                df = pd.DataFrame(cur.fetchall())
                if df.empty:
                    continue
                else:    
                    norecord3days_userID_list.append(str(df.userID[0]))
            healthmanagementID += 1
        
        #行動記録を3日以上行っていないユーザを確認
        sqlstring = f"""
            SELECT * FROM conduct;
        """
        my_query(sqlstring,cur)
        df_conduct = pd.DataFrame(cur.fetchall())
        if df_conduct.empty:
            return render_template("msg.html", 
                title = "[管理者]3日以上連続で記録がないユーザ一覧エラー", 
                msg = "行動記録データが1件もありません", 
                linkname = "[管理者]トップ", 
                link = "/admin/top"
            )
        conductID =1
        for date in df_conduct["recorddate"]:
            dt_native = datetime.datetime.combine(date, datetime.time())
            dif_date = dt_now - dt_native
            dif_date = int(str(dif_date)[0:2])
            if dif_date >= 3:
                sqlstring = f"""
                    SELECT * FROM conduct WHERE conductID = {conductID};
                """
                my_query(sqlstring,cur)
                df = pd.DataFrame(cur.fetchall())
                if df.empty:
                    continue
                else:    
                    norecord3days_userID_list.append(str(df.userID[0]))
            conductID += 1
        
        norecord3days_userID_list = list(set(norecord3days_userID_list))

        stmt_formats = ','.join(['%s'] * len(norecord3days_userID_list))
        stmt = """
            SELECT * FROM user WHERE userID IN (%s);
        """
        ## プリペアードステートメント実行
        cur.execute(
            stmt % stmt_formats, 
            tuple(norecord3days_userID_list) 
        )
        
        df = pd.DataFrame(cur.fetchall()).drop(columns=["userpassword", "adminflag", "lastupdate"])
        
        return render_template("pickup.html", 
            title = "3日以上連続で記録がないユーザ一覧", 
            table_data = df, 
            table_index = df_index, 
            pickupflag = 0 # 0:3日以上記録なし, 1:体調不良
        )
    else:
        return render_template("msg.html", 
            title = "[管理者]感染者ユーザ一覧エラー", 
            msg = "あなたは管理者ではありません", 
            linkname = "ログアウト", 
            link = "/logout"
        )

@app.route("/admin/check")
def admincheck():
    if "admin" in session:
        df_index = ["ユーザID", "学籍(個人)番号", "学科/部課室", "氏名", "種類", "携帯番号", "メール通知"]
    
        dbcon,cur = my_open(**dsn)
        
        temperature_userID_list = []
        symptoms_userID_list = []
        # 体調不良なユーザを確認
        # 体調不良とは以下を満たす
        # 体温が37.5度以上
        # 関節痛・だるさなどの症状が5個以上チェックされている
        sqlstring = f"""
            SELECT * FROM health_symptoms;
        """
        my_query(sqlstring,cur)
        df = pd.DataFrame(cur.fetchall())
        print(df)
        if df.empty:
            return render_template("msg.html", 
                title = "[管理者]体調不良なユーザ一覧エラー", 
                msg = "体調観察データが1件もありません", 
                linkname = "[管理者]トップ", 
                link = "/admin/top"
            )
        
        # 体温が37.5度以上のユーザを確認
        symptomsID = 1
        for data in df["temperature"]:
            if data >= 37.5:
                sqlstring = f"""
                    SELECT * FROM healthmanagement WHERE symptomsID = {symptomsID};
                """
                my_query(sqlstring,cur)
                df_temperature = pd.DataFrame(cur.fetchall())
                if df_temperature.empty:
                    continue
                else:
                    temperature_userID_list.append(str(df_temperature.userID[0]))
            symptomsID += 1
        print(temperature_userID_list)
        # 体調不良なユーザを確認
        i = 0
        for symptomsID in df["symptomsID"]:
            sqlstring = f"""
                SELECT * FROM symptoms WHERE symptomsID = {symptomsID};
            """
            my_query(sqlstring,cur)
            df_symptoms = pd.DataFrame(cur.fetchall())
            if df_symptoms.empty:
                continue
            else:
                df_bool = df_symptoms.drop(columns=["symptomsID"]) == 1
                if df_bool.sum(axis=1)[0] >= 5:
                    symptoms_userID_list.append(str(df.userID[i]))
            i+= 1
        userID_list = list(set(temperature_userID_list) & set(symptoms_userID_list))
        
        if not userID_list:
            return render_template("msg.html", 
            title = "[管理者]体調不良なユーザ一覧エラー", 
            msg = "体調不良なユーザはいません", 
            linkname = "[管理者]トップ", 
            link = "/admin/top"
        )

        stmt_formats = ','.join(['%s'] * len(userID_list))
        stmt = """
            SELECT * FROM user WHERE userID IN (%s);
        """
        # プリペアードステートメント実行
        cur.execute(
            stmt % stmt_formats, 
            tuple(userID_list) 
        )
        
        df = pd.DataFrame(cur.fetchall()).drop(columns=["userpassword", "adminflag", "lastupdate"])
        
        return render_template("pickup.html", 
            title = "体調不良なユーザ一覧", 
            table_data = df, 
            table_index = df_index, 
            pickupflag = 1 # 0:3日以上記録なし, 1:体調不良
        )
    else:
        return render_template("msg.html", 
            title = "[管理者]体調不良なユーザ一覧エラー", 
            msg = "あなたは管理者ではありません", 
            linkname = "ログアウト", 
            link = "/logout"
        )
        
@app.route("/admin/sendemail", methods=["GET", "POST"])
def sendemail():
    if "admin" in session:
        pickupflag = request.args.get("pickupflag", "")

        # メール情報の設定
        from_email ='detabesu18@gmail.com'      # 送信者 
        to_email = request.form["email"]        # 受信者
        smtp_host = 'smtp.gmail.com'            # ポートアドレス
        smtp_port = 587                         # ポート番号
        smtp_password = 'ihhd bzcn kbzy yigg'   # メールパスワード
        
        if pickupflag == "0":
            # メール件名とメッセージ本文  
            mail_title = 'COVID19管理システムからのお願い'
            message = '3日以上入力が行われていません。入力をお願いします。'
            # MIMEオブジェクトでメールを作成
            msg = MIMEText(message, 'plain')
            msg['Subject'] = mail_title
            msg['To'] = to_email
            msg['From'] = from_email
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
                server.login(from_email, smtp_password)
                server.send_message(msg)
            return render_template("msg.html", 
                title = "[管理者]メール送信", 
                msg = "メールを送信しました", 
                linkname = "[管理者]トップ", 
                link = "/admin/top"
            )
        elif pickupflag == "1":
            mail_title = 'COVID19管理システムからのお知らせ'
            message = '体調不良に見受けられます。病院で診て貰いましょう。'
            # MIMEオブジェクトでメールを作成
            msg = MIMEText(message, 'plain')
            msg['Subject'] = mail_title
            msg['To'] = to_email
            msg['From'] = from_email
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
                server.login(from_email, smtp_password)
                server.send_message(msg)
            return render_template("msg.html", 
                title = "[管理者]メール送信", 
                msg = "メールを送信しました", 
                linkname = "[管理者]トップ", 
                link = "/admin/top"
            )
        else:
            return render_template("msg.html", 
                title = "[管理者]体調不良なユーザ一覧エラー", 
                msg = "謎のエラー発生", 
                linkname = "[管理者]トップ", 
                link = "/admin/top"
            )
    else:
        return render_template("msg.html", 
            title = "[管理者]メール送信エラー", 
            msg = "あなたは管理者ではありません", 
            linkname = "ログアウト", 
            link = "/logout"
        )

@app.route("/admin/userinfo")
def adminuserinfo():
    if "admin" in session:
        return render_template("adminuserinfo.html", 
            title = "[管理者]各ユーザの情報確認"
        )
    else:
        return render_template("msg.html", 
            title = "[管理者]メール送信エラー", 
            msg = "あなたは管理者ではありません", 
            linkname = "ログアウト", 
            link = "/logout"
        )

@app.route("/admin/userinfo2", methods=["POST"])
def adminuserinfo2():
    if "admin" in session:
        userID = request.form.get('userID', '')
        kind = request.form.get("kind", "")

        session["userID"] = userID
        
        if kind=="health":
            dbcon,cur = my_open(**dsn)
            sqlstring = f"""
                SELECT * FROM health_symptoms WHERE timezone=0 AND userID='{session["userID"]}' ORDER BY recorddate ASC;
            """
            my_query(sqlstring, cur)
            df_AM = pd.DataFrame(cur.fetchall())
            
            sqlstring = f"""
                SELECT * FROM health_symptoms WHERE timezone=1 AND userID='{session["userID"]}' ORDER BY recorddate ASC;
            """
            my_query(sqlstring, cur)
            df_PM = pd.DataFrame(cur.fetchall())
            
            # HTMLで表記する際のindexを作成
            df_index = ["体温", " 関節・筋肉痛", "だるさ", "頭痛", "咽頭痛", "息苦しさ", "咳・くしゃみ", "吐気・嘔吐", "腹痛・下痢", "味覚障害", "嗅覚障害"]

            # AM, PMにデータがないときにmsg.htmlでreturn
            if df_AM.empty:
                if df_PM.empty: 
                    my_close(dbcon, cur)
                    return render_template("msg.html", 
                        title = "体調観察確認エラー", 
                        msg = "記録が1件もありません", 
                        linkname = "体調観察登録", 
                        link = "/health"
                    )
                else:
                    df_PM = df_PM.drop(columns=["symptomsID", "userID", "timezone"])
                    date_list_PM = df_PM["recorddate"].to_list()
                    date_list = sorted(list(set(date_list_PM)))
                    for column in df_PM.columns:
                        df_PM.loc[df_PM[column]==0, [column]]=""
                        df_PM.loc[df_PM[column]==1, [column]]="有り"
                    df_PM["temperature"] = df_PM["temperature"].astype(str) + "℃"
                    df_PM["recorddate"] = pd.to_datetime(df_PM["recorddate"])
                    df_PM = df_PM.sort_values("recorddate").drop(columns="recorddate").T
                    my_close(dbcon, cur)
                    return render_template("checkhealth.html",
                        title = "体調観察確認", 
                        date_list = date_list, 
                        table_index = df_index, 
                        table_data_AM = df_AM, 
                        table_data_PM = df_PM
                    )
            else:
                if df_PM.empty:
                    df_AM = df_AM.drop(columns=["symptomsID", "userID", "timezone"])
                    date_list_AM = df_AM["recorddate"].to_list()
                    date_list = sorted(list(set(date_list_AM)))
                    for column in df_AM.columns:
                        df_AM.loc[df_AM[column]==0, [column]]=""
                        df_AM.loc[df_AM[column]==1, [column]]="有り"
                    df_AM["temperature"] = df_AM["temperature"].astype(str) + "℃"
                    df_AM["recorddate"] = pd.to_datetime(df_AM["recorddate"])
                    df_AM = df_AM.sort_values("recorddate").drop(columns="recorddate").T
                    my_close(dbcon, cur)
                    return render_template("checkhealth.html",
                        title = "体調観察確認", 
                        date_list = date_list, 
                        table_index = df_index, 
                        table_data_AM = df_AM, 
                        table_data_PM = df_PM
                    )
                else:
                    df_AM = df_AM.drop(columns=["symptomsID", "userID", "timezone"])
                    df_PM = df_PM.drop(columns=["symptomsID", "userID", "timezone"])
                    
                    # AMとPMでどちらかしか登録がないかどうかを確認するためのdate_listを作成するためにAM, PMのrecorddateをリストにする
                    date_list_AM = df_AM["recorddate"].to_list()
                    date_list_PM = df_PM["recorddate"].to_list()
                    
                    # AMとPMでどちらかしか登録がないかどうかを確認するためのdate_listを作成
                    # 重複を削除し, listにした後ソートする.
                    date_list = sorted(list(set(date_list_AM + date_list_PM)))
                    
                    # AMとPMでどちらかしか登録がない場合に, recorddateをその日付に, その他は空にしたものをDFに追加
                    for i in date_list:
                        if not (i in date_list_AM):
                            df_AM.loc[i] = [i, "", "", "", "", "", "", "", "", "", "", ""]
                        
                        if not (i in date_list_PM):
                            df_PM.loc[i] = [i, "", "", "", "", "", "", "", "", "", "", ""]
                    
                    # HTML表示を見据えて, データが0なら空白, 1なら有りに変換
                    for column in df_AM.columns:
                        df_AM.loc[df_AM[column]==0, [column]]=""
                        df_AM.loc[df_AM[column]==1, [column]]="有り"
                    
                    for column in df_PM.columns:
                        df_PM.loc[df_PM[column]==0, [column]]=""
                        df_PM.loc[df_PM[column]==1, [column]]="有り"
                    
                    # 体温に単位を付ける
                    df_AM["temperature"] = df_AM["temperature"].astype(str) + "℃"
                    df_PM["temperature"] = df_PM["temperature"].astype(str) + "℃"

                    # 日付でソートするためにrecorddateの型をstrからdatetimeに変換
                    df_AM["recorddate"] = pd.to_datetime(df_AM["recorddate"])
                    df_PM["recorddate"] = pd.to_datetime(df_PM["recorddate"])
                    
                    # HTMLで表示する際にはrecorddateは要らないので削除
                    df_AM = df_AM.sort_values("recorddate").drop(columns="recorddate").T
                    df_PM = df_PM.sort_values("recorddate").drop(columns="recorddate").T
                        
                    my_close(dbcon, cur)
                    return render_template("checkhealth.html",
                        title = "体調観察確認", 
                        date_list = date_list, 
                        table_index = df_index, 
                        table_data_AM = df_AM, 
                        table_data_PM = df_PM
                    )
        elif kind=="conduct":
            dbcon,cur = my_open(**dsn) 
            df_index = ["No", "日付", "時間", "場所(行先)", "移動方法", "出発地", "到着地", "同行者", "特記事項"]
            sqlstring = f"""
                SELECT * FROM conduct WHERE userID = {session["userID"]} ORDER BY recorddate ASC;
            """
            my_query(sqlstring, cur)

            df = pd.DataFrame(cur.fetchall())
            
            if df.empty:
                my_close(dbcon, cur)
                return render_template("msg.html", 
                    title = "行動記録確認エラー", 
                    msg = "行動記録が1件も登録されていません", 
                    linkname = "行動記録登録", 
                    link = "/conduct"
                )
            else:
                df = df.drop(columns=["conductID", "userID", "lastupdate"])
                for column in df.columns:
                    if column == "companionflag":    
                        df.loc[df[column]==0, [column]]="無"
                        df.loc[df[column]==1, [column]]="有"
                
                my_close(dbcon, cur)
                return render_template("checkconduct.html", 
                    title = "行動記録確認", 
                    table_index = df_index, 
                    table_data = df
                )
        else:
            dbcon,cur = my_open(**dsn) 
            df_index = ["濃厚接触者", "感染者", "出席停止期間", "医療機関名", "医師氏名"]
            sqlstring = f"""
                SELECT * FROM infected WHERE userID = {session["userID"]};
            """
            my_query(sqlstring, cur)

            df = pd.DataFrame(cur.fetchall())
            
            if df.empty:
                my_close(dbcon, cur)
                return render_template("msg.html", 
                    title = "濃厚接触者・感染者確認エラー", 
                    msg = "行濃厚接触者・感染者の記録が1件も登録されていません", 
                    linkname = "濃厚接触者・感染者登録", 
                    link = "/infect"
                )
            else:
                df = df.drop(columns=["infectedID", "userID", "lastupdate"])
                for column in df.columns:    
                    df.loc[df[column]==0, [column]]="いいえ"
                    df.loc[df[column]==1, [column]]="はい"
                my_close(dbcon, cur)
            return render_template("checkinfect.html", 
                title = "濃厚接触者・感染者確認", 
                table_index = df_index, 
                table_data = df
            )
    else:
        return render_template("msg.html", 
            title = "[管理者]メール送信エラー", 
            msg = "あなたは管理者ではありません", 
            linkname = "ログアウト", 
            link = "/logout"
        )

#プログラム起動
app.run(host="localhost",port=5000,debug=True)