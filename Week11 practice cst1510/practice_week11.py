#class practice for lab
class Animal:
    def __init__(self, name, age):
        self.__name = name
        self.__age = age
        
    def get_name(self):
        return self.__name
    
    def get_age(self):
        return self.__age
    
    def __str__(self):
        return f"The Animal name is: {self.__name} and he is: {self.__age} years old"


class Cat(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)
        self.__breed = breed

    def hunts(self):
        return "It is true cats are hunting"
    
    def __str__(self):
        return super().__str__() + f" Breed: {self.__breed}. " + self.hunts()


class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)
        self.__breed = breed

    def barks(self):
        return "Dogs are barking!"
    
    def __str__(self):
        return super().__str__() + f" Breed: {self.__breed}. " + self.barks()


def main():
    vuk = Dog("Vuk", 3, "Bulldog")
    princess = Dog("Princess", 2, "Poodle")
    bark = Dog("Bark", 4, "Husky")
    piko = Cat("Piko", 2, "Ragdoll")
    poko = Cat("Poko", 1, "Ragdoll")

    dogs_list = [vuk, princess, bark]
    cats_list = [piko, poko]
    animals = dogs_list + cats_list

    for i in animals:
        print(i)
        if isinstance(i, Cat):
            print(i.hunts())
        elif isinstance(i, Dog):
            print(i.barks())


if __name__ == "__main__":
    main()