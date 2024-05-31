from . import content


@content.add_handler("action")
def hello_world():
    print("Hello World !!!")
