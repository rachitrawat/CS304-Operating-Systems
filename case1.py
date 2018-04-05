import time
from random import randint
from threading import Thread, Lock, Event

mutex = Lock()
enterFlag = None


class BarberShop:
    waitingCustomers = []

    def __init__(self, barber, numberOfSeats):
        self.barber = barber
        self.numberOfSeats = numberOfSeats

    def openShop(self):
        print('Barber has opened the Barber Shop')
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
                print('Barber is sleeping')
                self.barber.sleep()
                print('Barber woke up')

    def enterBarberShop(self, customer):
        mutex.acquire()
        print('Customer-{0} has arrived'.format(customer))

        if len(self.waitingCustomers) == self.numberOfSeats:
            print('Barbershop is full, Customer-{0} has left'.format(customer))
            mutex.release()
        else:
            print('Barber is busy, Customer-{0} is waiting'.format(customer))
            self.waitingCustomers.append(c)
            mutex.release()
            self.barber.wakeUp()


class Barber:
    barberWorkingEvent = Event()

    def __init__(self, durationOfHaircut):
        self.durationOfHaircut = durationOfHaircut

    def sleep(self):
        self.barberWorkingEvent.wait()

    def wakeUp(self):
        # awaken the thread
        self.barberWorkingEvent.set()

    def cutHair(self, customer):
        # Set barber as busy
        self.barberWorkingEvent.clear()

        print('Barber is cutting Customer-{0} hair'.format(customer))

        time.sleep(self.durationOfHaircut)
        print('Customer-{0} haircut is complete'.format(customer))


def generate_random_number():
    while (True):
        global enterFlag
        enterFlag = randint(0, 10 ** 6) % 3
        time.sleep(1)


if __name__ == '__main__':
    durationOfHaircut = int(input("Enter haircut duration (P): "))
    numberOfSeats = int(input("Enter number of regular chairs (N) : "))

    # start random number generator thread
    rand_gen = Thread(target=generate_random_number)
    # allow main program to exit
    rand_gen.daemon = True
    # run thread
    rand_gen.start()

    # customer list
    customer = list(range(6))
    customer.reverse()

    barber = Barber(durationOfHaircut)
    barberShop = BarberShop(barber, numberOfSeats)
    barberShop.openShop()

    while (len(customer) > 0):
        time.sleep(1)
        if enterFlag == 0:
            c = customer.pop()
            # New customer enters the barbershop
            barberShop.enterBarberShop(c)
