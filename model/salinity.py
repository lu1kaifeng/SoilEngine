salinity = {
    (0,2):('N','Nonsaline','None'),
    (2,4):('W','Weak','Very Slight'),
    (4,8):('M','Moderate','Slight'),
    (8,16):('S','Strong','Moderate'),
    (16,-1):('V','Very Strong','Severe')
}

def get_salinity(sal_val):
    for k,v in salinity.items():
        if sal_val > k[0]:
            if sal_val <= k[1]:
                return v
            elif k[1]==-1:
                return v
    return None
