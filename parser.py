#functions which parse h5f or xls files

import h5py
import pandas as pd

base = '/home/hyunbinl/smartgrid/'

def parse_h5f():
    """
    @return     a matrix dataset with shape (4629, 25201)
    """

    dir = base+'cer_parsed_data/Consumer_data_new.h5'
    h5f = h5py.File(dir,'r')
    retval = h5f['dataset'][...]
    h5f.close()
    return retval

def parse_type():
    """
    1 = residential
    2 = SME
    3 = others

    @return     a dictionary for (user, category) as (key,value)
    """

    dir = base+'cer_original/CER Electricity Revised March 2012/SME and Residential allocations.xlsx'
    xl = pd.ExcelFile(dir)
    df = xl.parse('Sheet1')
    return dict(zip(df['ID'],df['Code']))