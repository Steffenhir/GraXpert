<p align="center">
<img src="https://github.com/Steffenhir/GraXpert/blob/main/img/GraXpert_LOGO_Hauptvariante.png" width="500"/>
</p>

GraXpert is an astronomical image processing program for extracting and removing
gradients in the background of your astrophotos.

Original                     |  Gradients removed
:-------------------------:|:-------------------------:
![Original](https://github.com/Steffenhir/GraXpert/blob/main/img/LDN1235_original.jpg)   |  ![Gradients removed](https://github.com/Steffenhir/GraXpert/blob/main/img/LDN1235_processed.jpg)
![Original](https://github.com/Steffenhir/GraXpert/blob/main/img/NGC7000_original.jpg)   |  ![Gradients removed](https://github.com/Steffenhir/GraXpert/blob/main/img/NGC7000_processed.jpg)

**Homepage:** [https://www.graxpert.com](https://www.graxpert.com)  
**Manual:** [https://www.graxpert.com/daten/graXpert_manual_EN.pdf](https://www.graxpert.com/daten/graXpert_manual_EN.pdf)  
**Download:** [https://github.com/Steffenhir/GraXpert/releases/latest](https://github.com/Steffenhir/GraXpert/releases/latest)


## Installation for Developers
Clone repository
```
git clone https://github.com/Steffenhir/GraXpert
cd graxpert
```

Create new venv and install required packages
```
conda create --name graxpert python=3.10
conda activate graxpert
conda install --file requirements.txt
```

Starting from source
```
python graxpert/gui.py
```



