from MyDatabase import my_open , my_query , my_close
import pandas as pd
import datetime

#Data Source Nameのパラメータを辞書型変数で定義しオープン
dsn = {
    'host' : '',  #ホスト名(IPアドレス)
    'port' : '',        #mysqlの接続ポート番号
    'user' : 'root',      #dbアクセスするためのユーザid
    'password' : '',    #ユーザidに対応するパスワード
    'database' : 'covid19' #オープンするデータベース名
}
dbcon,cur = my_open(**dsn)

#5つのファイル名をlist変数として保存
filename = ["./csv/user.csv","./csv/symptoms.csv","./csv/healthmanagement.csv","./csv/conduct.csv","./csv/infect.csv",]

#現在の日時を取得
dt_now = datetime.datetime.now()

#7つのファイルを処理するための繰り返し処理
for fn in filename:
    df = pd.read_csv(fn,header=0)
    for ind,rowdata in df.iterrows():
        if fn == "./csv/user.csv" :
            #userテーブルの場合
            sqlstring = f"""
                INSERT INTO user
                (usercode,userpassword,facultyoffice,namae,kind,phone,email,adminflag,lastupdate)
                values
                ('{rowdata[0]}','{rowdata[1]}','{rowdata[2]}','{rowdata[3]}','{rowdata[4]}','{rowdata[5]}','{rowdata[6]}',0,'{dt_now}')
                ;
            """
        elif fn == "./csv/symptoms.csv" :
            #symptomsテーブルの場合
            sqlstring = f"""
                INSERT INTO symptoms
                (temperature,jointpain,washedoutfeeling,headache,sorethroat,breathless,coughsneezing,nausea,abdominalpain,tastedisorder,olfactorydisorder,lastupdate)
                values
                ({rowdata[0]},{rowdata[1]},{rowdata[2]},{rowdata[3]},{rowdata[4]},{rowdata[5]},{rowdata[6]},{rowdata[7]},{rowdata[8]},{rowdata[9]},{rowdata[10]},'{dt_now}')
                ;
            """
        elif fn == "./csv/healthmanagement.csv" : 
            #healthmanagementテーブルの場合
            sqlstring = f"""
                INSERT INTO healthmanagement
                (symptomsID,userID,recorddate,timezone,lastupdate)
                values
                ({rowdata[0]},{rowdata[1]},'{rowdata[2]}',{rowdata[3]},'{dt_now}')
                ;
            """
        elif fn == "./csv/conduct.csv":
            #conductテーブルの場合
            sqlstring = f"""
                INSERT INTO conduct
                (userID,recorddate,actiontime,location,movementmethod,dtp,arr,companionflag,relationshipnum,specialmention,lastupdate)
                values
                ({rowdata[0]},'{rowdata[1]}','{rowdata[2]}','{rowdata[3]}','{rowdata[4]}','{rowdata[5]}','{rowdata[6]}',{rowdata[7]},'{rowdata[8]}','{rowdata[9]}','{dt_now}')
                ;
            """
        else:
            #infectdテーブルの場合
            sqlstring = f"""
                INSERT INTO infected
                (userID,closecontact,infect,attendancestop,medicalinstitutionname,doctorname,lastupdate)
                values
                ({rowdata[0]},{rowdata[1]},{rowdata[2]},'{rowdata[3]}','{rowdata[4]}','{rowdata[5]}','{dt_now}')
                ;
            """

        my_query(sqlstring, cur)

    #INSERT文を実行するループが終了し，結果をフィードバック
    print(f"{fn}を{len(df)}レコードを新規挿入しました")

    dbcon.commit()  
    
my_close(dbcon, cur)
