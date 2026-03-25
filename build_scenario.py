import os
import subprocess

DIR = r"f:\Unconventional Intersection SUMO"
os.makedirs(DIR, exist_ok=True)
os.chdir(DIR)

# 1. net.nod.xml
nodes = """<nodes>
    <!-- Center Split Nodes for the 0.5m Island -->
    <node id="NE_corner" x="5.2" y="5.2" type="priority"/>
    <node id="SE_corner" x="5.2" y="-5.2" type="priority"/>
    <node id="SW_corner" x="-5.2" y="-5.2" type="priority"/>
    <node id="NW_corner" x="-5.2" y="5.2" type="priority"/>

    <node id="end_N" x="0" y="500" type="dead_end"/>
    <node id="end_S" x="0" y="-500" type="dead_end"/>
    <node id="end_E" x="500" y="0" type="dead_end"/>
    <node id="end_W" x="-500" y="0" type="dead_end"/>

    <!-- East U-turn Bulge Nodes -->
    <node id="E_out" x="150" y="9.95" type="priority"/>
    <node id="E_in" x="150" y="-9.95" type="priority"/>

    <!-- West U-turn Bulge Nodes -->
    <node id="W_out" x="-150" y="-9.95" type="priority"/>
    <node id="W_in" x="-150" y="9.95" type="priority"/>

    <!-- North U-turn Bulge Nodes -->
    <node id="N_out" x="-9.95" y="150" type="priority"/>
    <node id="N_in" x="9.95" y="150" type="priority"/>

    <!-- South U-turn Bulge Nodes -->
    <node id="S_out" x="9.95" y="-150" type="priority"/>
    <node id="S_in" x="-9.95" y="-150" type="priority"/>
</nodes>"""
with open("net.nod.xml", "w") as f: f.write(nodes)

# 2. net.edg.xml
# 3 lanes, 3.3m width
edges = """<edges>"""
directions = {
    'N': ('end_N', 'N_out', 'N_in', 'NE_corner', 'NW_corner', 
          '5.2,500 5.2,170 9.95,150', '9.95,150 5.2,130 5.2,5.2',
          '-5.2,5.2 -5.2,130 -9.95,150', '-9.95,150 -5.2,170 -5.2,500',
          '-9.95,150 -5,160 5,160 9.95,150'),
    'S': ('end_S', 'S_out', 'S_in', 'SW_corner', 'SE_corner', 
          '-5.2,-500 -5.2,-170 -9.95,-150', '-9.95,-150 -5.2,-130 -5.2,-5.2',
          '5.2,-5.2 5.2,-130 9.95,-150', '9.95,-150 5.2,-170 5.2,-500',
          '9.95,-150 5,-160 -5,-160 -9.95,-150'),
    'E': ('end_E', 'E_out', 'E_in', 'SE_corner', 'NE_corner', 
          '500,-5.2 170,-5.2 150,-9.95', '150,-9.95 130,-5.2 5.2,-5.2',
          '5.2,5.2 130,5.2 150,9.95', '150,9.95 170,5.2 500,5.2',
          '150,9.95 160,5 160,-5 150,-9.95'),
    'W': ('end_W', 'W_out', 'W_in', 'NW_corner', 'SW_corner', 
          '-500,5.2 -170,5.2 -150,9.95', '-150,9.95 -130,5.2 -5.2,5.2',
          '-5.2,-5.2 -130,-5.2 -150,-9.95', '-150,-9.95 -170,-5.2 -500,-5.2',
          '-150,-9.95 -160,-5 -160,5 -150,9.95')
}
for d, (e, out_node, in_node, c_in, c_out, shp_in1, shp_in2, shp_out1, shp_out2, shp_turn) in directions.items():
    # Inbound
    edges += f'\n    <edge id="in_{d}_1" from="{e}" to="{in_node}" priority="2" numLanes="3" width="3.3" speed="33.33" shape="{shp_in1}" spreadType="center"/>'
    edges += f'\n    <edge id="in_{d}_2" from="{in_node}" to="{c_in}" priority="2" numLanes="3" width="3.3" speed="33.33" shape="{shp_in2}" spreadType="center"/>'
    # Outbound
    edges += f'\n    <edge id="out_{d}_1" from="{c_out}" to="{out_node}" priority="2" numLanes="3" width="3.3" speed="33.33" shape="{shp_out1}" spreadType="center"/>'
    edges += f'\n    <edge id="out_{d}_2" from="{out_node}" to="{e}" priority="2" numLanes="3" width="3.3" speed="33.33" shape="{shp_out2}" spreadType="center"/>'
    # Dedicated U-Turn Edge forming the 'Eye' curve, now 2 lanes!
    edges += f'\n    <edge id="turn_{d}" from="{out_node}" to="{in_node}" priority="2" numLanes="2" width="3.3" speed="4.17" shape="{shp_turn}" spreadType="center"/>'
edges += "\n</edges>"
with open("net.edg.xml", "w") as f: f.write(edges)

# 3. net.con.xml
cons = """<connections>"""
# Left turns at center in LHT:
# S -> W
# N -> E
# E -> S
# W -> N
left_turns = [
    ('in_S_2', 'out_W_1'),
    ('in_N_2', 'out_E_1'),
    ('in_E_2', 'out_S_1'),
    ('in_W_2', 'out_N_1'),
]
for frm, to in left_turns:
    for lane in range(3):
        cons += f'\n    <connection from="{frm}" to="{to}" fromLane="{lane}" toLane="{lane}" speed="8.33"/>'

for d in ['N', 'S', 'E', 'W']:
    # At d_in node
    # Merge straight traffic into Lane 0 to avoid bottleneck gaps
    cons += f'\n    <connection from="in_{d}_1" to="in_{d}_2" fromLane="0" toLane="0"/>'
    cons += f'\n    <connection from="in_{d}_1" to="in_{d}_2" fromLane="1" toLane="0"/>'
    cons += f'\n    <connection from="in_{d}_1" to="in_{d}_2" fromLane="2" toLane="0"/>'
    # Dedicated 2-lane U-turn dumps into Lanes 1 and 2
    cons += f'\n    <connection from="turn_{d}" to="in_{d}_2" fromLane="0" toLane="1"/>'
    cons += f'\n    <connection from="turn_{d}" to="in_{d}_2" fromLane="1" toLane="2"/>'
    
    # At d_out node
    cons += f'\n    <connection from="out_{d}_1" to="out_{d}_2" fromLane="0" toLane="0"/>'
    # Lanes 1 and 2 exclusively for the 2-lane U-turn!
    cons += f'\n    <connection from="out_{d}_1" to="turn_{d}" fromLane="1" toLane="0"/>'
    cons += f'\n    <connection from="out_{d}_1" to="turn_{d}" fromLane="2" toLane="1"/>'
cons += "\n</connections>"
with open("net.con.xml", "w") as f: f.write(cons)

# Call netconvert
cmd = [
    "netconvert",
    "--node-files", "net.nod.xml",
    "--edge-files", "net.edg.xml",
    "--connection-files", "net.con.xml",
    "--output-file", "net.net.xml",
    "--lefthand", "true",
    "--no-turnarounds", "true"
]
print("Running netconvert...")
subprocess.run(cmd, check=True)

# 4. demands.rou.xml
vtypes = """
    <vType id="bus" vClass="bus" length="12.0" maxSpeed="16.67" speedFactor="0.5" speedDev="0.0" guiShape="bus" lcStrategic="1.0" lcCooperative="1.0" lcSpeedGain="0.1" latAlignment="center" minGapLat="0.6"/>
    <vType id="car" vClass="passenger" length="4.5" maxSpeed="16.67" speedFactor="1.0" speedDev="0.0" guiShape="passenger" lcStrategic="2.0" lcCooperative="1.0" lcSpeedGain="0.1" latAlignment="center" minGapLat="0.6"/>
    <vType id="autorickshaw" vClass="passenger" length="2.5" maxSpeed="5.56" speedFactor="0.5" speedDev="0.0" guiShape="passenger/sedan" width="1.4" lcStrategic="0.1" lcCooperative="0.1" lcSpeedGain="3.0" lcAssertive="2.0" lcKeepRight="0.1" latAlignment="center" minGapLat="0.6"/>
    <vType id="motorcycle" vClass="motorcycle" length="2.2" width="0.8" maxSpeed="16.67" speedFactor="1.0" speedDev="0.0" guiShape="motorcycle" lcStrategic="2.0" lcCooperative="1.0" lcSpeedGain="0.1" latAlignment="compact" minGapLat="0.1" lcSublane="2.0"/>
    <vType id="truck" vClass="truck" length="10.0" maxSpeed="11.11" speedFactor="0.3333" speedDev="0.0" guiShape="truck" lcStrategic="2.0" lcCooperative="1.0" lcSpeedGain="0.1" latAlignment="center" minGapLat="0.6"/>
"""
veh_counts = {
    'bus': 30,
    'car': 200,
    'autorickshaw': 250,
    'motorcycle': 500,
    'truck': 10
}
flows = ""
origins = ['in_N_1', 'in_S_1', 'in_E_1', 'in_W_1']
dests = ['out_N_2', 'out_S_2', 'out_E_2', 'out_W_2']

for vtype, total_vol in veh_counts.items():
    flow_per_od = total_vol / 3.0
    for o in origins:
        for dest in dests:
            if o.split('_')[1] == dest.split('_')[1]: continue # skip U-turn to same origin
            flow_id = f"flow_{vtype}_{o}_{dest}"
            flows += f'    <flow id="{flow_id}" type="{vtype}" begin="0" end="3600" vehsPerHour="{flow_per_od}" from="{o}" to="{dest}"/>\n'

with open("demands.rou.xml", "w") as f:
    f.write(f'<routes>\\n{vtypes}\\n{flows}</routes>')

# Call duarouter
cmd_dua = [
    "duarouter",
    "--net-file", "net.net.xml",
    "--route-files", "demands.rou.xml",
    "--output-file", "routed.rou.xml",
    "--ignore-errors", "true",
    "--begin", "0", "--end", "3600"
]
print("Running duarouter...")
subprocess.run(cmd_dua, check=True)

# 5. simulation.sumocfg
cfg = """<configuration>
    <input>
        <net-file value="net.net.xml"/>
        <route-files value="routed.rou.xml"/>
    </input>
    <processing>
        <lateral-resolution value="0.8"/>
    </processing>
    <time>
        <begin value="0"/>
        <end value="3600"/>
    </time>
</configuration>"""
with open("simulation.sumocfg", "w") as f: f.write(cfg)
print("Done!")
