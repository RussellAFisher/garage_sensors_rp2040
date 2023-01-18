# Garage Sensors using [Adafruit Feather RP2040](https://www.adafruit.com/product/4884)
### RP2040 based system for multiple sensors, relayed back to house using [LoRa](https://www.adafruit.com/product/3231)

This project started as a way to collect outdoor temp/humidity data. The best spot for sensors was on the North side of my detached garage to avoid direct sun but then I had to solve getting the data back to my house and powering the project.

To get the data back to my house I went with a LoRa radio transmitter for reliability as WiFi in the garage is weak enough to drop sporadically but I am hoping to run ethernet to the garage at some point and would switch to hardwired ethernet connection.

The garage had power but it was isolated to the South wall, I fixed this by running conduit up and over the door (from the existing wall mounted box for the lights/outlet) and placing new outlet boxes evenly on the East wall. Ultimately I decided to place the sensor box directly behind the door as the space was otherwise wasted.

I chose to run ethernet data/power wire for the outdoor sensors using an [Adafruit I2C extender/active terminator](https://www.adafruit.com/product/4756). The outdoor sensors include a [temp/humidity sensor](https://www.adafruit.com/product/4566) as well as an [air quality sensor](https://www.adafruit.com/product/4632).

Once the initial system was setup I added an additional temp/humidity sensor in the garage because...why not? I chose to use a different sensor ([SHT40](https://www.adafruit.com/product/4885)) to avoid I2C address conflicts with the outdoor sensors. In addition to the garage temp sensor I wired in a magnetic contact sensor next to the frame of the garage door allowing me to get notifications on my phone as to the current state of the door without needing to get a whole new smart garage door opener.

The above general setup was left in a generic hobby box sitting on a shelf for 6 months before I decided to rebuild the entire project around a 3D printed enclosure specifically for this project. The images in this repo show both the 3D modeled enclosure as well as the final project mounted securely to the wall. 

After creating the enclosure I decided to 3D print a rain gauge. The rain gauge is largely based on [this design by DusanJ](https://www.printables.com/model/130513-rain-gauge) but I again used a [magnetic contact switch](https://www.adafruit.com/product/375) as a robust/waterproof solution. To accomodate the rain gauge I simply drilled two holes in the side of my enclosure and added panel mount banana jacks which make the entire setup easy to take down for the winter.

The last thing that I added was an indication LED on the side of the garage. There were existing holes in the cinderblock (not sure what for) that perfectly fit an LED so I wired one inline with a resistor and pushed it 3/4 of the way through. It is protected from the elements being recessed and makes a nice indication of if the garage door is open or not with a quick glance from the house.

All of the sensor data that is sent to the house is collected by a Raspberry Pi system that is running a small python application that pushes the data to a Home Assistant instance to save to a DB or trigger automations.

