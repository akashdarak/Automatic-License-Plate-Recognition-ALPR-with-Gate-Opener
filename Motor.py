import RPi.GPIO as GPIO
from time import sleep
file1 = open("database.txt", "r")
file2 = open("database_4.txt", "r")
list1 = file1.readlines()
list2 = file2.readlines()
for i in list1:
    for j in list2:
        if  i==j:
            print(i)
            GPIO.setmode(GPIO.BOARD)
 
            Motor1A = 16
            Motor1B = 18
            Motor1E = 22
 
            GPIO.setup(Motor1A,GPIO.OUT)
            GPIO.setup(Motor1B,GPIO.OUT)
            GPIO.setup(Motor1E,GPIO.OUT)
 
            print "Turning motor on"
            GPIO.output(Motor1A,GPIO.HIGH)
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor1E,GPIO.HIGH)
 
            sleep(2)
 
            print "Stopping motor"
            GPIO.output(Motor1E,GPIO.LOW)
 
            GPIO.cleanup()

file1.close()
file2.close()

