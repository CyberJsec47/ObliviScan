## Drone Detector

--- 


#### The goal of this project is to incorporate ML and AI with an embedded system to detect the presence of a drone then to use infrared sensoring to locate the drone.<br> 


#### The working idea of this project will be the following

- **Use SDR to monitor the spectrum used by drone, 2.4GHz**
- **Use a trained ML model to detect a drone from its RF signature**
- **Swap program to an IR camera which uses AI object tracking to locate the drone**

##### Once a drone has been detected and located the camera will continue to track it untill stopped

---
### Equipment

- Raspberry Pi 5 4Gb
- Raspberry Pi AI HAT+ 16tops with Hailo chip
- HackRF One and ANT500 antenna
- Raspberry Pi camera module 3 noIR
- Waveshare 4.3" touch screen
- Wireless mini keyboard 

--- 

### Development phases

#### Phase 1:

- Collecting drone RF data **Completed**
- Collecting RF background noise **Completed**
- Train and evaluate ML models for performance **Completed**
- Test with live drone **Completed**

#### Phase 2:

- Set up Ai HAT+ and camera module **Completed**
- Setup and test object detection with YOLOv8 or latest **Completed** 
- Collect IR images of drones **Completed**
- Label images and train YOLO model **Completed**

#### Phase 3:

- Move all programs onto raspberry Pi and test all equipment **Completed**
- Test equipment and program on the Pi **Completed**
- Develop a final program **Completed**
- Live tests with drone **Completed**
- 
--- 

### Current plan / Idea

### ML drone detection
- Use Drone RF or simular dataset to train an ML model to detect the presence of a drone based on RF signature
- Have HackRF sweep freqencies from 2.4Ghz to 2.5Ghz using the ML model to make predictions for drone detection 
- Once a detection is made swap the program to the IR camera for locating

### AI object tracking

- Use IR images of a drone to train a YOLO model to track the drone using bounding boxes
- Attach the camera to a servo which rotates the camera over a 180 degree range to try and find the drone
- Attach camera to pan tilt kit so the camera can folllow the drone as it moves. This idea might change based on field of view of camera and complexity of the tracking

--- 

### Progress

#### Drone RF capture:
- 500 RF signals captured from a 2.4GHz drone and 500 signals of bakground noise
- Program sweep scans the 2.4GHz range using WiFi channels drones use to communicate on
- Drones communicate on the 802.11 standard and use FHSS to hop between wifi channels, to capture the range I chose to scan all freqencies and extract the feautres.
- Feature extraction program integrated with sweep function, when running each channel is scanned, exported and features extarcted and saved to a CSV file
- Intial model training shows around 80% accuracy on Random Forest, Desicion Tree, KNN and SVM. Parameter tuning is underway<br>

#### ML outcomes:
- Training, tuned and evaluted models have the following scores:<br>
    **Random Forest accuracy: 0.9356**
    - Confusion Matrix Random Forest
    [91 5]
    [8 98]<br>
    **Decision Tree accuracy: 0.8911**
    - Confusion Matrix Decision Tree
    [85 11]
    [11 95]<br>
    **SVM accuracy: 0.9257**
    - Confusion Matrix SVM:
    [88 8]
    [7 99]<br>
    **KNN accruacy: 0.9356**
    - Confusion Matrix KNN
    [93 3]
    [10 96]
<br>

##### Most Accurate models: KNN / Random Forest



