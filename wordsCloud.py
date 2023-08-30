import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from matplotlib.colors import LinearSegmentedColormap
from bidi.algorithm import get_display
import arabic_reshaper

if __name__ == "__main__":
    df = pd.read_csv('All Comments-Reviewed.csv')
    
    stop_words = set(STOPWORDS)
    stop_words.clear()
    # stop_words.update(["است", "بود", "شد", "دکتر", "که", "و", "به", "هم"])
    #ﺮﺘﮐﺩ

    stop_words.update(["است", "ﺩﻮﺑ", "شد", "ﺮﺘﮐﺩ", "ﻪﮐ", "ﻭ", "ﻪﺑ", "ﻢﻫ" , "ﺭﺩ", "ﺯﺍ", "ﺎﺑ" , "ﻭﺭ","ﯼﺍﺮﺑ"])

    bidi_comments = get_display(arabic_reshaper.reshape(" ".join(df['comment'])))

    colors = ["#BF0A30", "#002868"]
    cmap = LinearSegmentedColormap.from_list("colors", colors)


    wc = WordCloud(width=600,
                   height=400,
                   random_state=1,
                   background_color='white',
                   colormap=cmap,
                   collocations=True,
                   stopwords=stop_words,
                   font_path='font.ttf').generate(bidi_comments)
    
    
    with open("c.txt", "w", encoding="utf-8") as f:
        f.write(bidi_comments)
    
    plt.rcParams['font.family'] = 'Mj_Ramollah'
    plt.figure(figsize=[5,5])
    plt.imshow(wc, interpolation="bilinear")
    plt.axis('off')
    plt.show()
