# Unconventional Intersection for Left-Hand Traffic (SUMO)

This project contains a procedural generator that builds and compiles a highly detailed, Unconventional Intersection customized for Bangladeshi Left-Hand Traffic (LHT) in Eclipse SUMO. 

## 1. Scenario Overview
The scenario avoids traditional signalized intersection queues by completely restricting direct crossing movements (straight and right turns). 
- **The Core Rule**: All vehicles reaching the main intersection must perform a continuous, unhindered Left Turn. If a vehicle's intended route is straight or right, they travel 150m down the next arm to perform a continuous median U-Turn and return to the main intersection.
- **Traffic Hourly Volumes (per approach)**: 
  - Motorcycles: 500
  - Autorickshaws: 250
  - Cars: 200
  - Buses: 30
  - Trucks: 10

## 2. Geometric Design & Queue Prevention
The grid arms are generated as dual carriageways separated by a strict physical median. Each direction consists of **3 lanes**, each **3.3m wide**.
- **0.5m Global Median & Central Island Barrier**: To conserve space, the opposing directional lanes maintain exactly a **0.5m central gap** throughout the entire network. At the very center of the main intersection, this rigid 0.5m spacing physically manifests as an impassable `0.5m x 0.5m` central grass footprint. This acts as a physical center barrier (the yellow mark) forcefully blocking all crossing/straight/right-turn movements!
- **Precision 5m Flared 2-Lane U-Turn Islands**: The U-Turn loops EXACTLY 150m down each arm are physically flared outwards starting at the 130m mark (exactly 20m prior). Over this 20m span, the 0.5m median gently flares out to exactly 10 meters at the turnaround, generating a precision **5m inner turning radius** while conserving pavement!
- **2-Lane U-Turn Capacity & Conflict-Free Flow**: As vehicles approach the 150m U-turn bulbs:
  - The innermost lanes (Lanes 1 & 2) seamlessly merge directly into a massive **2-Lane dedicated U-Turn curve**. This doubles U-turn throughput!
  - The outermost lane (Lane 0) is **dedicated exclusively to continuous straight traffic**.
  - This forces all straight-bound traffic to maintain the outer lane, entirely eliminating merging bottlenecks with the massive influx of 2-lane U-turning vehicles returning to the network.

## 3. Vehicle Speeds
Since SUMO enforces connection limits universally across all vehicles, this scenario employs a mathematical coupling of generic edge speeds combined with tightly bounded vehicle `speedFactor` and `maxSpeed` profiles to guarantee distinct speed targets (in km/h) tailored per vehicle class:

| Vehicle Type | Straight (km/h) | Intersection Turn (km/h) | U-Turn (km/h) |
|--------------|-----------------|--------------------------|---------------|
| **Car/Moto** | 60              | 30                       | 15            |
| **Truck**    | 40              | 10                       | 5             |
| **Bus**      | 60              | 15                       | ~7.5          |
| **Rickshaw** | 20              | 15                       | ~7.5          |

## 4. Advanced Driver Behaviors & Sublane Overtaking
To capture the exact dynamics of South Asian traffic, the SUMO **`Sublane Model`** is fully active, allowing vehicles to physically stack side-by-side within the 3.3m lanes. 
Custom `vType` definitions override the default `lc2013` lane-changing logic:
1. **Motorcycles (`latAlignment="compact"`)**: Assigned a physical width of 0.8m and ultra-tight margins (`minGapLat="0.1"`). They actively trigger the Sublane Model to compress to the side of the lanes, allowing them to intelligently filter past and overtake slow cars/trucks during congested U-turns.
2. **Autorickshaws (`lcSpeedGain="3.0", lcAssertive="2.0"`)**: Defined as fiercely aggressive drivers who prioritize lane-hopping to maintain speed, drastically reducing their strategic routing foresight.
3. **Buses, Cars, Trucks (`latAlignment="center"`)**: Remain rigidly aligned to the center of their respective lanes and act conservatively. They plan their lanes far in advance (`lcStrategic="2.0"`) and are reluctant to randomly overtake (`lcSpeedGain="0.1"`).

## 5. How to Build & Run
The entire network, connections, routes, and `vTypes` are generated procedurally by the python script.

1. Generate the network by running the python compiler script in this directory:
   ```bash
   python build_scenario.py
   ```
2. Open and play the simulation using the SUMO GUI:
   ```bash
   sumo-gui -c simulation.sumocfg
   ```
