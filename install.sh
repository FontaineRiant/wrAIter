python -m venv venv
source ./venv/Scripts/activate
pip install torch==1.7.1+cu101 -f https://download.pytorch.org/whl/torch_stable.html
pip install -r requirements.txt
read -sn 1 -p "Press any key to continue.."