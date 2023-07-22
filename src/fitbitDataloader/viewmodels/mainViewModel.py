from datetime import datetime

class MainViewModel(object):
    """
    The view model is the object doing the liaison between
    the GUI and the model
    """
    def __init__(self):
        super().__init__()
        todaysDate = datetime.today().strftime('%Y-%m-%d')
        tod = f"Today is : {todaysDate}"