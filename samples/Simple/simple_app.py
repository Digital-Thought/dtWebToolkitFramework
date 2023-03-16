import sys
import os

sys.path.append(os.path.abspath('../../src'))

from dtWebToolkitFramework.app import AbstractWebToolkit


class SimpleDevApp(AbstractWebToolkit):

    def get_utils(self):
        return ['my_tool']


if __name__ == "__main__":
    os.environ['DEV_MODE'] = "True"
    SimpleDevApp(description="Simple App showing paths in Dev Mode", version="1.0", short_name="simple_dev_app",
                 full_name="Simple Development Application").run()
