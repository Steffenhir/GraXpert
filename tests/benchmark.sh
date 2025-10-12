set -e

USEGPU=true
#GRAXPERT="python graxpert/main.py"
GRAXPERT="graxpert"

# export PYTHONPATH=.

echo "Running background extraction..."
time $GRAXPERT -cmd background-extraction -output /tmp/testout_bk -gpu $USEGPU tests/test_images/real_crummy.fits
echo "Running deconvolution (object)..."
time $GRAXPERT -cmd deconv-obj -output /tmp/testout_deconv -gpu $USEGPU /tmp/testout_bk.fits
echo "Running denoising..."
time $GRAXPERT -cmd denoising -output /tmp/testout_denoise -gpu $USEGPU /tmp/testout_deconv.fits