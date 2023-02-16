import json
import random
import re
import shutil
import sys

version="1.0"
tiptext=[f"这是一条 {version} 版本专属的提示~",
         "本项目的仓库地址: https://github.com/whb04/phigros-helper",
         "启动时及使用tip指令时会随机显示一条提示, 可以使用tips指令查看所有提示",
         "帮助中的竖线表示选择一个, 如help|h|?表示输入help或h或?都可以查看帮助",
         "帮助中尖括号中的内容表示必填, 方括号中的内容表示选填",
         "要根据曲名查询歌曲信息, 可以使用list和show指令",
         "歌曲ID是所有歌曲按名称排序的序号, 增加或删除歌曲可能会改变其他歌曲的ID",
         "可以在README.md中查看修改设置的方法",
         "当前歌曲ID指上次查询或修改的歌曲的ID, 可以输入s查看",
         "许多常用命令都有简写, 通常是首字母",
         "输入准确率(acc)时小数点可省略(此时必须输入四到五位整数), 98.76% 98.76 9876 100. 10000 都是合法的输入",
         "如果你想在更新成绩时手动选择难度, 请将config.json中的auto_diff设置为false"]
curid=None
nameid={}
randlist=[]

def upd_id():
    cnt=0
    global nameid
    nameid={}
    data["songs"].sort(key=lambda song:song["name"])
    for song in data["songs"]:
        cnt+=1
        nameid[song["name"]]=cnt
def upd_randlist():
    global randlist
    randlist=[]
    for song in data["songs"]:
        lim=conf["rand_ignore"]
        old="score" in song or "acc" in song
        phi=False
        for key in conf["play"]:
            if key in song and "score" in song[key]:
                if song[key]["score"]==1000000:
                    phi=True
                break
        if lim["old"] and old: continue
        if lim["new"] and not old: continue
        if lim["phi"] and phi: continue
        randlist.append(nameid[song["name"]])

def help():
    print("backup|b    # 备份当前数据到data.json.bak")
    print("clear    # 清除所有歌曲的成绩数据")
    print("help|h|?    # 查看指令帮助")
    print("list|l [key]    # 列出所有名称中含有key的歌曲, 若不填则列出所有歌曲")
    print("modify|m [歌曲ID]    # 修改当前或指定ID歌曲的成绩(覆盖原有的)")
    print("random|r    # 随机抽取一首歌")
    print("show|s [歌曲ID]    # 查询当前或指定ID歌曲的信息")
    print("stop|exit    # 终止程序")
    print("tip|t    # 随机显示一条提示")
    print("tips    # 查看所有提示")
    print("update|u [歌曲ID]    # 更新当前或指定ID歌曲的成绩(保留较好的)")
def tip():
    print("Tip:",random.choice(tiptext))
def tips():
    for tip in tiptext:
        print(tip)    
def showlist(key=None):
    for song in data["songs"]:
        if key==None or song["name"].count(key)>0:
            print("{:>4} ".format(nameid[song["name"]]),f"\033[0;33m{song['name']}\033[0m")
def show(id):
    try:
        song=data["songs"][id-1]
    except:
        print("\033[0;31mID无效\033[0m")
        return
    print("{:>4} ".format(nameid[song["name"]]),f"\033[0;33m{song['name']}\033[0m")
    for key in conf["show"]:
        if not key in song: continue
        p=song[key]
        print(f"[{key.upper()} {p['diff']//10}.{p['diff']%10}]",end=" ")
        if "score" in p:
            print("{:07}".format(p["score"]),end=" ")
        if "acc" in p:
            print("{:02}.{:02}%".format(p["acc"]//100,p["acc"]%100),end=" ")
        print()
    global curid
    curid=id
def rand():
    global randlist
    show(random.randint(1,len(randlist)))
def update(id,cover):
    try:
        if id<1:
            raise ValueError
        song=data["songs"][id-1]
    except:
        print("\033[0;31mID无效\033[0m")
        return
    global curid
    curid=id
    cnt=len(set(conf["play"])&set(song.keys()))
    for key in conf["play"]:
        if key in song:
            p=song[key]
            break
    print("当前选择的歌曲:",f"[{key.upper()} {p['diff']//10}.{p['diff']%10}]",f"\033[0;33m{song['name']}\033[0m")
    if not conf["auto_diff"] or cnt>1:
        print("若要修改难度请输入难度, 否则直接回车")
        diff=input()
        if diff!="":
            try:
                diff=diff.lower()
                p=song[diff]
            except:
                print("\033[0;31m难度无效\033[0m")
    print("若要更新分数请输入分数, 否则直接回车. 若您AP了, 可直接输入p")
    phi=False
    score=input()
    if score!="":
        try:
            if score=="p" or score=="P":
                phi=True
                score=1000000
            else:
                score=int(score)
            if score<0 or score>1000000:
                raise ValueError
            if cover or not "score" in p:
                p["score"]=score
            else:
                p["score"]=max(score,p["score"])
        except:
            print("\033[0;31m分数无效\033[0m")
            return
    if phi:
        p["acc"]=10000
    else:
        print("若要更新准确率请输入准确率, 否则直接回车")
        acc=input()
        if acc!="":
            try:
                if acc[-1]=="%":
                    acc=acc[:-1]
                if acc.count(".")==1:
                    acc=acc.split(".")
                    if acc[1]=="":
                        acc[1]="00"
                    acc=int(acc[0])*100+int(acc[1])
                else:
                    if len(acc)<4 or len(acc)>5:
                        raise ValueError
                    acc=int(acc)
                if acc<0 or acc>10000:
                    raise ValueError
                if cover or not "acc" in p:
                    p["acc"]=acc
                else:
                    p["acc"]=max(acc,p["acc"])
            except:
                print("\033[0;31m准确率无效\033[0m")
                return
    upd_randlist()
    with open("data.json","w") as fp:
        json.dump(data,fp,indent=4)
def clear():
    print("是否要备份当前数据(y/n)")
    if input()!="n":
        backup()
    print("即将清除所有歌曲的成绩数据, 请确认(y/n)")
    if input()!="y":
        return
    for song in data["songs"]:
        for key in song:
            if "score" in song[key]:
                del song[key]["score"]
            if "acc" in song[key]:
                del song[key]["acc"]
    with open("data.json","w") as fp:
        json.dump(data,fp,indent=4)
    print("清除成功")
def backup():
    shutil.copy("data.json","data.json.bak")
    print("备份成功")
def stop():
    sys.exit()

print(f"\033[1;36mPhigros Helper {version}\033[0m")
with open("config.json") as fp:
    conf=json.load(fp)
print(f"读取配置成功")
with open("data.json") as fp:
    data=json.load(fp)
print(f"读取曲目列表成功, 版本为 {data['version']}")
if conf["show_tip"]:
    print(f"Tip: {random.sample(tiptext,1)[0]}")
upd_id()
upd_randlist()
print("启动成功, 输入 ? 获取帮助")
while True:
    print("\033[0;36m>\033[0m",end=" ")
    op=input()
    ins=op.split(' ')
    match ins[0]:
        case "backup"|"b":
            backup()
        case "clear":
            clear()
        case "help"|"h"|"?":
            help()
        case "list"|"l":
            if len(ins)>1:
                showlist(ins[1])
            else:
                showlist()
        case "modify"|"m":
            if len(ins)>1:
                try:
                    update(int(ins[1]),True)
                except:
                    print("\033[0;31m参数错误\033[0m")
            else:
                update(curid,True)
        case "random"|"r":
            rand()
        case "show"|"s":
            if len(ins)>1:
                show(int(ins[1]))
            else:
                show(curid)
        case "stop"|"exit":
            stop()
        case "tip"|"t":
            tip()
        case "tips":
            tips()
        case "update"|"u":
            if len(ins)>1:
                try:
                    update(int(ins[1]),False)
                except:
                    print("\033[0;31m参数错误\033[0m")
            else:
                update(curid,False)
        case _:
            print("未知指令, 输入 ? 获取帮助")

# 计划: 新增、删除、修改歌曲信息; rks计算; 智能推荐; b19查询; 随机选歌黑/白名单; 完善list指令