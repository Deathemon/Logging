# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 14:49:15 2019
自动将Techlog导出的format .csv文件转化为地层压力软件数据库导入需要的格式。
使用时在同目录下创建一个InputData文件夹和一个OutputData文件夹。
@author: Administrator
"""
import csv
import math
import numpy
import os
# import matplotlib.pyplot as plt

def main():
    
    nameList = GetFileNames('InputData\\');
    for fileName in nameList:
            ToSingle(fileName, [])
            print('file ', fileName, ' is done!')     

def GetFileNames(file_dir):   
    L=[]   
    for root, dirs, files in os.walk(file_dir):  
        for file in files:  
            if os.path.splitext(file)[1] == '.csv':  
                L.append(file)  
    return L  


'''
将csv文件测井数据分成单独数据
'''
def ToSingle(fileName, depthRange):
    """
    声波时差：30    -   200     us/ft
    电 阻 率：0.01  -   200
    井    径：2     -   120     cm
    自然伽玛：0     -   210     api
    密    度：0.5   -     8     g/cm^3
    """
    # 1英尺（ft） = 0.3048米    1米 = 3.2808英尺
    # 1英寸（in） = 0.0254米    1米 = 39.37英寸
#    fileName = 'BY5-2-2_BY5-2-2'
#    depthRange = [0,0]
    dataRange = {'DT':[30,200],'CALI':[2,120],'CAL':[2,120],'GR':[0,210],'RHOB':[0.5,8],'DEN':[0.5,8],'RT':[0.01,200],'BS':[0,210],'ECD':[0.5,5]}
    data = Readcsv('InputData\\' + fileName)
    DeleteMatrixColumns(data,[1,2])
    dataHead = data[0][1:]
    DeleteRows(data,[1,2])
    outPath = 'OutputData\\' + fileName
    if not os.path.exists(outPath):
        os.makedirs(outPath) 
    FillEmpty(data)
    outDataList = SplitData(data)
    filtraterColumns = [1]
    minDepth = 0
    maxDepth = 0
    if depthRange:
        filtraterColumns = [0,1]
        minDepth = depthRange[0]
        maxDepth = depthRange[1]
    for i in range(len(outDataList)):
        [minPara, maxPara] = dataRange[dataHead[i]]
        FiltrateData(outDataList[i], [minDepth, minPara], [maxDepth, maxPara], filtraterColumns)
        outData = [['Depth', dataHead[i]]]
        outData.extend(outDataList[i])
        Writecsv(outPath + '\\' + fileName + '-' + dataHead[i] + '.csv', outData)                
    return

'''
打开filePath路径的csv文件
'''
def Readcsv(filePath:str):
    file = open(filePath, encoding='gb18030', errors='ignore')
    fileReader = csv.reader(file)
    data = []
    for dataLine in fileReader:
        data.append(dataLine)
    file.close()
    return data

'''
将data数据写入filePath路径的csv文件
'''
def Writecsv(filePath:list, data:list):
    file = open(filePath, 'w', newline='')
    fileWrite = csv.writer(file, dialect='excel')
    for dataLine in data:
        fileWrite.writerow(dataLine)
    file.close()
    return True

'''
打开filePath路径的csv文件
'''
def Readtxt(filePath:str):
    file = open(filePath)
    fileReader = file.read()
    fileList = fileReader.strip().split('\n')
    data = []
    for dataLine in fileList:
        data.append(dataLine.split())
    file.close()
    return data

'''
将data中的空数据（''）补为0
'''
def FillEmpty(data:list):
    for dataLine in data:
        for i in range(len(dataLine)):
            if dataLine[i] == '':
                dataLine[i] = '-1'
    return True

'''
删除二维列表data中指定列的元素
'''
def DeleteMatrixColumns(data:list, columns:list):
    for dataLine in data:
        for i in reversed(columns):
            del dataLine[i - 1]
    return True

'''
删除一维、二维列表data中指定行的元素
'''
def DeleteRows(data:list, rows:list):
    for i in reversed(rows):
        del data[i - 1]
    return True

'''
删除data中超过范围的值
''' 
def FiltrateData(data:list,mins:list,maxs:list,columns:list):
    rows = []
    for i in range(0, len(data)):
        able = 1
        for j in range(len(data[0])):
            if j in columns:
                if float(data[i][j]) < mins[j]:
                    able = 0
                if float(data[i][j]) > maxs[j]:
                    able = 0
                if able == 0:
                    rows.append(i + 1)
    DeleteRows(data, rows)
    return True

'''
根据系数对数据进行转化
'''
def ConvertData(data:list,para:list):
    for i in range(1, len(data)):
        for j in range(len(data[0])):
            data[i][j] = str(float(data[i][j]) * para[j])
    return True

'''
合并数据列表，按顺序后覆盖前，以第一个列表的列名命名列
'''
def MergeData(dataList:list):
    midData = dict()
    for data in dataList:
        m = 1
        for dataLine in data:
            if m == 1:
                m = 0
                continue
            midData[dataLine[0]] = dataLine[1:]
    outData = []
    outData.append(dataList[0][0])
    for key,value in midData.items():
        dataLine = []
        dataLine.append(key)
        dataLine.extend(value)
        outData.append(dataLine)       
    return outData

'''
将data拆分成同单独测井曲线数据
'''
def SplitData(data:list):
    dataList = []
    column = len(data[0])
    for i in range(column - 1):
        outData = []
        for dataline in data:
            outData.append([dataline[0],dataline[i + 1]])
        dataList.append(outData)
    return dataList

'''
通过表达式，改变data中的某一列数据
'''
def FuncDataColumn(data:list, func, column):
    for dataLine in data:
        dataLine[column - 1] = str(func(float(dataLine[column - 1])))
    return True

'''
通过表达式，改变csvFile中的某一列数据
'''
def FuncFileColumn(inFilePath:str, outFilePath:str, func, column):
    data = Readcsv(inFilePath)
    FuncDataColumn(data, func, column)
    Writecsv(outFilePath, data)
    return True


'''
读入txt格式的MD-INC-AZI数据，返回拟合公式
'''
def PloyFitTXT(filePath:str, mi:int):
    data = Readtxt(filePath)
    MD = []
    INC = []
    AZI = []
    m = 1
    for dataList in data:
        if m == 1:
            m = 0
            continue        
        MD.append(float(dataList[0]))
        INC.append(float(dataList[1]))
        AZI.append(float(dataList[2]))
    TVD = [0 for _ in range(len(MD))]
    for i in range(1,len(MD)):
        TVD[i] = TVD[i - 1] + (MD[i] - MD[i - 1]) * math.cos(INC[i] / 180 * math.pi)
    p = numpy.polyfit(MD, TVD, mi)
    q = numpy.poly1d(p)
    return q

'''
读入txt格式的MD-TVD数据，返回拟合公式
'''
def PloyFitTXT2(filePath:str, mi:int):
    data = Readtxt(filePath)
    MD = []
    TVD = []
    m = 1
    for dataList in data:
        if m == 1:
            m = 0
            continue        
        MD.append(float(dataList[0]))
        TVD.append(float(dataList[1]))
    p = numpy.polyfit(MD, TVD, mi)
    q = numpy.poly1d(p)
    return q

'''
读入csv格式的MD-INC-AZI数据，返回拟合公式
'''
def PloyFitCSV(filePath:str, mi:int):
    data = Readcsv(filePath)
    MD = []
    INC = []
    AZI = []
    m = 1
    for dataList in data:
        if m == 1:
            m = 0
            continue       
        MD.append(float(dataList[0]))
        INC.append(float(dataList[1]))
        AZI.append(float(dataList[2]))
    TVD = [0 for _ in range(len(MD))]
    for i in range(1,len(MD)):
        TVD[i] = TVD[i - 1] + (MD[i] - MD[i - 1]) * math.cos(INC[i] / 180 * math.pi)
    p = numpy.polyfit(MD, TVD, mi)
    q = numpy.poly1d(p)
    return q
'''
读入csv格式的MD-TVD数据，返回拟合公式
'''
def PloyFitCSV2(filePath:str, mi:int):
    data = Readcsv(filePath)
    MD = []
    TVD = []
    m = 1
    for dataList in data:
        if m == 1:
            m = 0
            continue
        MD.append(float(dataList[0]))
        TVD.append(float(dataList[1]))
    p = numpy.polyfit(MD, TVD, mi)
    q = numpy.poly1d(p)
    return q

if __name__ == '__main__':
    main()