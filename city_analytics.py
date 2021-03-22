# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 17:25:41 2021

@author: lint_kid
"""

import requests
import datetime
import statistics 
# import xlsxwriter
import pandas
import json
import numpy as np
import calendar 
from dateutil.rrule import rrule, MONTHLY
import arrow

def hnt_mined_past_days(hotspot_addr,past_days):
    #example :# print(hnt_mined_past_days("116y7S1xPcYoybvP8pgVNjfQVCQNN9QkhiWUnSB9kfgbGcczJBa",30))
    now_object = datetime.datetime.now()
    now_iso_8601 = now_object.isoformat()
    
    thirty_days_ago = now_object - datetime.timedelta(days=past_days)
    thirty_days_ago_iso_8601 = thirty_days_ago.isoformat()
    
    request_string = "https://api.helium.io/v1/hotspots/" + \
    hotspot_addr + "/rewards/sum?min_time=" + thirty_days_ago_iso_8601 + \
    "&max_time=" + now_iso_8601
    
    # print(request_string)
    
    response = requests.get(request_string)
    # print(response.json())
    
    return response.json()['data']['total']

def hnt_mined_timespan(hotspot_addr,start_time,end_time):
    try:
        request_string = "https://api.helium.io/v1/hotspots/" + \
        hotspot_addr + "/rewards/sum?min_time=" + start_time + \
        "&max_time=" + end_time
        print('API income request success')
        response = requests.get(request_string)
        return response.json()['data']['total']
    except:
        print('API failed on income request')
        return np.NAN
    
    # print(request_string)
    
    
    # print(response.json())
    
    

def get_hotspot_addrs_in_city(city_addr):
    #example print(len(get_hotspot_addrs_in_city('c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM')))
    # of hotspots in San Diego
    
    request_string = "https://api.helium.io/v1/cities/" + \
    city_addr + "/hotspots"
    
    # print(request_string)
    hotspot_addr_list = []
    response = requests.get(request_string)
    # print(response.json())
    for i in range(len(response.json()['data'])):
        
        hotspot_addr_list.append(response.json()['data'][i]['address'])
        
    return hotspot_addr_list
    # response.json()['data']['total']
    
    # return response.json()['data']['total']

    
    
def get_list_of_hnt_income(hotspot_addr_list):
    hnt_income_list = []
    for i in range(len(hotspot_addr_list)):
        print('now trying ' + hotspot_addr_list[i])
        hnt_income_list.append(hnt_mined_past_days(hotspot_addr_list[i],30))
    
    return hnt_income_list

def update_income_spreedsheet(hnt_income_list,city_name):
    # df_new = pandas.DataFrame({'San Diego':SD})
    try:
        df_income = pandas.read_excel('city_income.xls')
        #if spreadsheet column length we just opened is greater than the length of our latest income list, we must pad new list with NaNs
        temp_new_df = pandas.DataFrame({city_name:hnt_income_list})
        if df_income.shape[0] > temp_new_df.shape[0]:
            temp_new_df = temp_new_df.reindex(range(df_income.shape[0]))
        elif df_income.shape[0] < temp_new_df.shape[0]: #otherwise we pad old list with NaNs
            df_income = df_income.reindex(range(temp_new_df.shape[0]))
        df_income[city_name] = temp_new_df
    except:
        print('except occured')
        df_income = pandas.DataFrame({city_name:hnt_income_list})
    
    df_income.to_excel('city_income.xls',index=False)

    
def city_search(list_of_city_name_strings):
    # city_string_dict = {'San Diego':'c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM'}
    city_string_dict = {}
    for i in range(len(list_of_city_name_strings)):
        try:
            request_string = "https://api.helium.io/v1/cities?search=" + list_of_city_name_strings[i]
            response = requests.get(request_string)
            city_id = response.json()['data'][0]['city_id']
            # print(city_id)
            city_string_dict[list_of_city_name_strings[i]] = city_id
            
        except:
            print('search failed, try different spelling')
            
    df = pandas.DataFrame(city_string_dict,index=[0])
    df.to_excel('city_keys.xls')
    return city_string_dict


def save_city_json(city_name_addr_dict):
    
    # city_hotspot_dict = {}
    try:
        with open('city_json.json') as json_file:
            old_json = json.load(json_file)
    except:
        old_json = {}

    for city_name in city_name_addr_dict.keys():
        print('now trying ' + str(city_name))
    # city_name_dict = {'San Diego':'c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM'}
        # request_string = "https://api.helium.io/v1/cities/c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM/hotspots"
        if city_name in old_json.keys():
            continue
        else:
            city_addr = city_name_addr_dict[city_name]
            request_string = "https://api.helium.io/v1/cities/" + \
            city_addr + "/hotspots"
            response = requests.get(request_string)
            old_json[city_name] = {}
            old_json[city_name]['data'] = response.json()['data']
            old_json[city_name]['address'] = city_addr
            
    with open('city_json.json', 'w') as f:
        json.dump(old_json, f)

def make_city_spreadsheet(list_of_city_name_strings):
    city_dict = city_search(list_of_city_name_strings)
    for i in range(len(list_of_city_name_strings)):
        print('now trying ' + list_of_city_name_strings[i])
        hotspot_addr_list = get_hotspot_addrs_in_city(city_dict[list_of_city_name_strings[i]])
        # print(hotspot_addr_list)
        hotspot_income_list = get_list_of_hnt_income(hotspot_addr_list)
        # print(hotspot_income_list)
        update_income_spreedsheet(hotspot_income_list,list_of_city_name_strings[i])
        
def get_iso_month_bounds_bt_dates(start_year,start_month,end_year,end_month):
    #insert years and months as ints
    #get out list of iso date bounds, with start day of month, end day of month, start day of month, end day of month, etc
    # from datetime import datetime

    start = datetime.datetime(start_year, start_month, 1)
    end = datetime.datetime(end_year, end_month, 1)
    list_of_dates_iter = [(d.month, d.year) for d in rrule(MONTHLY, dtstart=start, until=end)]
    
    iso_month_bounds = []
    for m in list_of_dates_iter:
        # datetime.datetime.strptime("2013-1-25", '%Y-%m-%d').isoformat()
        # iso_month_bounds.append('2021-03-06T00:50:37.262Z')
        iso_month_bounds.append(datetime.datetime.strptime(str(m[1]) +'-'+str(m[0])+'-1-0-0-0', '%Y-%m-%d-%H-%M-%S').isoformat())
        iso_month_bounds.append(datetime.datetime.strptime(str(m[1]) +'-'+str(m[0])+'-'+str(calendar.monthrange(m[1],m[0])[1])+'-23-59-59', '%Y-%m-%d-%H-%M-%S').isoformat())
    return iso_month_bounds

def iso_to_dt(iso):
    # return datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S%z")
    return arrow.get(iso).datetime

def update_json_with_income_by_month(start_year=2013,start_month=11,end_year=2021,end_month=3):
    date_list = get_iso_month_bounds_bt_dates(start_year,start_month,end_year,end_month)
    with open('city_json.json') as json_file:
        old_json = json.load(json_file)
    
    for city_name in old_json.keys():
        for hotspot in range(len(old_json[city_name]['data'])):
            if 'income_by_month' in old_json[city_name]['data'][hotspot].keys():
                continue
            old_json[city_name]['data'][hotspot]['income_by_month'] = {}
            date_added_to_network_iso = old_json[city_name]['data'][hotspot]['timestamp_added']
            print(date_added_to_network_iso)
            for i in range(len(date_list)-1):
                if (iso_to_dt(date_list[i+1]) - iso_to_dt(date_list[i])) < datetime.timedelta(seconds = 5):
                    continue
                if date_list[i] in old_json[city_name]['data'][hotspot]['income_by_month'].keys():
                    continue
                if iso_to_dt(date_added_to_network_iso) < iso_to_dt(date_list[i+1]):
                    income = hnt_mined_timespan(old_json[city_name]['data'][hotspot]['address'],date_list[i],date_list[i+1])
                    old_json[city_name]['data'][hotspot]['income_by_month'][date_list[i]] = income
                    print('date ' + date_list[i] + ' included')
                else:
                    print('date ' + date_list[i] + ' thrown out')
            with open('city_json.json', 'w') as f:
                json.dump(old_json, f)
                    

 
def update_json_with_city_income():

        
    with open('city_json.json') as json_file:
        old_json = json.load(json_file)
        
    
    
    for city in old_json:
        if 'total_income_by_month' in old_json[city].keys():
            continue
        old_json[city]['total_income_by_month'] = {}
        for date in get_iso_month_bounds_bt_dates(start_year=2013,start_month=11,end_year=2021,end_month=3):
            # print(date)
            # income_sum_for_date = 0
            for hotspot in old_json[city]['data']:
                # old_json[city]['total_income_by_month'] = {}
                if date in hotspot['income_by_month'].keys():
                    print(str(date) + '   ' + str(hotspot['income_by_month'][date]))
                    if hotspot['income_by_month'][date] > -1:
                        pass
                    else:
                        continue
                    # income_sum_for_date += hotspot['income_by_month'][date]
                    if date in old_json[city]['total_income_by_month'].keys():
    
                        old_json[city]['total_income_by_month'][date] += hotspot['income_by_month'][date]
                    else:
                        old_json[city]['total_income_by_month'][date] = hotspot['income_by_month'][date]
            # old_json[city]['total_income_by_month'][date] = income_sum_for_date
    
    with open('city_json.json', 'w') as f:
        json.dump(old_json, f)


def write_city_monthly_income_excel():
    date_list = get_iso_month_bounds_bt_dates(start_year=2013,start_month=11,end_year=2021,end_month=3)
    # date_list.remove([i for i in date_list if '59' in i])
    date_list = [i for i in date_list if ':00' in i] #isolate only start dates
    
    with open('city_json.json') as json_file:
        old_json = json.load(json_file)
    
    city_list = old_json.keys()
    
    # two_d_mat = np.array([]).reshape(2,2)
    
    
    #pad the lists on top with NaN and append to 2d np mat
    first = True
    for city in old_json:
        array_of_incomes=np.pad(pad_width = (len(date_list)-len(list(old_json[city]['total_income_by_month'].values())),0) ,mode='constant',constant_values=np.NAN,array=list(old_json[city]['total_income_by_month'].values()))
        if first:
            two_d_mat = array_of_incomes
            # two_d_mat = np.expand_dims(two_d_mat, axis=1)
            first=False
        else:
            two_d_mat = np.append(arr=two_d_mat,values=array_of_incomes)
    two_d_mat = np.reshape(order='F',a=two_d_mat,newshape=(len(date_list),len(city_list)))
    
    df = pandas.DataFrame(data=two_d_mat,index=date_list,columns=city_list)
    
    df.to_excel('total_city_income_by_month.xls',na_rep='NaN')
    
    
    
def do_list_thing():
        
    with open('city_json.json') as json_file:
        old_json = json.load(json_file)
        
    date_list = get_iso_month_bounds_bt_dates(start_year=2013,start_month=11,end_year=2021,end_month=3)
        # date_list.remove([i for i in date_list if '59' in i])
    date_list = [i for i in date_list if ':00' in i] #isolate only start dates
    
    for city in old_json:
        old_json[city]['hotspots_by_month'] = {}
        
        # first = True
        for date in date_list:
            # if first:
            old_json[city]['hotspots_by_month'][date] = 0
                # first = False
            for hotspot in old_json[city]['data']:
                if iso_to_dt(hotspot['timestamp_added']) < iso_to_dt(date):
                    old_json[city]['hotspots_by_month'][date] += 1
    
    with open('city_json.json', 'w') as f:
        json.dump(old_json, f)
    

def excel_thing():
        
    with open('city_json.json') as json_file:
            old_json = json.load(json_file)
    city_list = old_json.keys()
    date_list = get_iso_month_bounds_bt_dates(start_year=2013,start_month=11,end_year=2021,end_month=3)
    # date_list.remove([i for i in date_list if '59' in i])
    date_list = [i for i in date_list if ':00' in i] #isolate only start dates
    
    first = True
    for city in old_json:
        array_of_incomes=list(old_json[city]['hotspots_by_month'].values()) 
        if first:
            two_d_mat = array_of_incomes
            # two_d_mat = np.expand_dims(two_d_mat, axis=1)
            first=False
        else:
            two_d_mat = np.append(arr=two_d_mat,values=array_of_incomes)
    two_d_mat = np.reshape(order='F',a=two_d_mat,newshape=(len(date_list),len(city_list)))
    
    df = pandas.DataFrame(data=two_d_mat,index=date_list,columns=city_list)
    
    df.to_excel('hotspot_growth_by_month.xls',na_rep='NaN')

    
save_city_json(city_search(['Beijing','San Francisco','Dallas','Los Angeles','San Diego','Chicago','Seattle','Atlanta','London','Berlin','Paris','Amsterdam','Madrid','Austin','Lisboa','Boston','Minneapolis','Denver','🇷🇴București','Zagreb','Stockholm','Miami']))
# save_city_json({'New York':'bmV3IHlvcmtuZXcgeW9ya3VuaXRlZCBzdGF0ZXM'})

update_json_with_income_by_month()
update_json_with_city_income()
do_list_thing()


# yes = iso_to_dt('2014-05-01T00:00:00') < iso_to_dt('2020-10-13T13:43:16.000000Z')
    
    
    
    
# update_json_with_city_income()
# write_city_monthly_income_excel()






    # test = np.append(axis=0,arr=two_d_mat,values=np.pad(array=np.array(old_json[city]['total_income_by_month']),pad_width=len(date_list)))
    # for date in old_json[city]['total_income_by_month']:
    #     for other_date in date_list:
    #         if date = other

    # list_of_incomes=np.pad(pad_width = (len(date_list)-len(list(old_json[city]['total_income_by_month'].values())),0) ,mode='constant',constant_values=np.NAN,array=list(old_json[city]['total_income_by_month'].values()))

# with open('city_json.json') as json_file:
#     old_json = json.load(json_file)

# for city in old_json:
#     df_income_by_month = pandas.DataFrame(columns=old_json.keys(),index=old_json[city]['total_income_by_month'].keys,data=)

# df_income_by_month.to_excel('city_income_by_month.xls',index=False)


# save_city_json(city_search(['Beijing','San Francisco','Dallas','Los Angeles','San Diego','Chicago','Seattle','Atlanta','London','Berlin','Paris','Amsterdam','Madrid']))
# save_city_json(city_search(['Beijing']))

# update_json_with_income_by_month()
# update_json_with_city_income()

# data = np.zeros((122, 40, 30))

# writer = pd.ExcelWriter('file.xlsx', engine='xlsxwriter')

# for i in range(0, 30):
#     df = pd.DataFrame(data[:,:,i])
#     df.to_excel(writer, sheet_name='bin%d' % i)

# writer.save()


# datetime_obj_hopefully = iso_to_dt(get_iso_month_bounds_bt_dates(2012,1,2012,5)[0])
# date_list = get_iso_month_bounds_bt_dates(start_year=2013,start_month=11,end_year=2021,end_month=3)

# = get_iso_month_bounds_bt_dates(2012,1,2012,5)
# data = np.zeros((122, 40, 30))

# writer = pandas.ExcelWriter('test_file_lol.xlsx', engine='xlsxwriter')

# for i in range(0, 30):
#     df = pandas.DataFrame(data[:,:,i])
#     df.to_excel(writer, sheet_name='bin%d' % i)

# writer.save()
        
        
        

        
        
# make_city_spreadsheet(['London','Beijing','Berlin','Amsterdam'])


#manually add city:
# hotspot_addr_list = get_hotspot_addrs_in_city('bWVndXJvIGNpdHl0xY1recWNLXRvamFwYW4')
# hotspot_income_list = get_list_of_hnt_income(hotspot_addr_list)
# update_income_spreedsheet(hotspot_income_list,'Tōkyō-to')

# city_name_dict = {'San Diego':'c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM'}
# city_hotspot_dict = {}
# request_string = "https://api.helium.io/v1/cities/c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM/hotspots"
# response = requests.get(request_string)
# city_hotspot_dict['data'] = response.json()['data']
# city_hotspot_dict['city_address'] = city_name_dict

# import json
# with open('city_json.json', 'w') as f:
#     json.dump(city_hotspot_dict, f)

# old debug stuff below:

# SD = [2.41135953, 78.85727829, 70.03054614, 83.04223993, 119.83383009, 163.34241515, 115.70542069, 180.95051867, 86.31049044, 94.10215642, 83.72546183, 26.44720088, 203.13617231, 227.7830351, 497.75148162, 80.62996336, 43.70858791, 309.86317458, 296.11015284, 242.05312936, 164.42084796, 177.1763188, 344.98917672, 71.36347095, 110.3786777, 311.16209543, 219.82774814, 77.17562706, 96.10991909, 372.05580882, 467.95697899, 0.0, 0.0, 230.54412297, 156.4313668, 352.63467355, 110.75869735, 153.45330363, 510.80823612, 734.09066847, 88.24139086, 23.18341235, 94.34461351, 258.83267648, 246.37758835, 13.75479062, 30.01533273, 324.23532832, 180.66274094, 269.24768201, 286.87343061, 288.98685111, 229.93715649, 1389.43995528, 113.24145361, 40.9867689, 241.34883823, 234.01515795, 234.22924675, 131.0696028, 318.67343629, 58.15627151, 309.29837244, 221.87653463, 427.385226, 236.88670515, 38.65395341, 221.81554229, 0.0, 29.01062084, 541.0296647, 99.30044368, 180.22083768, 321.97329446, 19.85750703, 240.07784152, 244.64117497, 217.73181151, 196.37216725, 1016.92588306, 291.81773878, 459.15658666, 234.66927867, 496.502825, 250.42341132, 85.66541506, 74.02369141, 91.62923324, 938.29375323, 899.82112661, 743.34979614, 81.66157268, 853.88759999, 213.46921553, 496.32594797, 90.37810004, 137.17924723, 106.73947528, 157.99743054, 59.14758752, 398.86186713, 174.60150287, 755.93367684, 243.25963249, 369.24439334, 122.17063857, 291.13241662, 604.00201114, 70.65724308, 1.14672268, 6.84327924, 575.4762742, 529.44855921, 44.44751867, 6.92872519, 20.43368518, 125.0097012, 380.14674413, 349.42696589, 473.96230554, 0.0, 267.94169368, 191.37735319, 199.36171525, 336.92829691, 328.12419498, 265.91826078, 701.14835943, 355.02144199, 240.24504906, 456.13918754, 0.0, 181.99576053, 131.97705758, 288.70216878, 211.55313507, 25.06217926, 59.70939534, 11.86157185, 7.45761912, 89.65344872, 91.27045944, 31.21807696, 190.83462714, 92.35533282, 247.56270666, 13.99037078, 16.29376487, 38.41004237, 11.37274872, 689.68479603, 1154.6980805, 158.75478183, 376.11814925, 381.85168225, 718.66778855, 5.95594727, 289.02508902, 0.0, 379.68210281, 513.85056301, 83.90786908]
# # print(SD)

# hnt_income_list = SD

# city_name = 'San Diego'

# update_income_spreedsheet(SD,"San Diego")




# df_income = pandas.read_excel('city_income.xls')
#         #if spreadsheet column length we just opened is greater than the length of our latest income list, we must pad new list with NaNs
# temp_new_df = pandas.DataFrame({city_name:hnt_income_list})
# if df_income.shape[0] > temp_new_df.shape[0]:
#     temp_new_df = temp_new_df.reindex(range(df_income.shape[0]))
# elif df_income.shape[0] < temp_new_df.shape[0]: #otherwise we pad old list with NaNs
#     df_income = df_income.reindex(range(temp_new_df.shape[0]))

# df_income[city_name] = temp_new_df



# test = city_search(['San Francisco','Dallas','Los Angeles','San Diego','Chicago','Seattle','Atlanta'])

# test = city_search(['Seattle'])

# make_city_spreadsheet(['Austin'])
# df = pandas.read_excel('income_list_.xls')
    

# print(statistics.median(get_list_of_hnt_income(get_hotspot_addrs_in_city('c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM'))))
# print(len(get_hotspot_addrs_in_city('c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM')))

    
# print(hnt_mined_past_days("116y7S1xPcYoybvP8pgVNjfQVCQNN9QkhiWUnSB9kfgbGcczJBa"),30)




# city_string_dict = {'San Diego':'c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM'}

# request_string = "https://api.helium.io/v1/cities?search=" + "San Diego"
# response = requests.get(request_string)
# city_id = response.json()['data'][0]['city_id']
# # print(city_id)
# city_string_dict["San Diego"] = city_id


