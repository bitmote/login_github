
class Desc(object):

    def __init__(self,name):
        self.name = name

    def __get__(self,instance,owner):
        print 'in get'
        print instance,owner
        return self.name

    def __set__(self, instance, value):
        print 'in set'
        self.name = value

    def __delete__(self, instance):
        print 'in delete'
        del self.name

class haha(object):
    a = Desc('aaaa')
    b = Desc('bbbb')




