import os
import shutil

def clear():
    for root, dirs, files in os.walk(os.getcwd()):
        for dir in dirs:
            if '__pycache__' in dir:
                try:
                    shutil.rmtree(
                        dir
                    )
                except:
                    pass

clear()