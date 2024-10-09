set -e
python -m venv venv
source ./venv/bin/activate
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install whisper-mic==1.4.2 sentencepiece inquirerpy coqui-tts pygame pysbd accelerate diffusers
pip install bitsandbytes
read -sn 1 -p "Press any key to continue.."
