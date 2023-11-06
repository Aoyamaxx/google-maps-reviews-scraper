from rijksdriehoek import rijksdriehoek


def convert_cor(x, y):

    rd = rijksdriehoek.Rijksdriehoek()
    rd.rd_x = x
    rd.rd_y = y
    lat, lon = rd.to_wgs()
    
    return lat, lon