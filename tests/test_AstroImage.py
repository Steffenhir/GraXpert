from graxpert.astroimage import AstroImage
from numpy.testing import assert_array_almost_equal
import numpy as np
import pytest



array_mono = np.array([[[0],[0.5],[0]],
                  [[0.5],[0],[0.5]],
                  [[0],[0.5],[0]]])

array_color = np.array([[[0,0,0],[0.25,0.5,0.25],[0,0,0]],
                        [[0.25,0.5,0.25],[0,0,0],[0.25,0.5,0.25]],
                        [[0,0,0],[0.25,0.5,0.25],[0,0,0]]])

class DummyStretchOption:
    def get(self):
        return "No Stretch"

def test_set_from_array():
    stretch = DummyStretchOption()
    a = AstroImage(stretch)
    

    a.set_from_array(array_mono)
    assert_array_almost_equal(a.img_array, array_mono)
    assert a.width == 3
    assert a.height == 3  
    
    
    a.set_from_array(array_color)
    assert_array_almost_equal(a.img_array, array_color)
    assert a.width == 3
    assert a.height == 3
    

def test_set_from_file():
    stretch = DummyStretchOption()
    a = AstroImage(stretch)
    
    a.set_from_file("./tests/mono_fits.fits")
    assert_array_almost_equal(a.img_array, array_mono)
    assert a.width == 3
    assert a.height == 3
    
    a.set_from_file("./tests/color_fits.fits")
    assert_array_almost_equal(a.img_array, array_color)
    assert a.width == 3
    assert a.height == 3 
    
    a.set_from_file("./tests/mono_tiff.tiff")
    assert_array_almost_equal(a.img_array, array_mono)
    assert a.width == 3
    assert a.height == 3 
    
    a.set_from_file("./tests/color_tiff.tiff")
    assert_array_almost_equal(a.img_array, array_color)
    assert a.width == 3
    assert a.height == 3 
    
    
