

import MODULE
import METHOD
import concurrent.futures

#点的坐标
COORDINATES = [[24, 16],[24, 26],[34, 26],[34, 16],[29, 16],[24, 21],[29, 26],[34, 21]]

#不同platform点的计算顺序
PLATFORM_SORT= {
    "platform1":[7,2,6,1,5,4,8,3],
    "platform2":[8,3,7,2,6,1,5,4],
    "platform3":[5,4,8,3,7,2,6,1],
    "platform4":[6,1,5,4,8,3,7,2],
    "platform5":[2,6,1,5,4,8,3,7],
    "platform6":[3,7,2,6,1,5,4,8],
    "platform7":[4,8,3,7,2,6,1,5],
    "platform8":[1,5,4,8,3,7,2,6]

}


# #文件夹目录
# ####只需要更改最底层文件夹的目录了，下面的目录可以自动生成
#不同用户需要更改对应的文件夹，并且注意目录最后需要带上/
FOLDER_PATH=r"C:/Users/HZ/Desktop/sisi/"



if __name__ == '__main__':

    print("请选择需要执行的程序编号：\n")
    print("1、全流程（初始数据拆分，数据分析以及导出）\n")
    print("2、半流程（仅做数据图形整合和导出）\n")
    # p = input("请输入你的选择:")
    p = "1"

    excle_datas = [
        ["Subject", "Trial", "Platform", "Start", "total time(10HZ)", "avgDistance_Target", "areaBin1234", "img", "L3",
         "L2", "L1", "Target", "R1", "R2", "R3", "Opp", "a", "b", "c", "", "are", "img", "L3", "L2", "L1", "Target",
         "R1", "R2", "R3", "Opp", "a", "b", "c", "", "are", "img", "L3", "L2", "L1", "Target", "R1", "R2", "R3", "Opp",
         "a", "b", "c", "", "are", "img", "L3", "L2", "L1", "Target", "R1", "R2", "R3", "Opp", "a", "b", "c", "", "are",
         "img", "L3", "L2", "L1", "Target", "R1", "R2", "R3", "Opp", "a", "b", "c"]]
    filenames = METHOD.get_files_name(FOLDER_PATH, 1, ".txt")
    # sum = len(filenames)
    i = 1
    if p == "1":
        # 初始化文件目录
        MODULE.init_folder(FOLDER_PATH)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(MODULE.processing_data, filename, COORDINATES, FOLDER_PATH) for filename in
                       filenames]
    for i,file in enumerate(filenames):
        print("开始分析并绘图：", file,"剩余文件数量：",len(filenames)-i)
        res = MODULE.export_excle_only(file, FOLDER_PATH + "res_data/", PLATFORM_SORT)
        excle_datas += res
    MODULE.save_as_excle(excle_datas, FOLDER_PATH)

