import math
import pandas as pd
import numpy as np
from pandas.io.parsers import read_csv
from pandas import read_excel
#T为15,30,50年一遇年份
T=30
#自记与定时风速换算,手册P169,表3-1-7
#V=连续自记10min平均风速值
#V10=定时观测10min平均风速值，用于30m/s以下的最大风速
#廊坊地区采用北京公式 V=0.841V10+6.08
def wind_transfer_V_V10(V10):
    return 0.841*V10+6.08

#风速观测高度影响的换算，手册P168,式3-1-1
#气象区根据实际情况选择（影响地面粗糙度系数）
#默认换算至地面10m高度风速
alpha_type={'A':0.12,'B':0.16,'C':0.2}
alpha=alpha_type['B']
def hight_transfer(orig_hight,orig_wind,dest_hight=10):
    return orig_wind*(dest_hight/orig_hight/1.0)**alpha

#最大风速计算，手册P170,式3-1-5
#T=重现期，有15,30,50年取值
def wind_speed_max(wind_speed,T):
    n=len(wind_speed)
    assert wind_speed.count()==n
    average=wind_speed.mean()
    std=wind_speed.std()
   # print(wind_speed.describe())
    print(average,std)
    return average-math.sqrt(6)/math.pi*(0.57722+math.log(-math.log(1-1/T)))*std

#w=wind_speed_max(discontinuous_wind,30)
#print(w)

#df=read_csv('base_wind.csv')
df=read_excel('base_wind.xlsx')
year=df[df.columns[0]]
discontinuous_wind=df[df.columns[2]]
continuous_wind=df[df.columns[1]].fillna(0)
#print(continuous_wind.count())
device_hight=df[df.columns[3]]
column_num=len(df)
#查找为空的索引
#print(continuous_wind.isnull())
for i in range(column_num):
    assert discontinuous_wind.count()==column_num
    if continuous_wind[i]==0:
        continuous_wind[i]=wind_transfer_V_V10(discontinuous_wind[i])
    if device_hight[i]!=10:
#转换至10m高度
        continuous_wind[i]=hight_transfer(device_hight[i],continuous_wind[i])

output={'年份':year ,'自记最大风速':continuous_wind ,'定时最大风速':discontinuous_wind}

new_df=pd.DataFrame(output,columns=['年份','自记最大风速','定时最大风速'])
new_df.to_csv('output.csv')
for T in [15,30,50]:
    reference_wind=wind_speed_max(continuous_wind,T)
    rwname='统计{0}年一遇最大风速'.format(T)
    new_line=pd.DataFrame([rwname,reference_wind])
    new_line.to_csv('output.csv',mode='a',header=False,index=False)
