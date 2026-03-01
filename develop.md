<p align="center">
  <img src="resources/img/pincab_manager.png" alt="Pincab Manager" width="480"/>
</p>

# pincab-manager

Project to manage my Pincab

## Packaging

```bash
raw_version=$(head -n 1 CHANGELOG | awk '{print $1}')
version="${raw_version#R}"
python3 -m PyInstaller --name "pincab-manager" --onefile --noconsole --icon=resources/img/pincab.ico pincab-manager.py --add-data "libvlccore.dll:." --add-data "libvlc.dll:." --add-data "plugins:plugins" --add-data "resources:resources" --add-data "binaries:binaries" --add-data "CHANGELOG:." ; rm -Rf build ; rm pincab-manager.spec
```

## Install

Install :
- **python3**
- **TKINTER** with following commands:
```bash
sudo apt update
sudo apt install python3-tk
```
- **requirements** using **pip3**:
```bash
pip3 install -r requirements
```

## Testing locally

To analyze your code, use command:

```bash
find . -iname "*.py" -not -path "./.venv/*" | xargs python3 -m pylint
```

## Usage

Use the environment variable PINCAB_MANAGER_PATH to define a specific path to work.

```bash
export PINCAB_MANAGER_PATH=P:\\
export PINCAB_MANAGER_PATH=D:\\pincab\\data
```

To start the application, type following command:

```bash
python3 pincab-manager.py
```

## To update DOF Config

- Go to the website http://configtool.vpuniverse.com/ 
- Click on **Generate Config**
- Move generated files in **Z:/data/configs/pincab-manager/database/pincab11/common/32 bits/dof/DirectOutput/Config**
- Copy content from **Z:/data/configs/pincab-manager/database/pincab11/common/32 bits/dof/DirectOutput/Config/directoutputconfig8.ini** in **Z:/data/configs/pincab-manager/database/pincab11/common/32 bits/dof/DirectOutput/Config/directoutputconfig.ini** 
- Move generated files in **Z:/data/configs/pincab-manager/database/pincab11/common/64 bits/dof/DirectOutput/Config**
- Copy content from **Z:/data/configs/pincab-manager/database/pincab11/common/64 bits/dof/DirectOutput/Config/directoutputconfig8.ini** in **Z:/data/configs/pincab-manager/database/pincab11/common/64 bits/dof/DirectOutput/Config/directoutputconfig.ini** 
- Update project using **git add**, **git commit** and **git push**
- From the pincab, update the project using **git pull** then install **Configs files / DirectOuput / 32 Bits** and **Configs files / DirectOuput / 64 Bits**
- Execute in **Admin Mode** the executable **C:\DirectOutput\RegisterDirectOutputComObject.exe**

## To add a table for any emulator

**N.B.**: For the emulator **Visual Pinball X**, you can use the command **"<visual_pinball_exe>" -Minimized -ExtractVBS "<vpx_file_path>"** to generate the script where you can extract the rom's name in the variable **cGameName** and the videos path in the variable **cPuPPack** (or **cGameName** if this variable doesn't exist)

For example: **"c:\vPinball\VisualPinball\VPinballX10_7_3_32bit.exe" -Minimized -ExtractVBS "Z:\tables\Visual Pinball X\Gardiens de la galaxie\2.1.0\emulator\Tables\Gardiens de la galaxie.vpx"**

**N.B.**: For the emulator **Future Pinball**:
- the tables containing PuP-Pack are identified by **PinEvent**. **Z:\configs\32 bits\future_pinball\vPinball\FuturePinball** is retrieved from https://vpuniverse.com/files/file/14807-future-pinball-and-bam-essentials-all-in-one-complete/. 
- disable the option use_RayCast_Shadows from the script in the file .fpt to override
- by option Q, set table X and z to 0.0, scale Z to 1.500 and angle rotation to 0.00 deg
