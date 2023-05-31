from setuptools import setup, find_packages

def findVersion(strPath:str) -> str:
    """
    Description:
    =================================================
    Find the version of this module.

    Args:
    ==========================================================================
    - strPath:  pytpe: str, the path of the python code file that has the version

    Return:
    =================================================================
    - rtype: str, the fetched version
    """
    strVersion = "1.0.0"
    with open(strPath, "r", encoding="utf-8") as oReader:
        for strLine in oReader.readlines():
            if "__version__" in strLine:
                strVersion = strLine.split("=")[1].strip().replace("\"", "")
                break
            # End of if-condition
        # End of for-loop
    # End of with-block

    return strVersion
# End of findVersion 

def main():
    setup(name = "EncoderConnector",
        description = "This module can obtain status of encoder via socket.",
        version = findVersion("./EncoderConnector/__init__.py"),
        author = "HONG-CING HUANG",
        py_modules=["EncoderConnector/myEncoderConnector", 
                    "EncoderConnector/myEncoderReader",
                    "EncoderConnector/__init__"],
        packages=find_packages())
# End of main

if "__main__" == __name__:
    main()
# End of if-condition