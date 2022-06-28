import datetime
import os
import pymongo
from dateutil.relativedelta import relativedelta
from pymongo.errors import ConnectionFailure
from transliterate import translit
from app.report import create_report



class DB_provider:

    def __init__(self, host, port, db_name, conf):
        self.db = self.connection(host,port,db_name)
        self.config = conf

    def connection(self, host, port, db_name):
        try:
            client = pymongo.MongoClient(host, port)
            client.admin.command('ping')
            db = client[db_name]
            print("[УСПЕХ] Подключено к БД")
            return db
        except ConnectionFailure:
            print("[ОШИБКА] Ошибка подключения к БД")
        os.abort()

    def add_collection(self, name):
        if name not in self.db.list_collection_names():
            self.db.create_collection(name)
        else:
            print(f'Коллекция \'{name}\' уже существует')

    def add_teacher(self, l_n, f_n, m_n, tg_id):
        l_n = l_n.capitalize()
        f_n = f_n.capitalize()
        m_n = m_n.capitalize()
        home_path = f'{l_n}_{f_n}_{m_n}'
        home_path = translit(home_path, 'ru', reversed=True)
        if self.db.teachers.find_one({"home_path":f"\\{home_path}"}):
            return False
        try:
            self.db.teachers.insert_one(
                    {
                        "f_name": f_n,
                        "l_name": l_n,
                        "m_name": m_n,
                        "tg_id": str(tg_id),
                        "pub_key": '',
                        "home_path":f"\\{home_path}",
                        "paths_id_list": [],
                        "uncheck_file": [],
                    }
                )
            return True
        except Exception:
            return False

    def add_pub_key(self, key, user_id, type_user):
        try:
            if self.db.pub_keys.find_one({'key':key}):
                return False
            self.db.pub_keys.update_one({"user_id":user_id,'status': True}, {'$set': {'status': False}})
            _id = self.db.pub_keys.insert_one(
                    {
                        "user_id": user_id,
                        "key": key,
                        "status": True
                    }
                )
            if type_user == 'student':
                self.db.students.update_one({"_id":user_id}, {"$set":{"pub_key":_id.inserted_id}})
            else:
                self.db.teachers.update_one({"_id": user_id}, {"$set": {"pub_key": _id.inserted_id}})
            return True
        except Exception:
            return False

    def add_file_type(self, name,prefix, exp):
        name = name.capitalize()
        prefix = prefix.upper().replace(" ", "")
        prefix = translit(prefix, 'ru', reversed=True)
        if self.db.file_type.find_one({'$or': [{'name': name},{'prefix': prefix}]}):
            return False
        path = name.replace(" ", "_")
        path = translit(path, 'ru', reversed=True)
        try:
            exp = int(exp)
            self.db.file_type.insert_one(
                {
                    "name": name,
                    "path": f"\\{path}",
                    "prefix":prefix,
                    "exp": exp,
                }
            )
            return True
        except Exception:
            return False

    def get_types_doc(self):
        res = self.db.file_type.find({})
        res_ = {}
        for i in res:
            res_.update({f"{i['name']} [{i['exp']} мес][{i['prefix']}]":i})
        return res_

    def update_type(self,id, exp):
        try:
            self.db.file_type.update_one({'_id':id}, {'$set':{'exp':exp}})
            return True
        except Exception:
            return False

    def del_type(self,id):
        try:
            if self.db.files.find_one({'type':id}):
                return False
            self.db.file_type.delete_one({'_id':id})
            return True
        except Exception:
            return False

    def add_voucher(self, code, group_id,type_):
        date = datetime.datetime.today()
        self.db.vouchers.insert_one(
            {
                "code": code,
                "group": group_id,
                "date": date,
                "type": type_
            }
        )

    def check_voucher(self, voucher):
        d_now = datetime.datetime.today()
        date_ = d_now - datetime.timedelta(days=self.config.EXP_VOUCH * 7)
        self.db.vouchers.remove({"date": {"$lt": date_}})
        res = self.db.vouchers.find_one({"code":voucher})
        return res

    def add_user(self, voucher, fio, tg_id):
        fio = [i.capitalize() for i in fio]
        if voucher['type']=='student':
            if self.db.students.find_one({"l_name": fio[0], "f_name": fio[1], "m_name": fio[2], "group_id":voucher['group']}):
                return False
            else:
                self.add_student(*fio,tg_id,voucher['group'])
                self.db.vouchers.delete_one({"_id":voucher['_id']})
                return True
        else:
            if self.db.teachers.find_one({"l_name":fio[0],"f_name":fio[1],"m_name":fio[2]}):
                return False
            else:
                self.add_teacher(*fio,tg_id)
                self.db.vouchers.delete_one({"_id": voucher['_id']})
                return True

    def get_file_path(self, f_id):
        file = self.db.files.find_one({'_id':f_id})
        coll = self.db.paths.find_one({'_id':file['path_id']})
        st = self.db.students.find_one({'_id': file['st_id']})
        gr = self.db.groups.find_one({'_id': st['group_id']})
        type = self.db.file_type.find_one({'_id': file['type']})
        res = coll['path']+gr['path']+st['path']+type['path']
        return res

    def reset_user(self, id):
        self.db.aiogram_state.delete_one({'chat':int(id)})

    def update_teacher(self, id_obj, l_name, f_name, m_name, tg_id):
        l_name = l_name.capitalize()
        f_name = f_name.capitalize()
        m_name = m_name.capitalize()
        try:
            teach = self.db.teachers.find_one({'_id': id_obj})
            if (teach['l_name']==l_name)and(teach['f_name']==f_name)and(teach['m_name']==m_name):
                self.db.teachers.update_one({"_id": id_obj}, {
                    '$set': {"tg_id": tg_id}})
                self.reset_user(teach['tg_id'])
                return True
            if teach['paths_id_list']:
                return False
            home_path = f'{l_name}_{f_name}_{m_name}'
            home_path = translit(home_path, 'ru', reversed=True)
            if self.db.teachers.find_one({'home_path':home_path}):
                return False
            self.db.teachers.update_one({"_id":id_obj}, {'$set':{"f_name": f_name, "l_name": l_name, "m_name": m_name, "tg_id" : tg_id, "home_path": f'\\{home_path}'}})
            return True
        except Exception:
            return False

    def del_teacher(self, id_teach):
        try:
            teach = self.db.teachers.find_one({"_id":id_teach})
            if teach['paths_id_list']:
                return False
            self.db.teachers.delete_one({"_id":id_teach})
            return True
        except Exception:
            return False

    def add_student(self, l_n,f_n, m_n, tg_id, group_id):
        l_n = l_n.capitalize()
        f_n = f_n.capitalize()
        m_n = m_n.capitalize()
        home_path = f'{l_n}_{f_n}_{m_n}'
        home_path = translit(home_path, 'ru', reversed=True)
        gr_st = self.db.groups.find_one({'_id':group_id})
        for i in gr_st['list_students_id']:
            st = self.db.students.find_one({'_id':i})
            if st['path'].lower() == home_path.lower():
                return False
        try:
            id_stud = self.db.students.insert_one(
                    {
                        "f_name": f_n,
                        "l_name": l_n,
                        "m_name": m_n,
                        "tg_id": str(tg_id),
                        "group_id": group_id,
                        "path": '\\'+home_path,
                        "pub_key": '',
                        "file_list": [],
                    }
            )
            self.db.groups.update_one({'_id': group_id}, {'$addToSet': {'list_students_id': id_stud.inserted_id}})
            return True
        except Exception:
            return False

    def add_group(self, name):
        tr_name = translit(name, 'ru', reversed=True)
        tr_name = '_'.join(tr_name.split())
        id_ = self.db.groups.insert_one(
                {
                    "group_name": name,
                    "path":'\\'+tr_name,
                    "list_students_id": [],
                    "access_path": [],
                }
            )
        return id_

    def del_gr_from_coll(self, id_gr, id_coll):
        self.db.paths.update_one({'_id':id_coll},{'$pull':{'group_list_id':id_gr}})
        list_students_id = self.db.groups.find_one_and_update({'_id':id_gr},{'$pull':{'access_path':id_coll}})['list_students_id']
        list_stud_obj = self.db.students.find({"_id": {'$in': list_students_id}})
        for stud in list_stud_obj:
            for file_id in stud['file_list']:
                file_obj = self.db.files.find_one({"_id":file_id})
                if file_obj['path_id'] == id_coll:
                    if file_obj['status'] != 'accepted':
                        if os.path.isfile(self.config.HOME_PATH + f"\\unchecked_files\\{file_obj['_id']}.pdf"):
                            os.remove(self.config.HOME_PATH + f"\\unchecked_files\\{file_obj['_id']}.pdf")
                        self.db.files.delete_one({'_id':file_obj['_id']})
                        self.db.teachers.update_one({'_id': file_obj["tc_id"]}, {'$pull': {'uncheck_file': file_obj["_id"]}})
                    self.db.students.update_one({'_id':stud['_id']},{'$pull':{'file_list':file_id}})
        return True

    def del_group(self, id_gr):
        group = self.db.groups.find_one({'_id': id_gr})
        if not group['access_path']:
            for i in group['list_students_id']:
                self.del_stud(i)
            self.db.groups.delete_one({'_id':id_gr})
            return True
        else:
            return False

    def add_group_to_coll(self, id_gr, id_coll):
        self.db.groups.update_one({'_id':id_gr}, {"$addToSet":{'access_path':id_coll}})
        self.db.paths.update_one({'_id': id_coll}, {'$addToSet': {'group_list_id': id_gr}})

    def add_file(self, path_id, st_id, tc_id, date, type, name):
        try:
            file_id = self.db.files.insert_one(
                {
                    "file_name": name,
                    "path_id": path_id,
                    "date_upload": date,
                    "type": type,
                    "st_id": st_id,
                    "tc_id": tc_id,
                    "status": 'loaded',
                    "comment": ''
                }
            )
            self.db.students.update_one({"_id": st_id},{'$addToSet':{'file_list':file_id.inserted_id}})
            self.db.teachers.update_one({'_id': tc_id}, {'$addToSet': {'uncheck_file': file_id.inserted_id}})
            if not os.path.isdir(self.config.HOME_PATH + '\\unchecked_files'):
                os.makedirs(self.config.HOME_PATH + '\\unchecked_files')
            return file_id.inserted_id
        except Exception as e:
            print(e)
            return False

    def get_list_teacher(self):
        res = self.db.teachers.find({}).sort('l_name')
        teacher_list = {}
        for i in res:
            teacher_list.update({f"{i['l_name']} {i['f_name']} {i['m_name']}": i})
        return teacher_list

    def get_stud_list_adm(self, list_stud_id):
        res = {}
        for i in list_stud_id:
            st = self.db.students.find_one({'_id':i})
            res.update({f'{st["l_name"]} {st["f_name"]} {st["m_name"]}':st})
        return res

    def get_stud_list(self,gr_id):
        stud_list = self.db.groups.find_one({'_id':gr_id})
        res = {}
        for i in stud_list['list_students_id']:
            stud = self.db.students.find_one({'_id': i})
            res.update({f'{stud["l_name"]} {stud["f_name"]} {stud["m_name"]}': stud})
        return res

    def get_teacher_id(self, tg_id):
        res = self.db.teachers.find_one({'tg_id':str(tg_id)})
        if res:
            return res['_id']
        else:
            return False

    def get_student_id(self, tg_id):
        res = self.db.students.find_one({'tg_id':str(tg_id)})
        if res:
            return res['_id']
        else:
            return False

    def get_student(self, obj_id):
        res = self.db.students.find_one({'_id':obj_id})
        return res

    def get_teach_info(self, obj_id):
        res = self.db.teachers.find_one({'_id':obj_id})
        return res

    def get_name_group_id(self, obj_id):
        res = self.db.groups.find_one({'tg_id': obj_id})
        return res['group_name']

    def get_group_list_adm(self):
        group_list = self.db.groups.find({})
        res_ = {}
        for i in group_list:
            res_.update({i['group_name']: i})
        return res_

    def start_clear(self):
        types_ = self.db.file_type.find({})
        types = {}
        for i in types_:
            types.update({str(i['_id']):i['exp']})
        now = datetime.datetime.now()
        list_ = []
        for i in self.db.files.find({}):
            if i['date_upload'] + relativedelta(months=types[str(i['type'])]) < now:
                self.db.unsent_files.insert_one({'operation': 'DEL', 'path':i['path']+f"\\{i['file_name']}"})
                if i['status'] == 'loaded':
                    self.db.teachers.update_one({'_id':i['tc_id']}, {'$pull': {'uncheck_file':i['_id']}})
                self.db.students.update_one({'_id': i['st_id']}, {'$pull': {'file_list': i['_id']}})
                # try:
                if os.path.isfile(self.config.HOME_PATH + i['path'] + f"\\{i['file_name']}"):
                    os.remove(self.config.HOME_PATH + i['path'] + f"\\{i['file_name']}")
                path = i['path']
                while True:
                    if len(os.listdir(self.config.HOME_PATH + path)) == 0:
                        self.db.unsent_files.insert_one({'operation': 'DEL', 'path':path})
                        if os.path.isdir(self.config.HOME_PATH + path):
                            os.rmdir(self.config.HOME_PATH + path)
                        path = path[:path.rfind('\\')]
                        if path == '':
                            break
                    else:
                        break
                # except Exception:
                #     pass
                list_.append(i['_id'])
        self.db.files.delete_many({'_id':{'$in':list_}})
        return list_


    def get_group_list(self, path_id):
        group_list = self.db.paths.find_one({'_id':path_id})
        res_ = {}
        for i in group_list['group_list_id']:
            group = self.db.groups.find_one({'_id':i})
            res_.update({group['group_name']:group})
        return res_

    def get_files(self, id_stud,coll_id):
        try:
            list_files = self.db.students.find_one({'_id':id_stud})
            list_files = list_files['file_list']
            types = self.db.file_type.find({},{'name':1})
            types_ = {}
            for i in types:
                types_.update({i['_id']:i['name']})
            res = {i:{} for i in types_.values()}
            for i in list_files:
                emoj = ''
                file = self.db.files.find_one({'_id':i})
                if file['path_id']==coll_id:
                    if file['status'] == 'accepted':
                        emoj = '✅ '
                    elif file['status'] == 'loaded':
                        emoj = '⏳ '
                    else:
                        emoj = '🛠️️ '
                    res[types_[file['type']]].update({emoj+file['file_name']:file})
            for i in list(res.keys()):
                if res[i] == {}:
                    res.pop(i)
            return res
        except Exception:
            return []

    def get_files_teach(self, id_stud, id_coll):
        list_files = self.db.students.find_one({'_id': id_stud})['file_list']
        types = self.db.file_type.find({}, {'name': 1})
        types_ = {}
        for i in types:
            types_.update({i['_id']: i['name']})
        res = {i: {} for i in types_.values()}
        for i in list_files:
            emoj = ''
            file = self.db.files.find_one({'_id': i})
            if file['path_id']== id_coll:
                if file['status'] == 'accepted':
                    emoj = '✅ '
                elif file['status'] == 'loaded':
                    emoj = '⏳ '
                else:
                    emoj = '❌ '
                res[types_[file['type']]].update({emoj + file['file_name']: file})
        for i in list(res.keys()):
            if res[i] == {}:
                res.pop(i)
        return res

    def get_coll_stud(self, stud_id):
        group = self.db.students.find_one({'_id':stud_id})
        group = group['group_id']
        list_coll = self.db.groups.find_one({'_id':group})
        res = {}
        for i in list_coll['access_path']:
            path = self.db.paths.find_one({'_id':i})
            owner = self.db.teachers.find_one({'_id':path['owner_id']})
            path['owner_id'] = owner
            res.update({f'{path["name"]} [{owner["l_name"]+owner["f_name"][:1]+owner["m_name"][:1]}]':path})
        return res

    def get_types(self):
        res_ = self.db.file_type.find({})
        res = {}
        for i in res_:
            res.update({i['name']:i})
        return res

    def get_stud_info(self, st_id):
        res = self.db.students.find_one({'_id': st_id})
        return res

    def update_stud(self,obj_id, l_name, f_name, m_name, tg_id):
        l_name = l_name.capitalize()
        f_name = f_name.capitalize()
        m_name = m_name.capitalize()
        try:
            stud = self.db.students.find_one({'_id': obj_id})
            if (stud['l_name']==l_name)and(stud['f_name']==f_name)and(stud['m_name']==m_name):
                self.db.teachers.update_one({"_id": obj_id}, {
                    '$set': {"tg_id": tg_id}})
                self.reset_user(stud['tg_id'])
                return True
            for i in stud['file_list']:
                file = self.db.students.find_one({'_id': i})
                if file['status']=='accepted':
                    return False
            home_path = f'{l_name}_{f_name}_{m_name}'
            home_path = translit(home_path, 'ru', reversed=True)
            self.db.students.update_one({'_id': obj_id}, {
                '$set': {'l_name': l_name, 'f_name': f_name, 'm_name': m_name, 'tg_id': tg_id, 'path': home_path}})
            return True
        except Exception:
            return False

    def get_report(self, id_tc):
        tree = {}
        tc = self.db.teachers.find_one({'_id': id_tc})
        list_obj_coll = self.db.paths.find({"_id":{"$in":tc['paths_id_list']}})
        list_obj_coll_ = {}
        groups_list = []
        for i in list_obj_coll:
            list_obj_coll_.update({str(i['_id']): i})
            tree.update({str(i['_id']): {}})
            for j in i['group_list_id']:
                tree[str(i['_id'])].update({str(j):[]})
                if j not in groups_list:
                    groups_list.append(j)
        groups_obj = self.db.groups.find({"_id":{"$in":groups_list}})
        stud_list = []
        groups_obj_ = {}
        for i in groups_obj:
            groups_obj_.update({str(i['_id']): i})
            for j in i['list_students_id']:
                if j not in stud_list:
                    stud_list.append(j)
        stud_obj = self.db.students.find({"_id":{"$in":stud_list}})

        stud_obj_ = {}
        for i in stud_obj:
            stud_obj_.update({str(i['_id']):i})

        for coll in list(tree.keys()):
            for group in list(tree[coll].keys()):
                tree[coll][group].append('ALL')
                for stud in groups_obj_[group]['list_students_id']:
                    tree[coll][group].append(f'{stud_obj_[str(stud)]["l_name"]} {stud_obj_[str(stud)]["f_name"]} {stud_obj_[str(stud)]["m_name"]}')
                tree[coll].update({groups_obj_[group]['group_name']: tree[coll].pop(group)})
            tree.update({list_obj_coll_[coll]['name']: tree.pop(coll)})

        res = []
        file_list = self.db.files.find({'path_id': {'$in':tc['paths_id_list']}})
        types_f = self.db.file_type.find({})
        types_ = {}
        for i in types_f:
            types_.update({str(i['_id']):i})


        for i in file_list:
            res.append([f'{stud_obj_[str(i["st_id"])]["l_name"]} {stud_obj_[str(i["st_id"])]["f_name"]} {stud_obj_[str(i["st_id"])]["m_name"]}',
                        i["file_name"],
                        groups_obj_[str(stud_obj_[str(i["st_id"])]['group_id'])]['group_name'],
                        types_[str(i["type"])]['name'],
                        i['status'].replace('accepted', 'Принят').replace('modification', 'На доработке').replace('loaded', 'Ожидает проверки'),
                        list_obj_coll_[str(i["path_id"])]['name'],
                        i["date_upload"].strftime("%d.%m.%Y"),
                        i["comment"]
                        ])
        try:
            return create_report(res,tree,str(id_tc))
        except Exception as e:
            print(e)
            return False

    def get_group_in_coll(self, list_id):
        res = {}
        for i in list_id:
            group = self.db.groups.find_one({'_id':i})
            res.update({group['group_name']:group})
        return res

    def del_stud(self, stud_id):
        stud = self.db.students.find_one({'_id':stud_id})
        group_id = stud['group_id']
        file_list = self.db.files.find({'_id':{"$in":stud['file_list']}})
        for i in file_list:
            if i['status'] != 'accepted':
                if i['status'] == 'loaded':
                    self.db.teachers.update_one({'_id':i['tc_id']},{'$pull':{'uncheck_file':i['_id']}})
                if os.path.isfile(self.config.HOME_PATH + f"\\unchecked_files\\{i['_id']}.pdf"):
                    os.remove(self.config.HOME_PATH + f"\\unchecked_files\\{i['_id']}.pdf")
                self.db.files.delete_one({'_id': i['_id']})
        self.reset_user(stud['tg_id'])
        self.db.pub_keys.delete_many({'user_id':stud_id})
        self.db.groups.update_one({'_id':group_id},{'$pull':{'list_students_id':stud_id}})
        self.db.students.delete_one({'_id':stud_id})

    def remove_all(self):
        # self.db.teachers.delete_many({})
        self.db.paths.delete_many({})
        self.db.files.delete_many({})
        self.db.paths.update_many({},{'$set':{'file_list_id':[]}})
        # self.db.students.delete_many({})
        # self.db.groups.delete_many({})

    def check_free_group_name(self, group_name):
        if self.db.groups.find_one({'group_name':group_name}):
            return False
        else:
            return True

    def update_file(self, id_f, date_, date_t):
        try:
            file = self.db.files.find_one({'_id':id_f})
            if file['status'] != 'accepted':
                old_name = file['file_name']
                new_name = old_name[:old_name.rfind("_")+1]+date_+'.pdf'
                self.db.files.update_one({'_id':id_f},{'$set':{'date_upload':date_t,'file_name':new_name, 'status':'loaded'}})
                self.db.teachers.update_one({'_id':file['tc_id']},{'$addToSet':{'uncheck_file':id_f}})
                return True
            return False
        except Exception:
            return False

    def get_coll_teach(self, tc_id):
        res = self.db.teachers.find_one({'_id':tc_id})
        res_ = {}
        for i in res['paths_id_list']:
            coll = self.db.paths.find_one({'_id':i})
            res_.update({coll['name']:coll})
        return res_

    def get_uncheck_files_teach(self, tc_id):
        res = self.db.teachers.find_one({'_id':tc_id})
        res_ = {}
        if res:
            for i in res['uncheck_file']:
                file = self.db.files.find_one({'_id':i})
                path_ = self.db.paths.find_one({'_id':file['path_id']})
                if path_['name'] not in res_.keys():
                    res_.update({path_['name']:{}})
                stud_ = self.db.students.find_one({'_id':file['st_id']})
                group_ = self.db.groups.find_one({'_id':stud_['group_id']})
                if group_['group_name'] not in res_[path_['name']].keys():
                    res_[path_['name']].update({group_['group_name']: {}})

                if f"{stud_['l_name']} {stud_['f_name']} {stud_['m_name']}" not in res_[path_['name']][group_['group_name']].keys():
                    res_[path_['name']][group_['group_name']].update({f"{stud_['l_name']} {stud_['f_name']} {stud_['m_name']}": {}})

                type_ = self.db.file_type.find_one({'_id':file['type']})
                if type_['name'] not in res_[path_['name']][group_['group_name']][f"{stud_['l_name']} {stud_['f_name']} {stud_['m_name']}"].keys():
                    res_[path_['name']][group_['group_name']][f"{stud_['l_name']} {stud_['f_name']} {stud_['m_name']}"].update({type_['name']:{}})
                res_[path_['name']][group_['group_name']][f"{stud_['l_name']} {stud_['f_name']} {stud_['m_name']}"][type_['name']].update({file['file_name']:file})
            return res_
        else:
            return False

    def get_path_by_id(self, path_id):
        res = self.db.paths.find_one({'_id':path_id})
        return res

    def del_file_by_id(self, id_file):
        file = self.db.files.find_one({'_id':id_file})
        if file['status']!='accepted':
            if os.path.isfile(self.config.HOME_PATH + f"\\unchecked_files\\{file['_id']}.pdf"):
                os.remove(self.config.HOME_PATH + f"\\unchecked_files\\{file['_id']}.pdf")
            self.db.students.update_one({'_id':file["st_id"]},{'$pull':{'file_list':id_file}})
            self.db.teachers.update_one({'_id': file["tc_id"]}, {'$pull': {'uncheck_file': id_file}})
            self.db.files.delete_one({'_id':id_file})
            return True
        else:
            return False

    def del_coll(self, path_id, tc_id):
        coll = self.db.paths.find_one({'_id':path_id})
        if coll['group_list_id']:
            return False
        self.db.teachers.update_one({'_id': tc_id}, {'$pull': {'paths_id_list': path_id}})
        self.db.paths.delete_one({'_id': path_id})
        return True

    def add_coll(self, name, nickname, tc_id):
            name = name.capitalize()
            nickname = nickname.replace(" ","").upper()
            nickname = translit(nickname, 'ru', reversed=True)
            res = self.db.teachers.find_one({'_id':tc_id})
            if res['paths_id_list'] != {}:
                for i in res['paths_id_list']:
                    path = self.db.paths.find_one({'_id':i})
                    if (name == path['name']) or (nickname == path['nickname']):
                        return False
            tr_name = translit(name, 'ru', reversed=True)
            tr_name = '_'.join(tr_name.split())
            id_ = self.db.paths.insert_one(
                {
                    "name": name,
                    "nickname":nickname,
                    "owner_id": tc_id,
                    "path": f'\\{tr_name}',
                    "group_list_id": [],
                }
            )
            self.db.teachers.update_one({'_id': tc_id}, {'$addToSet': {'paths_id_list': id_.inserted_id}})
            return True

    def get_path_list(self, tc_id):
        coll_list = {}
        res = self.db.teachers.find_one({'_id':tc_id})
        for i in res['paths_id_list']:
            path = self.db.paths.find_one({'_id':i})
            coll_list.update({path['name']: path})
        return coll_list

    def check_new_file(self, path_id):
        path = self.db.paths.find_one({'_id':path_id})
        for i in path['file_list_id']:
            file = self.db.files.find_one({'_id':i})
            if (file['upload']==True) and (file['check']==False):
                return True
        return False

    def change_stud_key(self, obj_id, new_key):
        self.db.students.update_one({'_id':obj_id},{'$addToSet':{'pub_key':new_key}})

    def change_teach_key(self, obj_id, new_key):
        self.db.teachers.update_one({'_id':obj_id},{'$addToSet':{'pub_key':new_key}})

    def get_key(self, user_id):
        res = self.db.pub_keys.find_one({'user_id': user_id, 'status':True})
        if res:
            res = res['key']
        else:
            res = False
        return res

    def check_free_file_name(self, name, list_file):
        pos_ = name.find("_")
        str_ = name[:pos_]
        for i in list_file.keys():
            name_file = list_file[i]['file_name']
            pos__ = name_file.find("_")
            if str_ == name_file[:pos__]:
                return False
        return True


