import serial

def checksum(command):
    sum = 0
    for character in command:
        sum += ord(character)
        #print(f"Character {character} has value {str(hex(ord(character)))}")
    sum = sum % 256
    cs = str(hex(sum))[2:].upper()
    print(f"The checksum of command {command} is {cs}")
    return cs


with serial.Serial(port='COM3', baudrate=9600, timeout=3, rtscts=False, dsrdtr=False) as ser:
    #command = '>01AA2\r'
    rawCommand = command = '04B'
    cs = checksum(rawCommand)
    command = '>' + rawCommand + cs + '\r'

    ser.write(command.encode())
    result = ser.read_until(b'\r')
    print(result)

#Left to right as viewed from 