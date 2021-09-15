py -m venv venv
.\venv\Scripts\Activate.ps1
pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio===0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
py -m pip install -r requirements.txt
PAUSE