python -m venv venv
source ./venv/Scripts/activate
pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio===0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
pip install -r requirements.txt
read -sn 1 -p "Press any key to continue.."