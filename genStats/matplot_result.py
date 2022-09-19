from doctest import DocFileCase
import xml.etree.ElementTree as ET
from matplotlib.font_manager import FontProperties
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

myTreeList = []
XMLfiles = []
row = []
value = []
Value = []
column = XMLfiles


dir_path = os.path.dirname(os.path.realpath(__file__))
for filename in os.listdir(dir_path):
    if not filename.endswith('.xml'):
        continue
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

for i in range(0, len(Value)):
    for c in column:
        df[str(c)] = Value[i]

df.index = row
# print(df)


cell_text = []
for rows in range(len(df)):
    cell_text.append(df.iloc[rows])


fig, ax1 = plt.subplots()

table = ax1.table(cellText=cell_text,
                  colLabels=column, loc='center',
                  rowLabels=row, rowLoc='center',
                  cellLoc='center',
                  colColours=['#cdb4db']*len(column),
                  rowColours=["#d4e09b"]*len(row),
                  colWidths=[.1]*len(column))
plt.axis('off')
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.5, 1.5)
mng = plt.get_current_fig_manager()
mng.window.showMaximized()
# title = "demo title"
# subtitle = "demo subtitle"
# ax1.set_title(f'{title}\n({subtitle})', weight='bold', size=14, color='k')
plt.show()
ax1.savefig("demo_table2.png", dpi=500, bbox_inches='tight')

