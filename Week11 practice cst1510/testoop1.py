#in class practice with tutor
class Student:

    def __init__(self,MISIS,stdName,mark):
        self.__MISIS = MISIS
        self.__stdName = stdName
        self.__mark = mark
    
    def __str__(self):
        return f'Student info: {self.__MISIS}, {self.__stdName} and {self.__mark}'
    def resul(self):
        if self.__mark > 40:
            print(f"{self.__stdName} is passed")
        else:
            print("not passed")

std1 = Student("M0101", "Ali", 79)
std2 = Student("M123", "Mohammad",80)

print(std1)
print(std2) 
std2.resul()
