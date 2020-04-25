import numpy as np
from matplotlib import pyplot as plt
import os

known_types = ['.img']

def get_dtype(index):
    dtype_map = [np.uint8,           # unsigned byte
         np.int16,                   # 16-bit int
         np.int32,                   # 32-bit int
         np.float32,                 # 32-bit float
         np.float64,                 # 64-bit float
         np.complex64,               # 2x32-bit complex
         np.complex128,              # 2x64-bit complex
         np.uint16,                 # 16-bit unsigned int
         np.uint32,                 # 32-bit unsigned int
         np.int64,                  # 64-bit int
         np.uint64]                 # 64-bit unsigned int
    return(dtype_map[index-1])

class crism_img(object):
    """
    header = path to headerfile
    metadata = dictonary of the headerfile
    img_path = path to the img file
    """

    def __init__(self, headerfile, path = ''):
        """
        headerfile: name of header + path, ex "name.hdr"
        path: defaults to empty string, path to file, ex 'users/username/Desktop/'
        """
        self.header = headerfile
        self.metadata = self.hdr_to_dict(headerfile)

        ext = self.metadata['cat input files'][self.metadata['cat input files'].find('.'):]
        if ext.lower() not in known_types:
            raise RuntimeError('unknown file extention, known extentions include: '+str(known_types))

        self.img_path = path + self.metadata['cat input files'].strip(ext).strip(' ') + self.metadata['cat history'].strip(' ') + ext.lower()
        if not os.path.isfile(self.img_path):
            raise RuntimeError('path to binary file not found')

        self.samples = self.metadata['samples']
        self.lines = self.metadata['lines']
        self.bands = self.metadata['bands']
        self.shape = (self.lines, self.bands, self.samples,)

        self.dtype = get_dtype(self.metadata['data type'])

        datahold = np.fromfile(open(self.img_path,'rb'), self.dtype)
        self.data = datahold.reshape(self.shape)


    def hdr_to_dict(self, headerfile):
        x = open(headerfile,"r", encoding="utf-8")
        md = x.readlines()

        metadata = {}
        metadata['type'] = md[0].strip('\n')
        i = 1
        while i < len(md):
            eq_index = md[i].find('=')
            end = md[i].find('\n')
            startcol = md[i].find('{')
            if  startcol == -1:
                if md[i][eq_index+1: end].strip(' ').isdigit():
                    metadata[md[i][0:eq_index-1]] = int(md[i][eq_index+1: end])
                else:
                    try:
                        metadata[md[i][0:eq_index-1]] = float(md[i][eq_index+1: end])
                    except ValueError:
                        metadata[md[i][0:eq_index-1]] = md[i][eq_index+1: end]
            else:
                ls = ""
                startrow = i
                while md[i].find('}') == -1:
                    ls+= md[i].strip('\n')
                    i += 1
                ls+= md[i].strip('\n')
                metadata[md[startrow][:eq_index-1]] = ls[startcol: ]
            i += 1
        return metadata

    def image_band(self, band, ax = None, c = 'gray'):
        """
        band: an int of of the band you want to plot
        ax: axes to plot on
        c: colormap to use, from mpl color maps
        """
        if not band in range(self.bands):
            raise IndexError('band not in range')
        if type(band) != int:
            raise TypeError('band is not an int')

        if ax == None:
            plt.imshow(self.data[:,band, :], c)
        else:
            ax.imshow(self.data[:,band,:], c)

        return None

    def image_bands(self, bands, ax = None, multiplier = 5):
        """
        plots 3 bands as if they were rgb
        bands: tuple or array or len = 3, of bands to plot
        ax: axes to plot on
        multiplier: if the image is dark, use multiplier to lighten the colors
        """
        if len(bands) != 3:
            raise IndexError('there should be 3 bands')
        for band in bands:
            if not band in range(self.bands):
                raise IndexError('band not in range')
            if type(band) != int:
                raise TypeError('band is not an int')

        toplot = np.array([self.data[:, bands[0], :].T, self.data[:, bands[1], :].T, self.data[:, bands[2], :].T], dtype = np.float32).T

        if ax == None:
            im = plt.imshow(toplot * multiplier)
            plt.colorbar(im, orientation='vertical')
        else:
            im = ax.imshow(toplot * multiplier)
            ax.colorbar(im, orientation='vertical')

        return None

    def get_band(self, sample, line):
        """
        returns: an array of the band values coresponting to a pixel

        sample: sample
        line: line
        """
        #i kinda dont like this function
        return self.data[sample, :, line]
