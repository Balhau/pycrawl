import random
#Bunch of utility methods ip related
class IpUtils:

    @staticmethod
    def randomIPV4():
        blocks = []
        for i in range(0,4):
            blocks.append(str(random.randint(1,255)))
        return ".".join(blocks)
