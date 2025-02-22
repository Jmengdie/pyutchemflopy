#!/usr/bin/python 
# -*- coding: utf-8 -*-
"""
 @Author: Jane
 @FileName: gif.py
 @DateTime: 2024/10/1 20:31
 @SoftWare: PyCharm
"""
# 该程序用于生成不同时期平面分布图，然后利用多张图片合成一张动图

from PIL import Image
import os
from natsort import natsorted
import matplotlib.pyplot as plt
import numpy as np
import re


def extract_data_layer(filename, main_keyword1, main_keyword2, num_lines):
    data = []
    with open(filename, 'r') as file:
        content = file.read()

        # Find the index of main_keyword1
        start_index = content.find(main_keyword1)
        if start_index == -1:
            return data  # Keyword not found

        # Find the index of main_keyword2 after main_keyword1
        end_index = content.find(main_keyword2, start_index)
        if end_index == -1:
            return data  # Keyword not found

        # Extract the content between main_keyword2 and main_keyword1
        extracted_content = content[end_index + len(main_keyword2):].strip()

        # Split the content into lines
        lines = extracted_content.split('\n')

        # Process each line
        for line in lines[:num_lines]:
            # Extract numbers from the line using regular expression
            numbers = re.findall(r'\S+', line)

            # Filter out zeros and take only the first 10 non-zero numbers
            non_zero_numbers = [float(num) for num in numbers if num != '0']
            data.extend(non_zero_numbers[:10])

    return data


# extract the data of Sn in specific layer
# i表示地层数
for i in [30.138976, 60.276496, 90.143064, 120.319898, 150.240348, 180.176326, 210.502239, 240.304684, 270.271574,
          300.372101, 330.203333, 360.096354, 390.069994, 420.466408, 450.283721, 480.334662, 510.866581, 540.392524,
          570.217076, 600.524330, 630.419313, 660.950785, 690.014994, 720.020441, 750.691391, 780.025135, 810.090260,
          840.328588, 870.278344, 900.673725, 930.285878, 961.093752, 990.088951, 1020.852048, 1050.775050, 1080.586932,
          1110.565582, 1140.767362, 1170.265476, 1200.938220, 1230.301563, 1260.566943, 1290.631806, 1320.398779,
          1350.101610, 1380.496447, 1410.699006, 1441.199596, 1470.510698, 1501.232151, 1531.498318, 1560.333265,
          1590.274766, 1620.390896, 1650.872651, 1680.127741, 1710.331829, 1740.483684, 1770.784718, 1800.478632,
          1830.000000]:
    filename = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\utchem3\UTex21.SATP'

    # 关键词1：提取结果所在的时间
    main_keyword1 = f'{i}'
    # 关键词2：提取对应相
    main_keyword2 = 'SAT. OF PHASE            2 IN LAYER            5'
    # 确定提取关键词1、2之后的数据行数
    num_lines = 195
    result = extract_data_layer(filename, main_keyword1, main_keyword2, num_lines)

    # Reshape the data into a 39×50 array
    heatmap_data = np.array(result[:1950]).reshape((39, 50))  # (NY,NX)

    # # Save the heatmap data to a text file
    # heatmap_filename = fr'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test\
    # \Sn_lay4_{i}.txt'
    # np.savetxt(heatmap_filename, heatmap_data, fmt='%.4f', delimiter='\t')

    # 清除前一张图
    plt.clf()

    # 对应每一个地层平面绘图
    plt.imshow(heatmap_data, cmap='viridis', interpolation='nearest')
    plt.colorbar(shrink=0.45)
    plt.title(f'Sn of DNAPLs in {i} days')
    folder_path = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\gif_layer'
    file_name = f'Sn_lay5_{i}.png'
    plt.savefig(os.path.join(folder_path, file_name), format='png', dpi=300)  # 保存为PNG格式，DPI为300
    # plt.show()
    # print(f"Heatmap data saved to {heatmap_filename}")



# 合成GIF图片
# 图片文件夹路径和输出GIF文件路径
image_folder = r'H:\BaiduSyncdisk\08researchprogress\04Simulation\01_JiaDing_test\pyutchemflopy_Jiading_test3\gif_layer'
# 设置输出GIF的路径，并确保文件名以 .gif 结尾
output_gif = os.path.join(image_folder, 'output_animation_lay5.gif')

# 获取文件夹中的所有文件
files = os.listdir(image_folder)

# 存储PNG图片的列表
png_files = []

# 检查每个文件是否为PNG格式
for file in files:
    file_path = os.path.join(image_folder, file)
    try:
        with Image.open(file_path) as img:
            if img.format == 'PNG':  # 确认文件是PNG格式
                png_files.append(file_path)
    except IOError:
        # 如果文件无法被识别为图片，跳过
        continue

# 检查是否找到任何PNG文件
if not png_files:
    print("没有找到任何PNG图片，请检查图片文件夹路径或图片格式。")
else:
    # 使用 natsorted 对图片路径进行自然排序，确保合成顺序一致
    png_files = natsorted(png_files)

    # 打开所有图片
    images = [Image.open(png_file) for png_file in png_files]

    # 检查图片列表是否为空
    if len(images) > 0:
        # 将第一张图片作为GIF起始帧，其余的作为附加帧
        images[0].save(output_gif, save_all=True, append_images=images[1:], duration=100, loop=1)
        print(f"GIF 动图生成成功，文件路径为: {output_gif}")
    else:
        print("未能加载任何图片，无法生成GIF。")
