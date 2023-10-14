<p align="center">
<img src="https://github.com/Steffenhir/GraXpert/blob/main/img/GraXpert_LOGO_Hauptvariante.png" width="500"/>
</p>

GraXpert is an astronomical image processing program for extracting and removing
gradients in the background of your astrophotos.

Original                     |  Gradients removed
:-------------------------:|:-------------------------:
![Before](https://www.graxpert.com/wp-content/uploads/2022/04/M65before-2048x1100.jpg)   |  ![After](https://www.graxpert.com/wp-content/uploads/2022/04/M65after-2048x1097.jpg)
![Before](https://www.graxpert.com/wp-content/uploads/2022/04/M42before-2048x1101.jpg)   |  ![After](https://www.graxpert.com/wp-content/uploads/2022/04/M42after-2048x1100.jpg)

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



