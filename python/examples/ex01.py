language: str = "en_US"


class Vai:
    def foi(self, s):
        return s == "agora vai"


client = Vai()
a = 10
if client.is_enabled("feature 1"):
    print("hello world")
else:
    print("Hi world! 1")
    print("Hi world! 2")
    print("Hi world! 3")
    if client.is_enabled("feature 2"):
        a = 5
    else:
        a = 3
        if not client.is_enabled("feature 3"):
            print("The feature 3 is implemented")
print("The result is:", a)


def show_info():
    if client.is_enabled("feature 1") and client.is_enabled("feature 2"):
        print("Info feature 1 e 2!!!")
    else:
        print("Info default")
