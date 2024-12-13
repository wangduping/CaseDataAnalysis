import os


import METHOD
import shutil
import datetime

from openpyxl import Workbook








# #初始化数据，删除raw_data 以及 res_data文件夹，并且生成这两个文件夹,达到数据初始化的目的
def init_folder(folder_path):
    try:
        shutil.rmtree(folder_path + "raw_data")
        shutil.rmtree(folder_path + "res_data")
        shutil.rmtree(folder_path + "error")
    except:
        print("没有找到对应目录，不进行删除")
    os.makedirs(folder_path + "raw_data", exist_ok=True)
    os.makedirs(folder_path + "res_data", exist_ok=True)




def export_excle_only(file,folder_path,platform_sort):
    print("开始分析并绘图：", file)
    excle_data= []
    out_begin_with = file.split("/")[-1].split(".")[0] + "_"
    excle_data += (METHOD.create_excle_data(folder_path, out_begin_with, platform_sort))
    return excle_data




def processing_data(file,coordinates,folder_path):
    print("开始拆分数据：", file)
    excle_data= []
    out_begin_with = METHOD.split_data(file,folder_path)
    out_files = METHOD.get_files_name(folder_path+"raw_data/",2,out_begin_with)
    METHOD.s1_data_clean_and_save(out_files, folder_path + "res_data/", coordinates)
    # excle_data+=(METHOD.create_excle_data(folder_path + "res_data/",out_begin_with,platform_sort))
    print("拆分文件数据完成：", file)
    return file
    # result_queue.put(file)




def save_as_excle(excle_datas,folder_path):
    wb = Workbook()
    ws = wb.active

    headers = excle_datas[0]
    ws.append(headers)
    for row in excle_datas[1:]:
        if row[2] == "Probe":
            # ws.append(row[:7] + [""] + row[8:21] + [""] + row[22:35] + [""] +row[36:49] + [""] +row[50:63] + [""] +row[64:77]+""+row[78:])
            ws.append(row)
        else:
            ws.append(row[:7] + [""] + row[8:])

    for row_idx, row in enumerate(excle_datas[1:], start=2):
        max_width = 20
        max_height = 40
        METHOD.saveimg_to_excle(ws, row, 7, row_idx, max_width, max_height, "H")
        if row[2] == "Probe":
            METHOD.saveimg_to_excle(ws, row, 21, row_idx, max_width, max_height, "V")
            METHOD.saveimg_to_excle(ws, row, 35, row_idx, max_width, max_height, "AJ")
            METHOD.saveimg_to_excle(ws, row, 49, row_idx, max_width, max_height, "AX")
            METHOD.saveimg_to_excle(ws, row, 63, row_idx, max_width, max_height, "BL")
            METHOD.saveimg_to_excle(ws, row, 77, row_idx, max_width, max_height, "BZ")

    wb.save(folder_path + datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".xlsx")
