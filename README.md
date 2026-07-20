# Genshin artifact reshape math
Contains scripts to build a reshape infographic html page.

Link to colab with all the same math, but interactive figures: [colab](https://colab.research.google.com/drive/15oL4goVCWunXhfJHWgUXhSnHRWw9CLLo?usp=sharing)

## Requirements
`pip install matplotlib numpy scipy`

## Instructions
Run the image generation scripts
```
python make_image1.py
python make_image2.py
python make_image3.py
```

Insert those images into the html template
`python build_infographic.py`
