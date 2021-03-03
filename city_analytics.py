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
    except:
        df_income = pandas.DataFrame({city_name:hnt_income_list})
    
        
        
    
    df_income[city_name] = hnt_income_list
    
    df_income.to_excel('city_income.xls',index=False)
    
    
def city_search(list_of_city_name_strings):
    city_string_dict = {'San Diego':'c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM'}
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

def make_city_spreadsheet(list_of_city_name_strings):
    city_dict = city_search(list_of_city_name_strings)
    for i in range(len(list_of_city_name_strings)):
        print('now trying ' + list_of_city_name_strings[i])
        hotspot_addr_list = get_hotspot_addrs_in_city(city_dict[list_of_city_name_strings[i]])
        # print(hotspot_addr_list)
        hotspot_income_list = get_list_of_hnt_income(hotspot_addr_list)
        # print(hotspot_income_list)
        update_income_spreedsheet(hotspot_income_list,list_of_city_name_strings[i])
        
        
make_city_spreadsheet(['San Francisco','Dallas','Los Angelos','Chicago','Atlanta'])


# old debug stuff below:

# SD = [2.41135953, 78.85727829, 70.03054614, 83.04223993, 119.83383009, 163.34241515, 115.70542069, 180.95051867, 86.31049044, 94.10215642, 83.72546183, 26.44720088, 203.13617231, 227.7830351, 497.75148162, 80.62996336, 43.70858791, 309.86317458, 296.11015284, 242.05312936, 164.42084796, 177.1763188, 344.98917672, 71.36347095, 110.3786777, 311.16209543, 219.82774814, 77.17562706, 96.10991909, 372.05580882, 467.95697899, 0.0, 0.0, 230.54412297, 156.4313668, 352.63467355, 110.75869735, 153.45330363, 510.80823612, 734.09066847, 88.24139086, 23.18341235, 94.34461351, 258.83267648, 246.37758835, 13.75479062, 30.01533273, 324.23532832, 180.66274094, 269.24768201, 286.87343061, 288.98685111, 229.93715649, 1389.43995528, 113.24145361, 40.9867689, 241.34883823, 234.01515795, 234.22924675, 131.0696028, 318.67343629, 58.15627151, 309.29837244, 221.87653463, 427.385226, 236.88670515, 38.65395341, 221.81554229, 0.0, 29.01062084, 541.0296647, 99.30044368, 180.22083768, 321.97329446, 19.85750703, 240.07784152, 244.64117497, 217.73181151, 196.37216725, 1016.92588306, 291.81773878, 459.15658666, 234.66927867, 496.502825, 250.42341132, 85.66541506, 74.02369141, 91.62923324, 938.29375323, 899.82112661, 743.34979614, 81.66157268, 853.88759999, 213.46921553, 496.32594797, 90.37810004, 137.17924723, 106.73947528, 157.99743054, 59.14758752, 398.86186713, 174.60150287, 755.93367684, 243.25963249, 369.24439334, 122.17063857, 291.13241662, 604.00201114, 70.65724308, 1.14672268, 6.84327924, 575.4762742, 529.44855921, 44.44751867, 6.92872519, 20.43368518, 125.0097012, 380.14674413, 349.42696589, 473.96230554, 0.0, 267.94169368, 191.37735319, 199.36171525, 336.92829691, 328.12419498, 265.91826078, 701.14835943, 355.02144199, 240.24504906, 456.13918754, 0.0, 181.99576053, 131.97705758, 288.70216878, 211.55313507, 25.06217926, 59.70939534, 11.86157185, 7.45761912, 89.65344872, 91.27045944, 31.21807696, 190.83462714, 92.35533282, 247.56270666, 13.99037078, 16.29376487, 38.41004237, 11.37274872, 689.68479603, 1154.6980805, 158.75478183, 376.11814925, 381.85168225, 718.66778855, 5.95594727, 289.02508902, 0.0, 379.68210281, 513.85056301, 83.90786908]
# print(SD)

# hnt_income_list = SD

# city_name = 'San Diego'


# df_income = pandas.read_excel('city_income.xls')
#         #if spreadsheet column length we just opened is greater than the length of our latest income list, we must pad new list with NaNs
# temp_new_df = pandas.DataFrame({city_name:hnt_income_list})
# if df_income.shape[0] > temp_new_df.shape[0]:
#     temp_new_df = temp_new_df.reindex(range(df_income.shape[0]))
# elif df_income.shape[0] < temp_new_df.shape[0]: #otherwise we pad old list with NaNs
#     df_income = df_income.reindex(range(temp_new_df.shape[0]))

# df_income[city_name] = temp_new_df

# update_income_spreedsheet(SD,"San Diego")

# test = city_search(['San Francisco','Dallas','Los Angelos','San Diego','Chicago','Seattle','Atlanta'])

# test = city_search(['Seattle'])

# make_city_spreadsheet(['Austin'])
# df = pandas.read_excel('income_list_.xls')
    

# print(statistics.median(get_list_of_hnt_income(get_hotspot_addrs_in_city('c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM'))))
# print(len(get_hotspot_addrs_in_city('c2FuIGRpZWdvY2FsaWZvcm5pYXVuaXRlZCBzdGF0ZXM')))

    
# print(hnt_mined_past_days("116y7S1xPcYoybvP8pgVNjfQVCQNN9QkhiWUnSB9kfgbGcczJBa"),30)


