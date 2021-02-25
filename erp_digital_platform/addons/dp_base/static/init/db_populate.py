# -*- coding: utf-8 -*-
import xlsxwriter as xw
import numpy as np
import time, sys, os
from datetime import datetime as dt
import psycopg2
import pandas as pd
import math
import numpy as np
import unicodedata
start_time = time.time()

f = '/home/chinsheng/local_erp/digital_platform/digital_platform/addons/dp_base/static/init/np_database_tables.xlsx'
conn = psycopg2.connect(host="localhost",
                        dbname="dp_uat_godie",
                        user="chinsheng",
                        password="PPT3c|-|@12345")

# f = '/home/cs/workspace-pycharm/odoo_venv/src/custom_api/admin/np_database_tables.xlsx'
# conn = psycopg2.connect(host="localhost",
#                         dbname="np_customs",
#                         user="postgres",
#                         password="PPT3c|-|@12345")


# create a cursor
cur = conn.cursor()

def update_res_country():
    country = pd.read_excel(f, 'res_country')
    sql = """select id, code, name from res_country order by id"""
    cur.execute(sql)
    rescountry = cur.fetchall()
    n = 'no'
    cdb = 'code_db'
    ndb = 'name_db'
    dbxl = 'db_vs_excel'
    cxl = 'code_xl'
    nxl = 'name_xl'

    counter = 0
    for i in range(len(country)):
        if country[ndb][i]=='Namibia':
            sql = """update res_country set name = '{setname}' where code = '{code}' and name = '{name}'""".format(
                setname=country[nxl][i] if "'" not in country[nxl][i] else country[nxl][i].replace("'", "''"),
                code='NA',
                name=country[ndb][i] if "'" not in country[ndb][i] else country[ndb][i].replace("'", "''"),
            )
            cur.execute(sql)
            conn.commit()
            counter+=1
            # print(country[nxl][i], country[ndb][i])

        elif country[dbxl][i]:
            sql = """update res_country set name = '{setname}' where code = '{code}' and name = '{name}'""".format(
                setname=country[nxl][i] if "'" not in country[nxl][i] else country[nxl][i].replace("'", "''"),
                code=country[cdb][i],
                name=country[ndb][i] if "'" not in country[ndb][i] else country[ndb][i].replace("'", "''"),
            )
            cur.execute(sql)
            conn.commit()

            # print(country[nxl][i], country[cdb][i], country[ndb][i])
            counter += 1
        else:
            # counter += 1
            if isinstance(country[cxl][i], float) and isinstance(country[nxl][i], float):
                if math.isnan(country[cxl][i]) and math.isnan(country[nxl][i]):
                    try:
                        sql = """update res_country set name = '{setname}' where code = '{code}' and name = '{name}'""".format(
                            setname=country[ndb][i].upper() if "'" not in country[ndb][i].upper() else country[ndb][i].upper().replace("'", "''"),
                            code=country[cdb][i],
                            name=country[ndb][i] if "'" not in country[ndb][i] else country[ndb][i].replace("'", "''"),
                        )
                        cur.execute(sql)
                        conn.commit()
                    except:
                        pass
                    counter += 1




                    # print(country[cdb][i], country[ndb][i], country[ndb][i].upper())
                    # print(country[cdb][i], unicodedata.normalize('NFKD', country[ndb][i]).encode('ascii', 'ignore'), unicodedata.normalize('NFKD', country[ndb][i].upper()).encode('ascii', 'ignore'))
                    # print(country[cxl][i], country[nxl][i])
                    # print('\n')
            elif isinstance(country[cdb][i], float) and isinstance(country[ndb][i], float):
                if math.isnan(country[cdb][i]) and math.isnan(country[ndb][i]):
                    sql = """insert into res_country (code, name, create_uid, create_date, write_uid, write_date) values ('{code}', '{name}', {create_uid}, '{create_date}', {write_uid}, '{write_date}')""".format(
                        code=country[cxl][i],
                        name=country[nxl][i] if "'" not in country[nxl][i] else country[nxl][i].replace("'", "''"),
                        create_uid=1,
                        create_date=dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                        write_uid=1,
                        write_date=dt.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    cur.execute(sql)
                    conn.commit()
                    counter += 1

                    # print(country[cdb][i], country[ndb][i])
                    # print(country[cxl][i], country[nxl][i])
                    # print('\n')

            # print(country[n][i], country[cdb][i], country[ndb][i], country[dbxl][i], country[cxl][i], country[nxl][i])
    print('\n\ncounter is at %d' %counter)
    print('counter value is equal to 255 (total no of entries): %s' %(str(counter==255)))

def update_res_country_set_inactive():
    # default set to not active
    sql = """update res_country set active = False"""
    cur.execute(sql)
    conn.commit()
    # set all customs country to active = True
    sql = """update res_country set active = True where code not in ('AQ', 'AX', 'BL', 'BQ', 'CW', 'GS', 'MF', 'NT', 'PS', 'SS', 'SX', 'TP', 'YU', 'ZR')"""
    cur.execute(sql)
    conn.commit()

def insert_into_custom_port():
    port = pd.read_excel(f, 'port')
    sql = """select id, code, name from res_country"""
    cur.execute(sql)
    cty_data = cur.fetchall()
    prev_cty_code = prev_cty_id = None
    for row in range(len(port)):
        code = port['Code'][row]
        desc = port['Description'][row]
        if "'" in code:
            code = code.replace("'", "''")
        if "'" in desc:
            desc = desc.replace("'", "''")
        port_reference_num = port['PortReferenceId'][row]
        country_reference_num = port['CountryReferenceId'][row]
        country_name = port['Country Description'][row]

        if country_name != 'NAMIBIA':
            country_code = port['Country Code'][row]
        else:
            country_code = 'NA'

        if prev_cty_code != country_code:
            if any(cty[1] == country_code for cty in cty_data):
                for cty in cty_data:
                    if cty[1] == country_code:
                        country_id = cty[0]
            else:
                country_id = None
        else:
            country_id = prev_cty_id


        try:
            if country_id is not None:
                sql = """INSERT INTO custom_port (country_id, country_code, country_reference_num, port_reference_num, create_uid, code, create_date, name, write_uid, write_date) VALUES ({country_id}, '{country_code}', '{country_reference_num}', '{port_reference_num}', {create_uid}, '{code}', '{create_date}', '{name}', {write_uid}, '{write_date}')""" \
                        .format(
                                country_id=country_id,
                                country_code=country_code,
                                country_reference_num=country_reference_num,
                                port_reference_num=port_reference_num,
                                create_uid=1,
                                code=code,
                                create_date=dt.now().strftime('%Y-%m-%d %H:%M:%S'),
                                name=desc,
                                write_uid=1,
                                write_date=dt.now().strftime('%Y-%m-%d %H:%M:%S'))
                cur.execute(sql)
                conn.commit()
            else:
                raise Exception
        except Exception as e:
            print(e)
            print(sql)
            print(code)
            print(desc)
            print(port_reference_num)
            print(country_reference_num)
            print(country_code)
            print(country_id)
            print('\n\n\n\n\n')

        prev_cty_code = country_code
        prev_cty_id = country_id

if __name__ == '__main__':

    # run next 2 lines for new db, if reinstall module do not run
    print('\nupdate res country start')
    update_res_country()
    print('update res country complete')

    print('\nupdate res country set inactive start')
    update_res_country_set_inactive()
    print('update res country set inactive complete')

    print('\ninsert into custom_port start')
    insert_into_custom_port()
    print('insert into custom_port complete')
    print("-------------------- Completed in {seconds}sec --------------------".format(seconds=round(time.time() - start_time, 4)))
