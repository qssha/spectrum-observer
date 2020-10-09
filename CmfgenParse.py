import numpy as np


def spectr_input(file_name):
    """
    Parse multicolumn fortran data file from CMFGEN
    :param file_name: CMFGEN model filename
    :return: np.array(wave, f   lux)
    """
    input_file = open(file_name,'r')
    freq_flux_list = []
    all_lines = input_file.readlines()

    try:
        [parse_line(line, freq_flux_list) for line in all_lines]
        xfreq = np.array(freq_flux_list[0:len(freq_flux_list) / 2], dtype=np.float64)
        yint = np.array(freq_flux_list[len(freq_flux_list) / 2:], dtype=np.float64)

    except ValueError as exception:
        print("Value Error: " + exception.message)
        freq_flux_list = []

        [parse_line_eval(line,freq_flux_list) for line in all_lines]
        xfreq = np.array(freq_flux_list[0:len(freq_flux_list) / 2], dtype=np.float64)
        yint = np.array(freq_flux_list[len(freq_flux_list) / 2:], dtype=np.float64)


    xfreq = (2.99702547e3) / xfreq
    yint = (yint * 3 * 10**-5) / (xfreq * xfreq)
    spectum_model = np.transpose([xfreq, yint])

    return spectum_model


def parse_line(line, freq_flux_list):
    """
    Split and parse line
    :param line: line to parse
    :param freq_flux_list:  list with all items
    """
    line = line.rstrip().split()
    if line == [] or "." not in line[0]:
        return
    elif "E" not in line[0]:
        freq_flux_list.extend(list(map(lambda x: eval(x),line)))
    else:
        freq_flux_list.extend(line)


def parse_line_eval(line, freq_flux_list):
    """
    Safe(Eval) split and parse line
    Example: '1-303' can't be cast to float
    :param line: line to parse
    :param freq_flux_list:  list with all items
    """
    line = line.rstrip().split()
    if line == [] or "." not in line[0]:
        return
    else:
        freq_flux_list.extend(list(map(lambda x: eval(x),line)))
