from pyfiglet import Figlet
from colorama import Fore, Style, init
from Functions import *
from Calculations import *



init(autoreset=True)


def opening_script():
    f = Figlet(font='doom')
    print(Fore.YELLOW + "-" * 35)

    startup_checks()
    print("\n")

    print(Fore.YELLOW + f.renderText("ObliviScan "))
    print(Fore.YELLOW + "A drone detection and tracking program by Josh Perryman(BCS Hons Cyber Security)")
    print(Fore.YELLOW + "This program can be use to detect the presence of Wifi enabled drones by using a machine learning model to predict activity based on their RF signatures")
    print(Fore.YELLOW + "Once a drone has been detected an AI detection module will open a view from the camera and track the drone as it moves\n")
        
def main():


    f = Figlet(font='doom')

    try:
        while True:
            print(Fore.YELLOW + "-" * 35)
            print(Fore.YELLOW + "|" + Fore.GREEN + " Run Detect and Track        [1] " + Fore.YELLOW + "|" + Style.RESET_ALL)
            print(Fore.YELLOW + "-" * 35)
            print(Fore.YELLOW + "|" + Fore.GREEN + " Exit                        [2] " + Fore.YELLOW + "|" + Style.RESET_ALL)
            print(Fore.YELLOW + "-" * 35)

            option = input(Fore.YELLOW + "|" + Fore.GREEN + " Choose an option: ")
            print(Fore.YELLOW + "-" * 35)

            try:
                option = int(option)
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a valid number.")
                continue

            if option == 1:
                print(Fore.YELLOW + "|" + Fore.GREEN + "Running drone detection")
                try:
                    print(Fore.YELLOW + "-" * 35)
                    while True:
                        detect_and_track()
                except KeyboardInterrupt:
                    print(Fore.RED + "\nScan Stopped")

            elif option == 2:
                print(Fore.YELLOW + f.renderText("Exiting"))
                quit() 
            
            else:
                print("Select an option")

    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
        exit()


if __name__ == "__main__":
    opening_script()
    main()
