py -m venv venv
.\venv\Scripts\Activate.ps1
pip install torch==1.7.1+cu101 -f https://download.pytorch.org/whl/torch_stable.html
py -m pip install -r requirements.txt
PAUSE