import pandas as pd
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display

data = pd.read_csv('All Comments-Reviewed.csv')

city_comment_counts = data.groupby('specialty')['comment'].count().reset_index()

reshaped_city_names = [get_display(arabic_reshaper.reshape(city)) for city in city_comment_counts['specialty']]

plt.bar(reshaped_city_names, city_comment_counts['comment'])
plt.xticks(rotation=90)

fig = plt.gcf()
fig.set_size_inches(18, 9)

output_file_path = "specialtyPlot.png"
plt.savefig(output_file_path, bbox_inches='tight', dpi=300, format='png')

plt.show()
