set -e
python3.10 -m venv venv
source ./venv/bin/activate
#CMAKE_ARGS="-D LLAMA_HIPBLAS=ON HSA_OVERRIDE_GFX_VERSION=10.3.0 -D CMAKE_C_COMPILER=/opt/rocm/bin/amdclang -D CMAKE_CXX_COMPILER=/opt/rocm/bin/amdclang++ -D CMAKE_PREFIX_PATH=/opt/rocm -D AMDGPU_TARGETS=gfx1100" FORCE_CMAKE=1 pip install llama-cpp-python
pip install --extra-index-url https://download.pytorch.org/whl/rocm5.7 torch==2.2.1+rocm5.7 torchaudio==2.2.1+rocm5.7 torchvision==0.17.1+rocm5.7
pip install whisper-mic==1.4.2 sentencepiece inquirerpy TTS pygame pysbd
#pip install -r requirements_rocm.txt
read -sn 1 -p "Press any key to continue.."