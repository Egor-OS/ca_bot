import json
import os.path

import cloud_mail_api

class CloudMail:

    def __init__(self,db,email,password, conf):
        self.db_prov = db
        self.connection(email,password)
        self.config = conf
        self.start_upload()

    def connection(self,email,password):
        self.CM = cloud_mail_api.CloudMail(email,password)
        if not os.path.isfile('app/cookies.json'):
            with open('app/cookies.json', 'w') as file:
                json.dump({}, file)
        self.CM.load_cookies_from_file("app/cookies.json")
        if self.CM.auth():
            self.CM.save_cookies_to_file("app/cookies.json")


    def add_file(self, home_path, cloud_path):
        res = self.CM.api.file.add(home_path.replace('\\', '/'), cloud_path.replace('\\', '/'))
        if res['status'] != 200:
            return False
        else:
            return True

    # def del_path(self, path):
    #     path = path.replace('\\','/')
    #     tree = self.CM.api.folder(path)
    #     print(tree)
    #     # if (tree['body']['count']['files'] == 0) and (tree['body']['count']['folders'] == 0):
    #     #     self.CM.api.file.remove(path)
    #     # else:
    #     #     print('Дирректория не пуста')
    #     print(self.CM.api.file.remove(path))

    def del_file(self):
        list_del = self.db_prov.db.unsent_files.find({'operation': 'DEL'})
        for i in list_del:
            path = self.config.PATH_CLOUD + i['path'].replace('\\', '/')
            if self.CM.api.file.remove(path)['status'] == 200:
                self.db_prov.db.unsent_files.delete_one({'_id': i["_id"]})


    def start_upload(self):
            list_files_add = self.db_prov.db.unsent_files.find({'operation':'ADD'})
            for i in list_files_add:
                file_path = self.db_prov.db.files.find_one({'_id':i["_id"]})
                if self.add_file(self.config.HOME_PATH + file_path['path'] + f'\\{file_path["file_name"]}',
                                 self.config.PATH_CLOUD + file_path['path'] + f'\\{file_path["file_name"]}'):
                    self.db_prov.db.unsent_files.delete_one({'_id':i["_id"]})






