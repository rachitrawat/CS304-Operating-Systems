import time
from random import randint
from threading import Thread, Lock, Event

mutex1 = Lock()
mutex2 = Lock()


class BarberShop:
    waitingCustomers = []

    def __init__(self, barber, barber2, numberOfSeats):
        self.barber = barber
        self.barber2 = barber2
        self.numberOfSeats = numberOfSeats

    def openShop(self):
        print('{0} has opened the Barbershop!'.format(self.barber.name))
        workingThread = Thread(target=self.barberGoToWork, args=(self.barber, mutex1))
        workingThread.start()
        workingThread2 = Thread(target=self.barberGoToWork, args=(self.barber2, mutex2))
        workingThread2.start()

    def barberGoToWork(self, barber, mutex):
        while True:
            mutex.acquire()

            if len(self.waitingCustomers) > 0:
                c = self.waitingCustomers[0]
                del self.waitingCustomers[0]
                mutex.release()
                barber.cutHair(c)
            else:
                mutex.release()
                print('{0} is sleeping...'.format(barber.name))
                barber.sleep()
                print('Customer-{0} has woken up {1}.'.format(self.waitingCustomers[0], barber.name))

    def enterBarberShop(self, customer):

        # If there is no one in the barber1 chair, SET barber = barber1
        if self.barber.barberChair == False:
            mutex1.acquire()
            mutex = mutex1
            barber = self.barber
        # If there is no one in the barber2 chair, SET barber = barber2
        elif self.barber2.barberChair == False:
            mutex2.acquire()
            mutex = mutex2
            barber = self.barber2
        # If both barber are busy, set barber = barber1
        else:
            mutex1.acquire()
            mutex = mutex1
            barber = self.barber

        # If no one is sitting on barber chair
        if barber.barberChair == False:
            self.waitingCustomers.append(customer)
            mutex.release()
            barber.wakeUp()
        # No seats in waiting room
        elif len(self.waitingCustomers) == self.numberOfSeats:
            print('Barbershop is full, Customer-{0} has left.'.format(customer))
            mutex.release()
        # If someone is in the barber chair and there are seats left in the waiting room
        else:
            print('Both barbers are busy, Customer-{1} is waiting on chair-{2}.'.format(barber.name, customer,
                                                                                        len(self.waitingCustomers)))
            self.waitingCustomers.append(customer)
            mutex.release()
            barber.wakeUp()


class Barber:

    def __init__(self, name, durationOfHaircut):
        self.name = name
        self.barberWorkingEvent = Event()
        self.durationOfHaircut = durationOfHaircut
        self.barberChair = False  # Assigns barber chair as occupied (True) or unoccupied (False)

    def sleep(self):
        self.barberWorkingEvent.wait()

    def wakeUp(self):
        # awaken the thread
        self.barberWorkingEvent.set()

    def cutHair(self, customer):
        # Set barber as busy
        self.barberWorkingEvent.clear()

        print('Customer-{0} is sitting in the {1} chair.'.format(customer, self.name))
        print('{0} is cutting Customer-{1}\'s hair.'.format(self.name, customer))
        self.barberChair = True
        time.sleep(self.durationOfHaircut)
        print('Customer-{0}\'s haircut is completed by {1}.'.format(customer, self.name))
        self.barberChair = False


def generate_random_number():
    while len(customers) > 0:
        if randint(0, 10 ** 6) % 3 == 0:
            # New customer enters the barbershop
            barberShop.enterBarberShop(customers.pop())
        time.sleep(1)


if __name__ == '__main__':
    durationOfHaircut = int(input("Enter haircut duration (P): "))
    numberOfSeats = int(input("Enter number of regular chairs (N) : "))

    # customer list
    customers = list(range(6))
    customers.reverse()

    SweenyTodd = Barber('Sweeny Todd', durationOfHaircut)
    DavyCollins = Barber('Davy Collins', durationOfHaircut)

    barberShop = BarberShop(SweenyTodd, DavyCollins, numberOfSeats)
    barberShop.openShop()

    # start random number generator thread
    rand_gen = Thread(target=generate_random_number)
    # allow main program to exit
    rand_gen.daemon = True
    # run thread
    rand_gen.start()
