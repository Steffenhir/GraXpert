from graxpert.astroimage import AstroImage
from numpy.testing import assert_array_almost_equal
import os
import numpy as np
import pytest
from astropy.io import fits
from xisf import XISF
from skimage import io, img_as_float32


array_mono = np.array([[[0],[0.5],[0],[0.25],[0],[0.25]],
                  [[0.5],[0],[0.5],[0.25],[0],[0.25]],
                  [[0],[0.5],[0],[0.25],[0],[0.25]],
                  [[0],[0.75],[0],[0.33],[0],[0.25]],
                  [[0],[0.1],[0.1],[0.1],[0],[0.25]]])

array_color = np.array([[[0,0,0],[0.25,0.5,0.25],[0,0,0],[0.25,0.25,0.25],[0,0,0],[0.25,0.25,0.25]],
                        [[0.25,0.5,0.25],[0,0,0],[0.25,0.5,0.25],[0.25,0.25,0.25],[0,0,0],[0.25,0.25,0.25]],
                        [[0,0,0],[0.25,0.5,0.25],[0,0,0],[0.25,0.25,0.25],[0,0,0],[0.25,0.25,0.25]],
                        [[0,0.1,0],[0.25,0.5,0.2],[0,0,0],[0.2,0.25,0.2],[0,0,0],[0.25,0.25,0.25]],
                        [[1.0,0,0],[0.35,0.6,0.25],[0.9,0.8,0],[0.9,0.25,0.95],[0,0,0],[0.25,0.25,0.25]]])

test_images_mono = ["mono_16bit.fits", "mono_16bit.xisf", "mono_16bit.tiff",
                    "mono_32bit.fits", "mono_32bit.xisf", "mono_32bit.tiff"]

test_images_color = ["color_16bit.fits", "color_16bit.xisf", "color_16bit.tiff",
                     "color_32bit.fits", "color_32bit.xisf", "color_32bit.tiff"]

file_types = ["16 bit Fits", "32 bit Fits", "16 bit Tiff", "32 bit Tiff", "16 bit XISF", "32 bit XISF"]


class DummyStretchOption:
    def get(self):
        return "30% Bg, 2 sigma"
    
class DummySaturationOption:
    def get(self):
        return 2.0



def test_set_from_array_mono():
    stretch = DummyStretchOption()
    saturation = DummySaturationOption()
    a = AstroImage(stretch,saturation)
    
    a.set_from_array(array_mono)
    assert_array_almost_equal(a.img_array, array_mono, decimal=5)
    assert a.width == 6
    assert a.height == 5  
    
def test_set_from_array_color():
    stretch = DummyStretchOption()
    saturation = DummySaturationOption()
    a = AstroImage(stretch,saturation)
    
    a.set_from_array(array_color)
    assert_array_almost_equal(a.img_array, array_color, decimal=5)
    assert a.width == 6
    assert a.height == 5
    


@pytest.mark.parametrize("img", test_images_mono)
def test_set_from_file_mono(img):
    stretch = DummyStretchOption()
    saturation = DummySaturationOption()
    a = AstroImage(stretch,saturation)
    
    a.set_from_file("./tests/test_images/" + img)
    assert_array_almost_equal(a.img_array, array_mono, decimal=5)
    assert a.width == 6
    assert a.height == 5
    
@pytest.mark.parametrize("img", test_images_color)
def test_set_from_file_color(img):
    stretch = DummyStretchOption()
    saturation = DummySaturationOption()
    a = AstroImage(stretch,saturation)
    
    a.set_from_file("./tests/test_images/" + img)
    assert_array_almost_equal(a.img_array, array_color, decimal=5)
    assert a.width == 6
    assert a.height == 5



def test_update_display_mono():
    stretch = DummyStretchOption()
    saturation = DummySaturationOption()
    a = AstroImage(stretch,saturation)
    
    a.set_from_array(array_mono)
    a.update_display()
    assert np.asarray(a.img_display).shape == (5,6)
    assert np.asarray(a.img_display_saturated).shape == (5,6)
    
def test_update_display_color():
    stretch = DummyStretchOption()
    saturation = DummySaturationOption()
    a = AstroImage(stretch,saturation)
    
    a.set_from_array(array_color)
    a.update_display()
    assert np.asarray(a.img_display).shape == (5,6,3)
    assert np.asarray(a.img_display_saturated).shape == (5,6,3)


@pytest.mark.parametrize("file_type", file_types)
def test_save_mono(tmp_path, file_type):
    stretch = DummyStretchOption()
    saturation = DummySaturationOption()
    a = AstroImage(stretch,saturation)
    
    a.set_from_file("./tests/test_images/mono_32bit.fits")
    file_ending = file_type[-4::].lower()
    file_dir = os.path.join(tmp_path, file_type + "." + file_ending)
    a.save(file_dir, file_type)
    
    if file_ending == "fits":
        hdul = fits.open(file_dir)
        img_array = hdul[0].data
        hdul.close()
    
    elif file_ending == "xisf":
        xisf = XISF(file_dir)
        img_array = xisf.read_image(0)
        
    else:
        img_array = io.imread(file_dir)
    
    if file_ending != "xisf":
        img_array = np.array([img_array])
        img_array = np.moveaxis(img_array, 0, -1)
        
    img_array = img_as_float32(img_array)    
    
    assert_array_almost_equal(array_mono, img_array, decimal=5)
    
@pytest.mark.parametrize("file_type", file_types)
def test_save_color(tmp_path, file_type):
    stretch = DummyStretchOption()
    saturation = DummySaturationOption()
    a = AstroImage(stretch,saturation)
    
    a.set_from_file("./tests/test_images/color_32bit.fits")
    file_ending = file_type[-4::].lower()
    file_dir = os.path.join(tmp_path, file_type + "." + file_ending)
    a.save(file_dir, file_type)
    
    if file_ending == "fits":
        hdul = fits.open(file_dir)
        img_array = hdul[0].data
        hdul.close()
        img_array = np.moveaxis(img_array,0,-1) 
    
    elif file_ending == "xisf":
        xisf = XISF(file_dir)
        img_array = xisf.read_image(0)
        
    else:
        img_array = io.imread(file_dir)
    
    img_array = img_as_float32(img_array)    
    
    assert_array_almost_equal(array_color, img_array, decimal=5)



@pytest.mark.parametrize("file_type", file_types)
def test_save_stretched_mono(tmp_path, file_type):
    stretch = DummyStretchOption()
    saturation = DummySaturationOption()
    a = AstroImage(stretch,saturation)
    
    a.set_from_file("./tests/test_images/mono_32bit.fits")
    file_ending = file_type[-4::].lower()
    file_dir = os.path.join(tmp_path, file_type + "." + file_ending)
    a.save_stretched(file_dir, file_type)
    
    if file_ending == "fits":
        hdul = fits.open(file_dir)
        img_array = hdul[0].data
        hdul.close()
    
    elif file_ending == "xisf":
        xisf = XISF(file_dir)
        img_array = xisf.read_image(0)
        
    else:
        img_array = io.imread(file_dir)
    
    if file_ending != "xisf":
        img_array = np.array([img_array])
        img_array = np.moveaxis(img_array, 0, -1)
        
    img_array = img_as_float32(img_array)
    
    assert array_mono.shape == img_array.shape
    
@pytest.mark.parametrize("file_type", file_types)
def test_save_stretched_color(tmp_path, file_type):
    stretch = DummyStretchOption()
    saturation = DummySaturationOption()
    a = AstroImage(stretch,saturation)
    
    a.set_from_file("./tests/test_images/color_32bit.fits")
    file_ending = file_type[-4::].lower()
    file_dir = os.path.join(tmp_path, file_type + "." + file_ending)
    a.save_stretched(file_dir, file_type)
    
    if file_ending == "fits":
        hdul = fits.open(file_dir)
        img_array = hdul[0].data
        hdul.close()
        img_array = np.moveaxis(img_array,0,-1) 
    
    elif file_ending == "xisf":
        xisf = XISF(file_dir)
        img_array = xisf.read_image(0)
        
    else:
        img_array = io.imread(file_dir)
    
    img_array = img_as_float32(img_array)    
    
    assert array_color.shape == img_array.shape

    