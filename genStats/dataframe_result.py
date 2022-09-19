from doctest import DocFileCase
import xml.etree.ElementTree as ET
import pandas as pd
import os 
import numpy as np
import matplotlib.pyplot as plt

myTreeList = []
XMLfiles = []
row = []
value = []
Value = []
column= XMLfiles;


dir_path = os.path.dirname(os.path.realpath(__file__))
for filename in os.listdir(dir_path):
    if not filename.endswith('.xml'): continue
    fullname = os.path.join(dir_path, filename)
    path_list = fullname.split(os.sep)
    XMLfiles += [str(path_list[-1])]
    myTreeList += [ET.parse(fullname)]
    
    


# mytree = ET.parse('my_intersection.stats.xml')
# mytree2 = ET.parse('my_intersection.stats2.xml')

# myTreeList2 = [mytree, mytree2]


for tree in myTreeList:
    value = []
    row = []
    root = tree.getroot()
    for x in root.findall('.//item'):
        row += [x.attrib['name']]
        value += [x.text] 
    Value += [value]

df = pd.DataFrame(columns=column)

for i in range(0,len(Value)):
    for c in column:
        df[str(c)] = Value[i]

df.index = row;
# print(df)


cell_text = []
for rows in range(len(df)):
    cell_text.append(df.iloc[rows])


fig= plt.subplots(figsize= (8,6))

table = plt.table(cellText=cell_text, colLabels=column,loc='center',rowLabels=row,rowLoc='center',cellLoc='center',colColours=['#F3CC32']*len(column),rowColours=["#DC3735"]*len(row))
plt.axis('off')

mng = plt.get_current_fig_manager()
mng.window.showMaximized()
# title = "demo title"
# subtitle = "demo subtitle"
# ax1.set_title(f'{title}\n({subtitle})', weight='bold', size=14, color='k')
plt.show()


# column_headers = column
# row_headers = row
# cell_text = [row for row in Value[0:]]
# print(cell_text)
# fig, ax1 = plt.subplots(figsize=(16,len(column_headers)))

# rcolors = np.full(len(row_headers), 'linen')
# ccolors = np.full(len(column_headers), 'lavender')

# table = ax1.table(cellText=cell_text,
#                   colLabels=column_headers,
#                   loc='center')
# table.scale(1, 2)
# table.set_fontsize(16)
# ax1.axis('off')
# title = "demo title"
# subtitle = "demo subtitle"
# ax1.set_title(f'{title}\n({subtitle})', weight='bold', size=14, color='k')
# plt.show()
# plt.savefig("demo_table.png", dpi=500, bbox_inches='tight')

