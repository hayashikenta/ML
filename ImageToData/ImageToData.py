import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image
from collections import Counter


def ImageToData(filename, flip_up_side_down=True,
                x_range=None, y_range=None, white_backscreen=False):
    """
    ペイントなどで作った画像から、
    データの作成を行う。
    具体的には、黒いドットを書き込むと、
    その座標を(x,y)とするデータを作成する。




    parameters
    ----------------------------
    filename: str
     画像のファイル名

    flip_up_size_down: bool
     上下の数値を反転させることで、matplotlibで描画するときに想定した形になる
     デフォルトはTrue

    x_range,y_range :list[min,max]
     デフォルトでは画像のサイズに基づいてデータが作成されるが、
     範囲を指定することで軸を変換する

    white_backscreen: bool
     白(255,255,255)を背景として、データと認識しない。デフォルトはFalse

    """

    with open(filename, 'rb') as f:
        binary = f.read()

    img = Image.open(BytesIO(binary))

    img_np = np.array(img)

    image_height, image_width, _ = img_np.shape

    # 0-255の色配列をstr化 [0,0,0] -> "000-000-000"
    img_str_list = ["{:03}-{:03}-{:03}".format(i[0], i[1], i[2]) for i in img_np.reshape(-1, 3)]
    img_np_str = np.array(img_str_list).reshape(image_height, image_width)

    # 色の出現頻度をcollections.Counterで作成
    color_counter = Counter(img_str_list)
    print(color_counter)

    # 最も多く出現する色を背景色として認識する（most_common_color）
    if white_backscreen:
        most_common_color = "255-255-255"
    else:
        most_common_color = color_counter.most_common(1)[0][0]

    # 色辞書の作成 高い頻度を持つ色から0,1,2...となる（0は背景色）
    color_dict = {key: i for i, (key, value) in enumerate(color_counter.items())}

    def transform_by_range(range_list, max_range):

        def inner(x):
            range_min = range_list[0]
            range_max = range_list[1]
            return (x / max_range) * (range_max - range_min) + range_min

        return inner

    x_transform = (lambda x: x) if x_range == None else transform_by_range(x_range, image_width)
    y_transform = (lambda y: y) if y_range == None else transform_by_range(y_range, image_height)

    data_array = np.empty((0, 3))

    # 画像内で、最頻色以外の色を、x,yの値と、色(出現頻度の多い順に1,2...)のデータに変換
    for row in range(image_height):

        for col in range(image_width):

            color_value = img_np_str[row][col]

            if not color_value == most_common_color:

                # np.arrayはすべて同じ形式にさせられる
                # どれかがstrだとすべてstrにされる

                x_temp = x_transform(col)

                if flip_up_side_down:
                    y_temp = y_transform(image_height - row)
                else:
                    y_temp = y_transform(row)

                data_array = np.concatenate(
                    [data_array, np.array(
                        [[x_temp,
                          y_temp,
                          color_dict[color_value]]])],
                    axis=0)

    plt.figure(figsize=(5, 5))
    plt.scatter(data_array[:, 0], data_array[:, 1], c=data_array[:, 2], s=5)

    if x_range: plt.xlim(x_range[0], x_range[1])
    if y_range: plt.ylim(y_range[0], y_range[1])

    return data_array