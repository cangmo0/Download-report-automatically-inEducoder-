import requests
import sys
import json
import re
from selenium import webdriver
import os
import time
import shutil

#  ppf2aex9b
uname = input("your count:")  # 账号
passwd = input("your password:")  # mima
need = input("which you want to download?(input all or your class name like 'python机器学习实验'):")

loginUrl = 'https://www.educoder.net/api/accounts/login.json'  # 登录url
baseUrl = 'https://www.educoder.net/api'  # apiUrl
url = 'https://www.educoder.net'  # url
#  post登录所需json数据
data = {
    'login': uname,
    "password": passwd,
    "autologin": True
}
# 通用头部
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36Content-Type: application/json; charset=utf-8',
    'Origin': 'https://www.educoder.net',
    'Referer': 'https://www.educoder.net/',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Content-Type': "application/json; charset=utf-8",
}
# 维持会话
r = requests.session()
# 登录返回结果
loginRes = r.post(loginUrl, headers=header, data=json.dumps(data))
# 获取用户的标识,用以构造访问用户所有的班级的url，如下面url的ppf2aex9b
loginDic = json.loads(loginRes.text)
# print(j['user_url'])
# https://www.educoder.net/api/users/ppf2aex9b/courses.json?category=undefined&status=undefined&page=1&per_page=16&sort_by=updated_at&sort_direction=desc&username=ppf2aex9b

print(loginRes.text)

# 访问用户班级的url
classUrl = baseUrl + loginDic['user_url'] + '/courses.json?category=undefined&status=undefined&page=1&per_page=16' \
                                            '&sort_by=updated_at&sort_direction=desc&username=ppf2aex9b'
# 获取班级的url(包含id)和名称
classRes = r.get(classUrl, headers=header)
classDic = json.loads(classRes.text)
classDic = classDic['courses']
classUrls = []  # 存储班级url
classNames = []  # 存储班级名称
for i in range(len(classDic)):
    each = classDic[i]
    if need != "all" and need not in each['name']:
        continue
    classUrls.append(each['first_category_url'])
    classNames.append(each['name'])

# https://www.educoder.net/api/courses/9069/left_banner.json?id=9069
# 实训作业分类url
catalogUrls = []
# 实训作业分类名称
catalogNames = []
# 作业url
fileUrlss = []
# 作业名称
fileNamess = []
for index in range(len(classUrls)):
    each = classUrls[index]
    dirs = []
    fileNames = []
    # 班级id
    classId = re.search(r'\d+', each).group()
    # 构造获取班级实训作业中的分类url
    catalogResUrl = baseUrl + '/courses/' + classId + "/left_banner.json?id=" + classId
    # print(catalogResUrl)
    catalogRes = r.get(catalogResUrl, headers=header).text
    catalogDic = json.loads(catalogRes)
    catalogDic = catalogDic['course_modules']
    for i in catalogDic:
        if i['name'] == '实训作业':
            catalogDic = i
    # 获取分类结果
    catalogDicRes = catalogDic['second_category']
    # 存储每个班级的分类url
    catalogUrl = []
    # 存储每个班级的分类名称
    catalogName = []
    fileIds = []
    fileUrls = []
    if catalogDicRes == "" or catalogDicRes is None or len(catalogDicRes) == 0:
        catalogDic = [catalogDic['category_url']]
        print(catalogDic)
    else:
        catalogDic = catalogDicRes
    for catalog in catalogDic:
        catalogId = None
        if isinstance(catalog, dict):
            # 获取分类url
            catalogUrl.append(str(catalog['second_category_url']))
            # 获取分类名称
            catalogName.append(catalog['category_name'])
            catalogId = re.search(r'\d+$', catalogUrl[-1]).group()
        else:
            catalogUrl.append(catalog)
            catalogName.append('无分类')
            catalogId = re.search(r'\d+', catalogUrl[-1]).group()
        # 获取分类ID
        # print('catalogUrl', catalogUrl)

        # 构造获取作业url
        homeworkUrl = baseUrl + '/courses/' + classId + '/homework_commons.json?id=' + classId
        if isinstance(catalog, dict):
            homeworkUrl += '&type=4&category=' + catalogId

        # print(homeworkUrl)
        # 获取作业名称结果
        fileRes = r.get(homeworkUrl, headers=header).text
        fileDic = (json.loads(fileRes))['homeworks']
        # 作业实训报告的名称
        fileName = []
        # 存储实训报告的id
        fileId = []
        # 存储实训报告的名称
        fileUrl = []
        for i in fileDic:
            fileName.append(i['name'])
            # print(i['name'])
            fileId.append(i['homework_id'])
            # 获取实训报告的用户的id的url
            tempUrl = 'https://www.educoder.net/api/homework_commons/' + str(fileId[-1]) + '/works_list.json'
            # print(tempUrl)
            tempRes = r.get(tempUrl, headers=header).text
            tempId = json.loads(tempRes)['id']
            fileUrl.append(url + '/classrooms/' + str(classId) + "/shixun_homework/" + str(fileId[-1]) + "/"
                           + str(tempId) + "/comment")
        fileUrls.append(fileUrl)
        fileNames.append(fileName)
        # print(fileNames)
    catalogNames.append(catalogName)
    fileUrlss.append(fileUrls)
    fileNamess.append(fileNames)


cook = loginRes.cookies
cookie = {}
browser = webdriver.ChromeOptions()
# browser.add_argument('headless')
browser.add_experimental_option('prefs', {
    "download.default_directory": 'G:\\educoder',
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
})
browser = webdriver.Chrome(options=browser)
coo = browser.get_cookies()
browser.get('https://www.educoder.net')
for k, v in cook.items():
    cookie['name'] = k
    cookie['value'] = v
    browser.add_cookie(cookie)
if not os.path.exists("G:\\scratch"):
    os.mkdir("G:\\scratch")
for i in range(len(classNames)):
    print(classNames[i])
    classNames[i] = re.sub(r'[\\:/*?"<>|]', "_", classNames[i])
    dir1 = 'G:\\scratch\\' + classNames[i]
    if not os.path.exists(dir1):
        os.mkdir(dir1)
    for j in range(len(catalogNames[i])):
        catalogNames[i][j] = re.sub(r'[\\:/*?"<>|]', "_", catalogNames[i][j])
        # print(catalogNames[i][j], ":")
        dir2 = 'G:\\scratch\\' + classNames[i] + "\\" + catalogNames[i][j]
        dir2 = re.sub(r'[/*?"<>|]', "_", dir2)
        if not os.path.exists(dir2):
            os.mkdir(dir2)
        for k in range(len(fileNamess[i][j])):
            pre = os.listdir('G:\\educoder')
            # print("pre", pre)
            browser.get(fileUrlss[i][j][k])
            time.sleep(3)
            browser.find_element_by_css_selector('button').click()
            time.sleep(3)
            now = os.listdir('G:\\educoder')
            # print("now", now)
            new = None
            for m in now:
                if m not in pre:
                    new = m
            # print('m:', new)
            fileNamess[i][j][k] = re.sub(r'[\\:/*?"<>|]', "_", fileNamess[i][j][k])
            # print(fileNamess[i][j][k])
            shutil.move("G:\\educoder\\"+new, dir2 + "\\" + fileNamess[i][j][k] + ".pdf")
