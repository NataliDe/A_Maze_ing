from mlx import Mlx
from random import randint 

def key_hooks(keycode, arguments):
    mlx = arguments['mlx']
    window = arguments['window']
    ptr = arguments['mlx_ptr']
    draw = arguments['draw']
    args_draw = arguments['draw_args']
    if keycode == 65307:
        mlx.mlx_destroy_window(ptr, window)
        mlx.mlx_loop_exit(ptr)
    if keycode == 32:
        arguments['color'] = bytes([randint(0, 255), randint(0, 255), randint(0, 255), 255])
        draw(*args_draw, arguments['my_way'], arguments['color'])
    if keycode == 65293:
        arguments['my_way'] = not arguments['my_way']
        draw(*args_draw, arguments['my_way'], arguments['color'])

    

def show_me_this_shieeeeet(block, row_idx, block_idx, size_line, scale, image_address, color):
    numer = int(block, 16)
    str_bin = format(numer, '04b')
    west = str_bin[0]
    south = str_bin[1]
    east = str_bin[2]
    north = str_bin[3]
    offset_x = scale * block_idx * 4
    offset_y = scale*size_line*row_idx

    if north == "1":
        image_address[offset_x + offset_y:scale*4 + offset_x + offset_y] = color * scale
    if south == "1":
        image_address[(scale - 1)*size_line + offset_x + offset_y:(scale - 1)*size_line+scale*4 + offset_x + offset_y] = color * scale
    
    for i in range(scale):
        if west == "1":
            image_address[size_line*i + offset_x + offset_y:size_line*i + offset_x + offset_y + 4] = color
        if east == "1":
            image_address[size_line*i + offset_x + offset_y + ((scale - 1) * 4):size_line*i + offset_x + offset_y+((scale - 1) * 4)+4] = color

def put_block(image_address, scale, size_line, x, y, color):
    offset_x = scale * x * 4
    offset_y = scale*size_line*y
    for i in range(scale):
        image_address[offset_x + offset_y + i * size_line:scale*4 + offset_x + offset_y+ i * size_line] = color * scale

def drrraw(mlx, mlx_pointer, window, image, tab_str, size_line, scale, image_address, start, exit, path, bedzie_scieszka, color):
    image_address[:] = bytes([0, 0, 0, 255]) * (len(image_address)//4)
    if bedzie_scieszka:
        for step in path:
            put_block(image_address, scale, size_line, *step, bytes([0,255,255,255]))
    put_block(image_address, scale, size_line, start[0], start[1], bytes([255,0,0,255]))
    put_block(image_address, scale, size_line, exit[0], exit[1], bytes([0,255,0,255]))
    for row_idx, row in enumerate(tab_str):
        for block_idx, block in enumerate(row):
            if block == "F":
                put_block(image_address, scale, size_line, block_idx, row_idx, bytes([0,0,255,255]))
    for row_idx, row in enumerate(tab_str):
        for block_idx, block in enumerate(row):
            show_me_this_shieeeeet(block, row_idx, block_idx, size_line, scale, image_address, color)
    mlx.mlx_put_image_to_window(mlx_pointer, window, image, 0, 0)

def main():

    mlx = Mlx()
    mlx_pointer = mlx.mlx_init()

    window = mlx.mlx_new_window(mlx_pointer, 1500, 800, "Natalia")
    image = mlx.mlx_new_image(mlx_pointer, 1500, 750)
    (image_address, bpp, size_line, theformat) = mlx.mlx_get_data_addr(image)
    path_str = "EESSESSSESEESSSWSWSSWWSSSWSSWWSSESSESESEESESENNNEEEEEEEEENEESEESSSSSENENNEEENWWNNNEENEEESESSSSSSSS"

    string_main = "D53BD15153B95179155115117D3BD3\n\
B94056D6946C3C3AC7BEC7EC150416\n\
AC7AB9156BD3ABAA93ABB93D692B87\n\
C3BC2EEB94542AEC6EAC2EABBAAA87\n\
94692D52EB93AC53954101402EAAAB\n\
ABD2A97AB86E8556C392AEBA83C2C2\n\
843A82D4407941553AEEAD2EE87ED2\n\
ED2EEC13BAB87ABBAC792B83D6BD52\n\
B96D17EA86C4782A8512EAAC794792\n\
C43947B8057B96AC6BAC3C2BBABBEA\n\
D12C3B86C3D46BC392AB852A86AABA\n\
9681286BB87B96D02A86EB82A96A86\n\
E96EAAD004546952EEC3BAEC441447\n\
D69142D2EBBBF87EFFFEA83D394397\n\
BBA87ABE9282FC5557FB82EBAEBAC3\n\
86E83C296AEAFFFBFFFC2EBC07A852\n\
8516ED287EBC3BFAFD5107852D2ED2\n\
C787B9683947AAFAFFFE8143C7C53A\n\
9507AA96C6BD043ABD3BEABE917B82\n\
ABC7868155416D684146BA856EB86E\n\
82D3C7EC3D3C53BAD4152AAD510417\n\
A8501797856D102C57EBC2C112E943\n\
E83EEBC52D53EEC79138787AA83C7A\n\
96C3BC39055451552EC43C52EEED52\n\
EBBC43AAC5157AD3A93B87D45153D2\n\
D2C1542ABD07D03A86EAAB9552D6BA\n\
D05697C46D6BD6EC057C2AAD3ED142\n\
BC152B97B9787BB907D52843C17C7A\n\
A92BEA8380141442C13B843ED01792\n\
C6C6D46C6EC7ED547EC6C7ED56C56E"
    tab_str = string_main.split("\n")
    high_str = len(tab_str)
    w = len(tab_str[0])
    scale = 750 // high_str
    scale_w = 1500 // w
    scale = scale if scale_w > scale else scale_w
    color = bytes([255, 255, 255, 255])
    way = False
    start = (1,1)
    exit = (29,29)

    path = []
    path.append(start)
    for letter in path_str:
        x = path[-1][0]
        y = path[-1][1]
        if letter == "E":
            path.append((x + 1, y))
        if letter == "S":
            path.append((x, y+1))
        if letter == "W":
            path.append((x - 1, y))
        if letter == "N":
            path.append((x, y - 1))
    drrraw(mlx, mlx_pointer, window, image, tab_str, size_line, scale, image_address, start, exit, path, way, color)
    arguments = {
        'mlx': mlx,
        'mlx_ptr': mlx_pointer,
        'window': window,
        'draw': drrraw,
        'color': color,
        'my_way': way,
        'draw_args': (mlx, mlx_pointer, window, image, tab_str, size_line, scale, image_address, start, exit, path)
    }
    mlx.mlx_string_put(mlx_pointer, window, 50, 760, 0xFFFFFFFF, "Opis ")
    mlx.mlx_string_put(mlx_pointer, window, 50, 770, 0xFFFFFFFF, "Opis")

    mlx.mlx_key_hook(window, key_hooks, arguments)
    mlx.mlx_loop(mlx_pointer)


if __name__ == "__main__":
    main()

