

import re
import os
import csv
import os.path
import numpy as np
import math
import shutil
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from scipy.optimize import curve_fit
from openpyxl.drawing.image import Image




def s1_SaveAsTxt(new_data,folder_path):
   # 创建文件夹
   if not os.path.exists(folder_path):
       os.makedirs(folder_path)
    # 将结果保存到文件
   # res_file_name = folder_path+"/"+"_".join(new_data[-1][:4]) + "."+new_data[-1][1]+".txt"
   res_file_name = folder_path+"_".join(new_data[-1][:4]) +".txt"
   with open(res_file_name, 'w') as file:
        for row in new_data:
            line = ','.join(str(value) for value in row)
            file.write(line + '\n')
        # print("end clean and save txt",res_file_name)

#分割原始文档数据并且将数据导出
def split_data(filename,folder_path):
    try:
        # print("start split file", filename)
        with open(filename, "r") as file:
            for i in range(8):
                file.readline()
            reader = csv.reader(file, delimiter='\t')
            data = list(reader)
            # 寻找”walker"，并根据它并分段
        start_indices = [i for i, row in enumerate(data) if row and row[0] == "Walker"]
        walker_count = len(start_indices)
        # print(f"Found {walker_count} instance of 'Walker'.")
        # 分段后另存为文件
        file_counter = 1
        for i, start_index in enumerate(start_indices):
            end_index = start_indices[i + 1] if i < len(start_indices) - 1 else len(data)
            if i < len(data) and end_index <= len(data):
                file_name = f"{folder_path + 'raw_data/' + filename.split('/')[-1].split('.')[0]}_{file_counter:02d}.txt"
                file_path = os.path.join(folder_path + "raw_data/", file_name)
                with open(file_path, 'w') as sub_file:
                    writer = csv.writer(sub_file, delimiter='\t')
                    writer.writerows(data[start_index:end_index + 1])
                file_counter += 1
            else:
                print("Invalid start and end index")
        return filename.split('/')[-1].split('.')[0]+"_"
    except:
        print("error for split data ",filename)

#整理文档中的数据并且对数据进行保存
def s1_data_clean_and_save(files_path,folder_path, coordinates):
    for file_path in files_path:
        modified_lines = []
        is_practice =0
        # 提取文件名
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        parts = file_name.split("_")
        if len(parts) >= 2:
            SS = parts[0]
            Trial = parts[1]
        # 读取文本内容
        with open(file_path, 'r') as file:
            lines = file.readlines()
            line_start = []
            for line in lines:
                if line.split("\t")[0] == "Maze":
                    name = line.split("\\")[-1]
                    if len(name.split("practice"))>1 or len(name.split("Practice"))>1:
                        print("文档中含有Practice，不进行后续处理",file_path.split(folder_path.split("res_data")[0])[-1])
                        is_practice=1
                        break
                    else:
                        if len(line.split("\\")[-1].split(".")[0].split("_"))==2:
                            [platform, start] = line.split("\\")[-1].split(".")[0].split("_")
                        else:
                            [platform, start] = line.split("\\")[-1].split(".")[0].split("_")[1:3]
                        line_start = [SS, Trial, platform, start]
                        continue
                elif line == "\n" or len(line.split("\t"))not in [8,9] or line.split("\t")[0] =="Time(ms)" or len(line.split("Event"))>1:
                    continue
                else:
                    line_splits =line.replace("\n","").split("\t")[:8]
                    need_data = line_start+ line_splits[1:4]
                    modified_lines.append("\t".join(need_data))
        if is_practice==1:
            if not os.path.exists(folder_path.split("res_data")[0] + "error/practice/"):
                os.makedirs(folder_path.split("res_data")[0] + "error/practice/")
            # 移动文件
            shutil.move(file_path,folder_path.split("res_data")[0] + "error/practice/" + file_path.split("raw_data")[-1])
            continue

        if len(modified_lines):
            s1_data_export(modified_lines, file_path,folder_path, coordinates)

#数据计算处理，算出各个值的平均值,然后将数据导出
def s1_data_export(essential_data,file_path,folder_path,coordinates):
    new_data = []
    # 将第五-七列数据转换为列表
    d_sums = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    d_count = 0
    probe_sums = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
    probe_count =[0,0,0,0,0]
    try:
        for row in essential_data:
            new_row = row.split("\t")[:-3]  # 复制第一到第四列的数据，不进行转换
            converted_values = []
            for i, value in enumerate(row.split("\t")[-3:]):
                value = float(re.match(r'^[-+]?[0-9]*\.?[0-9]*', str(value))[0])
                # value = float(va)
                # print(value,type(value))
                if value is not None:
                    if i == 0:
                        converted_values.append(int(value / 100))
                    else:
                        converted_values.append(round(value, 4))
                else:
                    print("error-", row)
                    continue
            if new_data == [] or new_data[-1][-3] != converted_values[0]:
                d = []
                # 如果是probe，则按照原逻辑进行sum计算以及数据添加 ,如果是platform，仅在时间<=1200的时候进行sum计算以及数据的添加，否则跳过
                if row.split("\t")[:-3][2].lower() == "probe" or (
                        row.split("\t")[:-3][2][:8].lower() == "platform" and converted_values[0] <= 1200):
                    for j, coordinate in enumerate(coordinates):
                        d.append(math.sqrt(
                            (converted_values[1] - coordinate[0]) ** 2 + (converted_values[2] - coordinate[1]) ** 2))
                        d_sums[j] += d[-1]
                        if row.split("\t")[:-3][2].lower() == "probe":
                            if int(max(converted_values[0] - 1, 0) / 150):
                                probe_sums[-1][j] += d[-1]
                                probe_count[-1] += 1
                            probe_sums[int(max(converted_values[0] - 1, 0) / 150)][j] += d[-1]
                            probe_count[int(max(converted_values[0] - 1, 0) / 150)] += 1
                    d_count += 1
                    new_data.append(new_row + converted_values)

        d_avg = [round(d_sum / int(d_count), 3) for d_sum in d_sums]

        # #最后数据汇总，最长时间，平均距离
        try:
            new_data.append(new_data[-1][:5] + d_avg)
        except:
            print(new_data[-1][:5], d_avg)
            print(new_data)
        # 如果数据中的含有probe，会重新生成4组数据
        if new_data[-1][2].lower() == "probe":
            for i in range(0, 5):
                new_data.append(
                    new_data[-1][:5] + [round(probe_sum / probe_count[i] * 8, 3) for probe_sum in probe_sums[i]])
        s1_SaveAsTxt(new_data, folder_path)
    except:
        print("文件拆分错误转移到错误文件夹中",file_path)
        # 确保目标文件夹存在
        if not os.path.exists(folder_path.split("res_data")[0] + "error/raw_data/"):
            os.makedirs(folder_path.split("res_data")[0] + "error/raw_data/")
        # 移动文件
        shutil.move(file_path, folder_path.split("res_data")[0] + "error/raw_data/" + file_path.split("raw_data")[-1])


#获取文件夹下的某个类型/全类型的文件名称，并且排序，返回含路径的地址
def get_files_name(folder_path,type,content):
    #type =0 获取所有文件
    if type==0:
        txt_files = [file for file in os.listdir(folder_path) if os.path.isfile(folder_path)]
    #type ==1 获取以content结尾的文件
    elif type ==1:
        txt_files = [file for file in os.listdir(folder_path) if file.endswith(content)]
    # type ==2 获取以content开头的文件
    elif type ==2:
        txt_files = [file for file in os.listdir(folder_path) if file.startswith(content) and file.endswith(".txt")]
    txt_files = [os.path.join(folder_path, file) for file in txt_files]
    txt_files.sort(key=lambda x: x.split(".")[0])
    return txt_files


def polygon_area(points):
    x = points[:, 0]
    y = points[:, 1]
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

#创建表格中的数据
def create_excle_data(folder_path,out_begin_with,platform_sort):
    res_files = get_files_name(folder_path , 2, out_begin_with)
    previous_plat = ""
    excle_data =[]
    for file in res_files:
        with open(file,  'r',errors='ignore') as f:
            lines = f.readlines()
            try:
                # 如果判断为platform，则只用去最后一条数据,
                #并且将最后一条之前的所有数据找到点，然后求得凸形顶点以及面积
                if len(re.match(r'platform[0-9]*', lines[-1].split(",")[2])[0]) > 8:
                    previous_plat = re.match(r'platform[0-9]*', lines[-1].split(",")[2])[0]
                    data = lines[-1].replace("\n", "").split(",")
                    d_sort = []
                    for i, value in enumerate(platform_sort[data[2]]):
                        d_sort.append(data[-8:][value - 1])
                    # 计算抛物线a,b,c的值，并将值对应的添加到列表中
                    # x_data = [-2, -1, 0, 1, 2]
                    x_data = [1, 2, 3, 4, 5]
                    y_data = [float(item) for item in data[-7:-2]]
                    # popt, pcov = curve_fit(parabolic, x_data, y_data)
                    # a, b, c = popt
                    coefficients = np.polyfit(x_data, y_data,2)
                    a,b,c = coefficients

                    # !!!a,b,c = np.polyfit(x_data,y_data,deg=2)
                    data[-8:] = d_sort
                    #并且将最后一条之前的所有数据找到点，然后求得凸形顶点以及面积
                    points= []
                    for line in lines[:-1]:
                        x,y = line.replace("\n","").split(",")[-2:]
                        points.append([float(x),float(y)])
                    points = np.array(points)
                    are,are_path = hull_points(points,file.split(".")[0] + '_hull.png')
                    # 显示图像
                    # a = sorted([f.name for f in matplotlib.font_manager.fontManager.ttflist])
                    # for i in a:
                    #     print(i)
                    excle_data.append(data[:5] + [data[-5],are,are_path] + data[-8:] + [round(a, 3), round(b, 3), round(c, 3)])
            except:
                try:
                    # Probe，则取最后五条数据，进行加工
                    if len(re.match(r'probe', lines[-1].split(",")[2].lower())[0]) == 5:
                        points = []
                        for line in lines[:-6]:
                            x, y = line.replace("\n", "").split(",")[-2:]
                            points.append([float(x), float(y)])
                        points = np.array(points)
                        are,are_path = hull_points(points, file.split(".")[0] + '_hull.png')
                        are_1,are_1_path = hull_points(points[:151], file.split(".")[0] + '_1_hull.png')
                        are_2,are_2_path = hull_points(points[:301], file.split(".")[0] + '_12_hull.png')
                        are_3,are_3_path = hull_points(points[:451], file.split(".")[0] + '_123_hull.png')
                        are_4,are_4_path = hull_points(points[:601], file.split(".")[0] + '_1234_hull.png')
                        are_234,are_234_path = hull_points(points[151:], file.split(".")[0] + '_234_hull.png')
                        d_all = [d_sort[3],are,are_path]
                        for j, line in enumerate(lines[-6:]):
                            if j ==1:
                                d_all += ["Block1",are_1,are_1_path]
                            elif j ==2:
                                d_all += ["Block2",are_2,are_2_path]
                            elif j == 3:
                                d_all += ["Block3",are_3, are_3_path]
                            elif j == 4:
                                d_all += ["Block4",are_4, are_4_path]
                            elif j == 5:
                                d_all += ["Block234",are_234, are_234_path]
                            d_sort = []
                            for i, value in enumerate(platform_sort[previous_plat]):
                                d_sort.append(line.replace("\n", "").split(",")[-8:][value - 1])
                            x_data = [-2, -1, 0, 1, 2]
                            y_data = line.replace("\n", "").split(",")[-7:-2]
                            popt, pcov = curve_fit(parabolic, x_data, y_data)
                            a, b, c = popt
                            d_all += d_sort + [round(a, 3), round(b, 3), round(c, 3)]

                        data = lines[-1].replace("\n", "").split(",")[:-8] + d_all
                        excle_data.append(data)

                except:
                    print("except这个文件中解析数据错误，需要人工处理：", file)
    return excle_data

#计算顶点的数据
def hull_points(points,path):

    # plt.rcParams['axes.unicode minus']=False
    try:
        hull = ConvexHull(points)
        hull_ver = hull.vertices
        tip_points = points[hull_ver]
        are = round(polygon_area(tip_points), 4)
        # 绘制凸包多边形和所有点
        plt.rcParams['font.family'] = ['SimHei']
        # plt.rcParams['font.sans-serif'] = ['SimHei']# 定然认字体
        plt.figure()
        plt.plot(points[:, 0], points[:, 1], 'o', label='all points')
        # plt.plot(points[:, 0], points[:, 1], 'o', label='all points', fontfamily='Helvetica')
        # plt.plot(tip_points[:, 0], tip_points[:, 1], 'r-', lw=2, label='top points', fontfamily='Helvetica')
        plt.plot(tip_points[:, 0], tip_points[:, 1], 'r-', lw=2, label='top points')
        plt.fill(tip_points[:, 0], tip_points[:, 1], alpha=0.3, edgecolor='r')
        # 添加标签和标题
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.grid(True)
        plt.legend()
        # 保存图像为PNG文件
        # plt.savefig()
        plt.savefig(path)
        plt.close()
        return are,path
    except:
        print("该图片中点在一条直线上，无法计算面积",path)
        # 绘制凸包多边形和所有点
        plt.rcParams['font.family'] = ['SimHei']
        # plt.rcParams['font.sans-serif'] = ['SimHei']# 定然认字体
        plt.figure()
        plt.plot(points[:, 0], points[:, 1], 'o', label='all points')
        # plt.plot(points[:, 0], points[:, 1], 'o', label='all points', fontfamily='Helvetica')
        # plt.plot(tip_points[:, 0], tip_points[:, 1], 'r-', lw=2, label='top points', fontfamily='Helvetica')
        # plt.plot(tip_points[:, 0], tip_points[:, 1], 'r-', lw=2, label='top points')
        # plt.fill(tip_points[:, 0], tip_points[:, 1], alpha=0.3, edgecolor='r')
        # 添加标签和标题
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.grid(True)
        plt.legend()
        # 保存图像为PNG文件
        # plt.savefig()
        plt.savefig(path)
        plt.close()
        return np.float64(0.000), path


def parabolic(x, a, b, c):
    return a * x * x + b * x + c



#给表格里面保存图片
def saveimg_to_excle(ws,row,column_id,row_idx,max_width,max_height,column_name):
    img_path = row[column_id]
    img = Image(img_path)
    ws.column_dimensions[column_name].width = max_width
    ws.row_dimensions[row_idx].height = max_height
    img.width = 4 * max_width
    img.height = max_height
    img.anchor = ws.cell(row=row_idx, column=column_id+1).coordinate
    ws.add_image(img)


