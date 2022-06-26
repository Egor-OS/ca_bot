from datetime import datetime

import pandas as pd
import datapane as dp

NO_DATA = html = """
<html>
    <style type='text/css'>
        @keyframes example {
            0%   {color: #EEE;}
            25%  {color: #EC4899;}
            50%  {color: #8B5CF6;}
            100% {color: #EF4444;}
        }
        #container {
            background: #4e46e524;
            padding: 10em;
        }
        h1 {
            position: absolute;
            top: 50%;
            left: 50%;
            margin-right: -50%;
            transform: translate(-50%, -50%);
            color:#eee;
            animation-name: example;
            animation-duration: 4s;
            animation-iteration-count: infinite;
        }
    </style>
    <div id="container">
      <h1> Пусто </h1>
    </div>
</html>
"""


def create_report(data, tree, name):
    date = datetime.now().strftime("%d.%m.%Y")
    name = f'report_{date}_{name[::-3]}.html'
    df = pd.DataFrame(data, columns=['ФИО',"Файл",'Группа','Тип','Статус','Дисциплина','Дата','Коментарий'])
    select_obj_0 = []
    for coll in tree.keys():
        select_obj_1 = []
        df_1 = df[df['Дисциплина']==coll]
        for group in tree[coll].keys():
            select_obj_2 = []
            df_2 = df_1[df_1['Группа'] == group]
            for stud in tree[coll][group]:
                if stud != 'ALL':
                    df_3 = df_2[df_2['ФИО']==stud]
                else:
                    df_3 = df_2
                if not df_3.empty:
                    select_obj_2.append(dp.DataTable(df_3, label=stud))
                else:
                    select_obj_2.append(dp.HTML(NO_DATA,label=stud))
            select_obj_1.append(dp.Select(blocks=select_obj_2, label=group))
        if len(tree.keys())>1:
            if len(select_obj_1) > 1:
                select_obj_0.append(dp.Page(blocks=[dp.Select(blocks=select_obj_1)], title=coll))
            else:
                select_obj_0.append(dp.Page(blocks=[f"# {group}", *select_obj_1], title=coll))
        else:
            select_obj_0.append(f'# {coll}')
            if len(select_obj_1) > 1:
                select_obj_0.append(dp.Select(blocks=select_obj_1))
            else:
                select_obj_0.append(f"# {group}")
                select_obj_0.append(select_obj_1[0])
    report = dp.Report(
            *select_obj_0
    )

    report.save(name)
    return name

