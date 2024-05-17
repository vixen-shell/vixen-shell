from . import content


@content.add("action")
def hello_world():
    print("Hello World !!!")
