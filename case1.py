import time
from random import randint
from threading import Thread, Lock, Event

mutex = Lock()


class BarberShop:
    waitingCustomers = []

    def __init__(self, barber, numberOfSeats):
        self.barber = barber
        self.numberOfSeats = numberOfSeats

    def openShop(self):
        print('{0} has opened the Barbershop!'.format(self.barber.name))
        workingThread = Thread(target=self.barberGoToWork)
        workingThread.start()

    def barberGoToWork(self):
        while True:
            mutex.acquire()

            if len(self.waitingCustomers) > 0:
                c = self.waitingCustomers[0]
                del self.waitingCustomers[0]
                mutex.release()
                self.barber.cutHair(c)
            else:
                mutex.release()
                print('{0} is sleeping...'.format(self.barber.name))
                self.barber.sleep()
                print('Customer-{0} has woken up {1}.'.format(self.waitingCustomers[0], self.barber.name))

    def enterBarberShop(self, customer):
        mutex.acquire()
        print('Customer-{0} has arrived.'.format(customer))
        # If there is no one in the barber chair
        if self.barber.barberChair == False:
            self.waitingCustomers.append(customer)
            mutex.release()
            self.barber.wakeUp()
        # No seats in waiting room
        elif len(self.waitingCustomers) == self.numberOfSeats:
            print('Barbershop is full, Customer-{0} has left.'.format(customer))
            mutex.release()
        # If someone is in the barber chair and there are seats left in the waiting room
        else:
            print('{0} is busy, Customer-{1} is waiting on chair-{2}.'.format(self.barber.name, customer,
                                                                              len(self.waitingCustomers)))
            self.waitingCustomers.append(customer)
            mutex.release()
            self.barber.wakeUp()


class Barber:
    barberWorkingEvent = Event()

    def __init__(self, name, durationOfHaircut):
        self.name = name
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

        print('Customer-{0} is sitting in the barber chair.'.format(customer))
        print('{0} is cutting Customer-{1}\'s hair.'.format(self.name, customer))
        self.barberChair = True
        time.sleep(self.durationOfHaircut)
        print('Customer-{0}\'s haircut is complete.'.format(customer))
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
    barberShop = BarberShop(SweenyTodd, numberOfSeats)
    barberShop.openShop()

    # start random number generator thread
    rand_gen = Thread(target=generate_random_number)
    # allow main program to exit
    rand_gen.daemon = True
    # run thread
    rand_gen.start()
