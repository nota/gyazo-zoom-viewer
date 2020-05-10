#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import requests
import datetime

def getGyazoImagesData(fetch, access_token, write_to_file=True, page_limit=None, progress_callback=None):
    print(fetch)
    pages = []
    if fetch:
        # Gyazo APIからデータを取得し data/ に保存する
        page = 0
        while True:
            page += 1
            api_path = "https://api.gyazo.com/api/images?per_page=100&page=%s" % page
            print(api_path)
            gyazo_res = requests.get(api_path, headers={"Authorization": "Bearer %s" % access_token})
            # 2xx以外だったら止める
            print(gyazo_res.status_code)
            if gyazo_res.status_code != requests.codes.ok:
                break
            # 最後尾に到達したら "[]" になるので止める
            if len(gyazo_res.text) == 2:
                break
            if write_to_file == True:
                file_path = "data/gyazo_data_%s.json" % page
                if not os.path.isfile(file_path):
                    with open(file_path, mode='x', encoding='utf-8'):
                        pass
                with open(file_path, mode='w', encoding='utf-8') as f:
                    f.write(gyazo_res.text)
            else:
                pages.append(gyazo_res.text)
            if page_limit and page >= page_limit:
                break
            if progress_callback:
                progress_callback(page)

    gyazo_viewer_data_all = []
    if write_to_file:
        page = 0
        while True:
            page += 1
            file_path = "data/gyazo_data_%s.json" % page
            if os.path.isfile(file_path):
                with open(file_path, encoding='utf-8') as f:
                    gyazo_viewer_data_all.extend(convertPage(json.loads(f.read())))
            else:
                break
        file_path = "index_files/gyazodata.js"
        with open(file_path, mode='w', encoding='utf-8') as f:
            f.write("var data = "+json.dumps(gyazo_viewer_data_all, indent=2, ensure_ascii=False)+";")
    else:
        for page in pages:
            gyazo_viewer_data_all.extend(convertPage(json.loads(page)))
        return "var data = " + json.dumps(gyazo_viewer_data_all, indent=2, ensure_ascii=False) + ";"

# data/ 内のJSONをすべて結合する
# From:
#   {
#     "image_id":"xxxx",
#     "permalink_url":"https://api.gyazo.com/xxxx",
#     "url":"https://i.gyazo.com/f4f4dfad8180f955fe6e0bbfbd1ff49c.gif",
#     "metadata":
#       {
#         "app":"Google Chrome",
#         "title":"title of example.com",
#         "url":"https://example.com",
#         "desc":""
#       },
#     "type":"gif",
#     "thumb_url":"https://thumb.gyazo.com/thumb/200/xxxxx.xxxxx.xxxxx-gif.gif",
#     "created_at":"2020-04-02T01:51:43+0000"
#   }
# To:
#   {
#     "str": "20200328193707",
#     "id": "xxxxx",
#     "url": "https://thumb.gyazo.com/thumb/200/xxxxx.xxxxx.xxxxx-jpg.jpg",
#     "keywords": null,
#     "description": "title, description",
#     "comment": "ocr"
#   }
def convertPage(images):
    gyazo_viewer_data = []
    for image in images:
        id_str = image["image_id"]
        created_at = datetime.datetime.strptime(image["created_at"], "%Y-%m-%dT%H:%M:%S%z")
        description = ""
        if "metadata" in image and "app" in image["metadata"] and image["metadata"]["app"] is not None:
            description += " "
            description += image["metadata"]["app"]
        if "metadata" in image and "title" in image["metadata"] and image["metadata"]["title"] is not None:
            description += " "
            description += image["metadata"]["title"]
        if "metadata" in image and "url" in image["metadata"] and image["metadata"]["url"] is not None:
            description += " "
            description += image["metadata"]["url"]
        if "metadata" in image and "desc" in image["metadata"] and image["metadata"]["desc"] is not None:
            description += " "
            description += image["metadata"]["desc"]
        comment = ""
        if "ocr" in image and image["ocr"] is not None:
            description += " "
            description += image["ocr"]["description"]
            comment = image["ocr"]["description"]
        data = {
            "id": id_str,
            "str": created_at.strftime("%Y%m%d%H%M%S"),
            "gyazourl": image["thumb_url"],
            "keywords": "",
            "description": description,
            "comment": comment,
            "usercomment": image["metadata"]["desc"]
        }
        gyazo_viewer_data.extend([data])
    return gyazo_viewer_data

import sys
if __name__ == "__main__":
    if (len(sys.argv) == 1):
        print("python main.py fetch=[true/false]")
    getGyazoImagesData(
        fetch=((len(sys.argv) >= 2) and (sys.argv[1] == "fetch=true")),
        access_token=os.environ.get('gyazo_access_token')
    )
