import sys
from streamlit.web import cli as stcli

sys.argv = ["streamlit", "run", "./Python/app.py"]
sys.exit(stcli.main())  